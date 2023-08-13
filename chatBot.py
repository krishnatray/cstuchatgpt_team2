import streamlit as st
st.set_page_config(layout="wide")
import os
from dotenv import load_dotenv
import openai
import textwrap

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
    st.title("Welcome to CSTU Chat GPT")
    st.write("This is the chat box interface designed by team 2. Please enter your question into the box below and then press the Submit button")

    # Initialize the chat history on the first run
    if "chat_history" not in st.session_state:
        # Initialize the chat history with the system message if it doesn't exist
        st.session_state.chat_history = [
            {'role': 'system', 'content': f"""
            You are a smart and friendly virtual assistant designed to enhance student engagement. Please start by greeting the student
            and offering assistance with registering for July courses with one sentence.

            If a student wishes to register for a different time period, kindly apologize and explain that registration
            is currently only open for July. If a student requires other functions besides registration, ask them to
            check other corresponding web pages.

            Begin by greeting the student and then proceed with the registration process for the July course selection.
            Ask for email, inform them that they will receive a confirmation email upon completion.

            After collecting all registrations, summarize them and check if the student wishes to enroll in any additional courses.

            Please review the following course list and respond in a short, conversational, and friendly manner.
            The course includes:
            - UX/Product Design Instructor: Xinyu, Time Saturday morning 9:30-11:30
            - AI and Reinforcement Learning, Instructor: YC,  Time: Monday night 19:30-21:00 and Saturday 15:10-17:10
            - Data Visualization, Instuctor: George,  Time: Tuesday night 19:30-21:00 and Saturday 13:30 - 15:00
            - CSTUGPT， Instructor: Michael, Time: Wednesday night 19:30-21:30
            - Python,  Insturctor: Glen, Time: Thursday night: 19:30-21:30
            - Security (Seminor), Insturctor: Wickey Wang Time: Friday night 19:30-21:30
            """},
        ]

    user_input = st.text_area("Your question:", key="user_input", value="", placeholder="Type your question here", height=None)

    if st.button("Submit"):
        if user_input.strip() != "":
            my_message = {"role": "user", "content": user_input}
            st.session_state.chat_history.append(my_message)

            # Generate response using the GPT model with potential context from JSON data
            gpt3_response = generate_response(cleaned_input)

            # Save the user input and chatbot response to chat history
            st.session_state.chat_history.append(("User", cleaned_input))
            st.session_state.chat_history.append(("Assistant", gpt3_response))

            # Empty the input field after submitting using a JavaScript workaround
            st.markdown("<script>document.getElementById('user_input').value = '';</script>", unsafe_allow_html=True)

    # Display the chat history
    st.write("Conversation content:")
    for sender, message in st.session_state.chat_history:
        st.text(f"{sender}: {message}")


if __name__ == "__main__":
    main()
