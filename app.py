import streamlit as st
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

def main():
    st.title("Interactive Story Generator")

    if 'story_state' not in st.session_state:
        st.session_state.story_state = {}
        initialize_story()

    if 'current_story' not in st.session_state:
        st.session_state.current_story = False

    if st.session_state.current_story:
        display_current_state()
        handle_user_input()
    else:
        display_genre_options()

def initialize_story():
    # Initialize story state to track prompts and user choices
    st.session_state.story_state['current_prompt'] = None
    st.session_state.story_state['story_text'] = ""
    st.session_state.story_state['choices'] = []
    st.session_state.story_state['history'] = []

def display_genre_options():
    # Ask Gemini to generate 4 random genres with descriptions
    prompt = """
    Generate 4 random story genres (e.g., Mystery, Fantasy, Sci-Fi, Romance) with a brief description for each. 
    Format the response as a dictionary with genre names as keys and their descriptions as values. 
    Example response format:
    {
        "Mystery": "A gripping detective story.",
        "Fantasy": "An epic adventure in a magical world.",
        "Sci-Fi": "A futuristic space adventure.",
        "Romance": "A heartfelt love story."
    }
    Please provide only the dictionary in the response without any additional code or explanation.
    """
    response = model.generate_content(prompt)

    try:
        # Attempt to parse the response as JSON
        genre_options = json.loads(response.text)  # Parse the JSON response

        if isinstance(genre_options, dict):
            # Display genre options to the user
            genre_choice = st.radio("Choose a genre for your story:", list(genre_options.keys()))
            st.write(f"Description: {genre_options[genre_choice]}")

            if st.button("Submit"):
                # Start the story based on the user's genre selection
                st.session_state.story_state['current_prompt'] = genre_choice
                st.session_state.story_state['story_text'] = genre_options[genre_choice]
                st.session_state.story_state['history'] = [st.session_state.story_state['story_text']]
                st.session_state.current_story = True
                generate_next_choices(st.session_state.story_state['story_text'])

            if st.button("Refresh"):
                st.session_state.current_story = False
                st.session_state.story_state = {}

        else:
            raise ValueError("Unexpected format for genre options")

    except json.JSONDecodeError as e:
        st.error(f"Error parsing genre options: {e}")
        st.write(f"Response from Gemini: {response.text}")
    except Exception as e:
        st.error(f"Error generating genre options: {e}")
        st.write(f"Response from Gemini: {response.text}")

def display_current_state():
    # Display the current story text
    if st.session_state.story_state['story_text']:
        st.write(st.session_state.story_state['story_text'])
    
    if st.session_state.story_state['choices']:
        for choice in st.session_state.story_state['choices']:
            if st.button(choice):
                handle_choice(choice)

def handle_user_input():
    if not st.session_state.story_state['current_prompt']:
        prompt_selection = st.selectbox("Choose a story prompt:", list(st.session_state.story_state['prompts'].keys()))
        if st.button("Start Story"):
            st.session_state.story_state['current_prompt'] = prompt_selection
            st.session_state.story_state['story_text'] = st.session_state.story_state['prompts'][prompt_selection]
            st.session_state.story_state['history'].append(st.session_state.story_state['story_text'])
            generate_next_choices(st.session_state.story_state['story_text'])

def handle_choice(choice):
    # Add user choice to the story history and generate next text
    st.session_state.story_state['history'].append(choice)
    st.session_state.story_state['story_text'] += "\n" + choice
    generate_next_text(choice)

def generate_next_choices(text):
    # Request Gemini to generate the next set of choices based on the current story
    prompt = f"Given the following story text: '{text}', generate 4 distinct choices the user could make to continue the story. Return them as a python list of strings."
    response = model.generate_content(prompt)
    try:
        choices = json.loads(response.text)  # Parse the JSON response
        st.session_state.story_state['choices'] = choices
    except json.JSONDecodeError:
        st.session_state.story_state['choices'] = ["Continue the story in a new direction."]

def generate_next_text(choice):
    # Generate the next part of the story based on the user's choice
    prompt = f"Continue the following story based on the user's choice: '{st.session_state.story_state['story_text']}'. The user chose: '{choice}'. Provide the next part of the story."
    response = model.generate_content(prompt)
    st.session_state.story_state['story_text'] += "\n" + response.text
    st.session_state.story_state['history'].append(response.text)
    generate_next_choices(st.session_state.story_state['story_text'])

if __name__ == "__main__":
    main()
