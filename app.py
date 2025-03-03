​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Google Generative AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')  # Verify this model name in the docs

# Function to call the API safely
def call_api(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"API call failed: {e}")
        return None

# Initialize story state
def initialize_story():
    st.session_state.story_state = {
        'current_prompt': None,
        'story_text': "",
        'choices': [],
        'history': []
    }

# Display genre options
def display_genre_options():
    prompt = (
        "Generate 4 random story genres (e.g., Mystery, Fantasy, Sci-Fi, Romance) with a brief description for each. "
        "Format the response as:\n"
        "1. Genre: [genre name] - [description]\n"
        "2. Genre: [genre name] - [description]\n"
        "3. Genre: [genre name] - [description]\n"
        "4. Genre: [genre name] - [description]"
    )
    response = call_api(prompt)
    if not response:
        st.error("Failed to fetch genres. Try again!")
        return

    # Parse the response into a list of (genre, description) tuples
    genre_lines = [line.strip() for line in response.split("\n") if line.strip()]
    genres = []
    for line in genre_lines:
        try:
            genre_part = line.split(" - ", 1)
            genre = genre_part[0].replace("Genre:", "").strip()
            desc = genre_part[1].strip()
            genres.append((genre, desc))
        except IndexError:
            st.warning(f"Skipping malformed genre line: {line}")

    # Display options
    st.subheader("Choose Your Story Genre")
    genre_choice = st.radio("Pick a genre to begin:", [f"{g} - {d}" for g, d in genres], key="genre_select")
    if st.button("Start Story"):
        selected_genre = genre_choice.split(" - ")[0]
        start_story(selected_genre)

# Start the story with the chosen genre
def start_story(genre):
    prompt = (
        f"Begin an interactive story in the {genre} genre. Write a short opening paragraph (3-5 sentences) "
        f"and provide 3 distinct choices for the next step. Format the response as:\n"
        f"Story: [opening text]\n\nChoices:\n1. [choice 1]\n2. [choice 2]\n3. [choice 3]"
    )
    response = call_api(prompt)
    if response:
        story, choices = parse_response(response)
        if story and choices:
            st.session_state.story_state['story_text'] = story
            st.session_state.story_state['choices'] = choices
            st.session_state.story_state['history'].append({"segment": story, "choice": None})

# Parse API response
def parse_response(response_text):
    if not response_text:
        return None, None
    try:
        story_start = response_text.index("Story:") + len("Story:")
        choices_start = response_text.index("Choices:")
        story = response_text[story_start:choices_start].strip()
        choices_text = response_text[choices_start + len("Choices:"):].strip()
        choices = [c.strip() for c in choices_text.split("\n") if c.strip()]
        return story, choices
    except ValueError:
        st.error("Invalid response format from API.")
        return None, None

# Display current story state
def display_current_state():
    st.markdown(f"### Your Story")
    st.write(st.session_state.story_state['story_text'])
    if st.session_state.story_state['choices']:
        st.subheader("What Happens Next?")
        choice = st.radio("Choose your path:", st.session_state.story_state['choices'], key="choice_select")
        if st.button("Continue"):
            handle_user_input(choice)

# Handle user input and continue the story
def handle_user_input(choice):
    prompt = (
        f"Continue this story: '{st.session_state.story_state['story_text']}'\n"
        f"The user chose: '{choice}'.\n"
        f"Write the next paragraph (3-5 sentences) and provide 3 new distinct choices. "
        f"Format the response as:\nStory: [next text]\n\nChoices:\n1. [choice 1]\n2. [choice 2]\n3. [choice 3]"
    )
    response = call_api(prompt)
    if response:
        new_segment, new_choices = parse_response(response)
        if new_segment and new_choices:
            st.session_state.story_state['story_text'] += "\n\n" + new_segment
            st.session_state.story_state['choices'] = new_choices
            st.session_state.story_state['history'].append({"segment": new_segment, "choice": choice})

# Main function
def main():
    st.title("Interactive Story Generator")
    st.markdown("Craft your own adventure, one choice at a time!")

    if 'story_state' not in st.session_state:
        initialize_story()

    if not st.session_state.story_state['story_text']:
        display_genre_options()
    else:
        display_current_state()

if __name__ == "__main__":
    main()
​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​​
