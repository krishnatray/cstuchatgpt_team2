import streamlit as st
import os
from dotenv import load_dotenv
import openai
import json

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load JSON data
json_data = json.loads(open("data.json", "r").read())  # Replace "your_json_file.json" with the actual file path

# Generating responses from the GPT-3 API
def generate_response(prompt):
    for conversation in json_data["conversations"]:
        if prompt.lower() == conversation["user"].lower():
            # If the user's input matches any of the user questions in the JSON data,
            # use the corresponding bot response as the initial context for GPT-3.
            initial_context = conversation["bot"]
            break
    else:
        # If no match found in JSON data, use an empty string as initial context.
        initial_context = ""

    completions = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"{initial_context}\nUser: {prompt}\nBot:",
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.5
    )
    messages = completions.choices[0].text
    return messages

# Chatbot interface
def main():
    st.title("Chatbot Interface")
    st.write("Welcome to cstuGPT")

    # Input for user prompt
    user_input = st.text_input("You: ")

    if st.button("Submit"):
        if user_input:
            # Generate response using the GPT model with potential context from JSON data
            gpt3_response = generate_response(user_input)

            # Display the response
            st.text_area("Chatbot:", value=gpt3_response, height=200)

if __name__ == "__main__":
    main()
