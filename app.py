import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

def main():
    st.title("Interactive Story Generator")

    if 'story_state' not in st.session_state:
        st.session_state.story_state = {}
        initialize_story()

    # If the story has not started, ask the user to choose a genre
    if 'current_story' not in st.session_state or not st.session_state.current_story:
        display_genre_options()
    else:
        display_current_state()
        handle_user_input()

def initialize_story():
    st.session_state.story_state['current_prompt'] = None
    st.session_state.story_state['story_text'] = ""
    st.session_state.story_state['choices'] = []
    st.session_state.story_state['history'] = []

def display_genre_options():
    # Ask Gemini to generate 4 random genres with descriptions
    prompt = "Generate 4 random story genres (e.g., Mystery, Fantasy, Sci-Fi, Romance) with a brief description for each."
    response = model.generate_content(prompt)
    genre_options = eval(response.text)  # Convert Gemini's response to a list of genre-description pairs

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

def display_current_state():
    # Display the current story text
    st.write(st.session_state.story_state['story_text'])
    
    if st.session_state.story_state['choices']:
        for choice in st.session_state.story_state['choices']:
            if st.button(choice):
                handle_choice(choice)

    if st.button("End Story"):
        generate_ending()

def handle_user_input():
    pass  # User input is handled dynamically by the buttons (choices)

def handle_choice(choice):
    st.session_state.story_state['history'].append(choice)
    st.session_state.story_state['story_text'] += "\n" + choice
    generate_next_text(choice)

def generate_next_choices(text):
    # Ask Gemini to generate 4 random choices based on the current story text
    prompt = f"Given the following story text: '{text}', generate 4 distinct choices the user could make to continue the story. Return them as a Python list of strings."
    response = model.generate_content(prompt)

    try:
        choices = eval(response.text)  # Parse Gemini's response into a list of choices
        st.session_state.story_state['choices'] = choices
    except:
        st.session_state.story_state['choices'] = ["Continue the story in a new direction."]

def generate_next_text(choice):
    # Ask Gemini to generate the next part of the story based on the user's choice
    prompt = f"Continue the following story based on the user's choice: '{st.session_state.story_state['story_text']}'. The user chose: '{choice}'. Provide the next part of the story."
    response = model.generate_content(prompt)
    st.session_state.story_state['story_text'] += "\n" + response.text
    st.session_state.story_state['history'].append(response.text)
    generate_next_choices(st.session_state.story_state['story_text'])

def generate_ending():
    # Ask Gemini to generate a fitting ending to the story
    prompt = f"Finish the following story: '{st.session_state.story_state['story_text']}'. Provide a satisfying and conclusive ending."
    response = model.generate_content(prompt)
    st.session_state.story_state['story_text'] += "\n" + response.text
    st.session_state.story_state['history'].append(response.text)
    st.write("The story has ended.")

if __name__ == "__main__":
    main()
