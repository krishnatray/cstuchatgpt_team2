import streamlit as st
import os
from dotenv import load_dotenv
import openai
import textwrap

dotenv_path = '../.env'  # modify and change to your correct path!
load_dotenv(dotenv_path)
openai.api_key = os.getenv("OPENAI_API_KEY")

def chat_complete_messages(messages, temperature=0):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        temperature=temperature, # this is the degree of randomness of the model's output
    )
    return response.choices[0]["message"]["content"]
# Function to limit the line width of the text
def limit_line_width(text, max_line_width):
    lines = textwrap.wrap(text, width=max_line_width)
    return "\n".join(lines)

# Chatbot interface
def main():
    st.title("Chatbot Interface")
    st.write("Welcome to cstuGPT")
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

    user_input = st.text_input("User Message:", key="user_input", value="", placeholder="Type your question here")

    if st.button("Submit"):
        if user_input.strip() != "":
            my_message = {"role": "user", "content": user_input}
            st.session_state.chat_history.append(my_message)

            # Get the model response
            response = chat_complete_messages(st.session_state.chat_history, temperature=0)
            # Limit the line width to, for example, 40 characters
            max_line_width = 60
            formatted_text = limit_line_width(response, max_line_width)
            ai_message = {"role": "assistant", "content": formatted_text}
            st.session_state.chat_history.append(ai_message)
            # Display the chat history for Assistant and User only
        for idx, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user" or message["role"] == "assistant":
                st.text(f"{message['role']}: {message['content']}")



if __name__ == "__main__":
    main()
