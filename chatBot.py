import streamlit as st
import os
from dotenv import load_dotenv
import openai
import json

dotenv_path = '.env'  #modify and  change to your correct path!
load_dotenv(dotenv_path)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load JSON data
json_data = json.loads(open("data.json", "r").read())  # Replace "your_json_file.json" with the actual file path
context = json_data["system guide"].copy()

# Generating responses from the GPT-3.5 API
def generate_response(prompt):
  global context
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",  
    messages=context+[{"role":"user", "content":prompt}],
    temperature=0,
    max_tokens=150)
  answer = response.choices[0]["message"]["content"]
  context = context + [{"role":"assistant", "content": answer}]
  return answer

# Chatbot interface
def main():
    st.title("Chatbot Interface")
    st.write("Welcome to cstuGPT")

    # Initialize the chat history on the first run
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("You:", key="user_input", value="", placeholder="Type your question here")

    if st.button("Submit"):
        if user_input.strip():
            # Clean the user input by removing leading and trailing spaces
            cleaned_input = user_input.strip()

            # Generate response using the GPT model with potential context from JSON data
            gpt3_response = generate_response(cleaned_input)

            # Save the user input and chatbot response to chat history
            st.session_state.chat_history.append(("You", cleaned_input))
            st.session_state.chat_history.append(("Chatbot", gpt3_response))

            # Empty the input field after submitting using a JavaScript workaround
            st.markdown("<script>document.getElementById('user_input').value = '';</script>", unsafe_allow_html=True)



    # Display the chat history
    st.write("Chat History:")
    for sender, message in st.session_state.chat_history:
        st.text(f"{sender}: {message}")
if __name__ == "__main__":
    main()