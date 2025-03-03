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

    display_current_state()
    handle_user_input()

def initialize_story():
    # Initialize story prompts and starting points
    st.session_state.story_state['prompts'] = {
        "Mystery": "You wake up in a dimly lit room with no memory of how you got there. A single note lies on the table.",
        "Fantasy": "You are a young wizard's apprentice, tasked with retrieving a lost artifact from a forbidden forest.",
        "Sci-Fi": "A distress signal echoes through your spaceship. You are the only one awake.",
        "Romance": "You meet a stranger in a coffee shop, and there's an instant connection."
    }
    st.session_state.story_state['current_prompt'] = None
    st.session_state.story_state['story_text'] = ""
    st.session_state.story_state['choices'] = []
    st.session_state.story_state['history'] = []

def display_current_state():
    if st.session_state.story_state['current_prompt']:
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
    st.session_state.story_state['history'].append(choice)
    st.session_state.story_state['story_text'] += "\n" + choice
    generate_next_text(choice)

def generate_next_choices(text):
    prompt = f"Given the following story text: '{text}', generate 2-3 short, distinct choices the user could make to continue the story. Return them as a python list of strings."
    response = model.generate_content(prompt)
    try:
        choices = eval(response.text)
        st.session_state.story_state['choices'] = choices
    except:
        st.session_state.story_state['choices'] = ["Continue the story in a new direction."]

def generate_next_text(choice):
    prompt = f"Continue the following story based on the user's choice: '{st.session_state.story_state['story_text']}'. The user chose: '{choice}'. Provide the next part of the story."
    response = model.generate_content(prompt)
    st.session_state.story_state['story_text'] += "\n" + response.text
    st.session_state.story_state['history'].append(response.text)
    generate_next_choices(st.session_state.story_state['story_text'])

if __name__ == "__main__":
    main()
