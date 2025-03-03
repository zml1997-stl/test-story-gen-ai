import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import random

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')

def main():
    st.title("Interactive Story Generator")

    if 'story_state' not in st.session_state:
        st.session_state.story_state = {}
        initialize_story()

    display_current_state()
    handle_user_input()

def initialize_story():
    # Randomly generate the story prompt
    genres = ["Mystery", "Fantasy", "Sci-Fi", "Romance"]
    random_genre = random.choice(genres)
    st.session_state.story_state['current_prompt'] = random_genre

    # AI-generated starting prompt based on the genre
    prompt = f"Generate a brief starting scene for a {random_genre} story."
    response = model.generate_content(prompt)
    st.session_state.story_state['story_text'] = response.text
    st.session_state.story_state['history'] = [response.text]
    st.session_state.story_state['choices'] = []
    
    generate_next_choices(st.session_state.story_state['story_text'])

def display_current_state():
    if st.session_state.story_state['current_prompt']:
        st.write(st.session_state.story_state['story_text'])
        if st.session_state.story_state['choices']:
            for choice in st.session_state.story_state['choices']:
                if st.button(choice):
                    handle_choice(choice)

def handle_user_input():
    if not st.session_state.story_state['current_prompt']:
        st.write("Loading a random story prompt...")
        st.session_state.story_state['current_prompt'] = "Starting..."
        generate_next_choices(st.session_state.story_state['story_text'])

def handle_choice(choice):
    st.session_state.story_state['history'].append(choice)
    st.session_state.story_state['story_text'] += "\n" + choice
    generate_next_text(choice)

def generate_next_choices(text):
    # Randomly generate 2-3 choices based on the current story text
    prompt = f"Given the following story text: '{text}', generate 2-3 random, distinct choices the user could make to continue the story. Return them as a python list of strings."
    response = model.generate_content(prompt)
    try:
        choices = eval(response.text)
        st.session_state.story_state['choices'] = choices
    except:
        st.session_state.story_state['choices'] = ["Continue the story in a new direction."]

def generate_next_text(choice):
    # Continue the story based on the user's choice
    prompt = f"Continue the following story based on the user's choice: '{st.session_state.story_state['story_text']}'. The user chose: '{choice}'. Provide the next part of the story."
    response = model.generate_content(prompt)
    st.session_state.story_state['story_text'] += "\n" + response.text
    st.session_state.story_state['history'].append(response.text)
    generate_next_choices(st.session_state.story_state['story_text'])

if __name__ == "__main__":
    main()
