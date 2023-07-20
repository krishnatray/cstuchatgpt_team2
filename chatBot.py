import streamlit as st
from streamlit_chat import message

st.title('🎈 cstuGPT')

st.write('Welcome to cstuGPT')

import os
from dotenv import load_dotenv

import openai
import json

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
#st.write(openai.api_key)  #check your api_key

# Generating responses from the api
prompt = "hello"
def generate_response(prompt):
    completions = openai.Completion.create(
        engine = "text-davinci-002",
        prompt = prompt,
        max_tokens = 5,
        n=1,
        stop=None,
        temperature=0.5
    )
    messages = completions.choices[0].text
    return messages
#st.write(generate_response(prompt))

# create an chatbot interfaces
def main():
    st.title("Chatbot Interface")

    # Input for user prompt
    user_input = st.text_input("You: ")

    if st.button("Submit"):
        if user_input:
            # Generate response using your model
            response = generate_response(user_input)

            # Display the response
            st.text_area("Chatbot:", value=response, height=200)

if __name__ == "__main__":
    main()
