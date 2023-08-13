# app.py
# Team 2: CSTU Chat GPT App
# Sushil Sharma, Fang Wang
# 07/29 Added Fang's chnages, Aded sidebar for OPENAI key input
#  

import streamlit as st
import random
import time
import openai
import textwrap3 as textwrap

st.title("Team2 CSTUChatgpt 💬")

st.sidebar.image("robo.gif")

OPENAI_API_KEY = st.sidebar.text_input("Enter openai key", type="password")

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

if "chat_history" not in st.session_state:
   st.session_state.chat_history = []
     

# Initialize chat history
if "prompt_history" not in st.session_state:
        # Initialize the chat history with the system message if it doesn't exist
        st.session_state.prompt_history = [
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

def chat_complete_messages(messages, temperature=0):
    """  Utility function to call chatgpt api chat completion 
         function with temparature = 0 as default 
         and returns the api response 
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        temperature=temperature, # this is the degree of randomness of the model's output
    )
    return response.choices[0]["message"]["content"]


def limit_line_width(text, max_line_width):
    """ Function to limit the line width of the text """
    lines = textwrap.wrap(text, width=max_line_width)
    return "\n".join(lines)


# Display chat messages from history on app rerun
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if user_input := st.chat_input("Welcome to Team2 CSTUChatgpt! 🤖"):

    if OPENAI_API_KEY:
        my_message = {"role": "user", "content": user_input}
        
        # Add user message to chat history
        st.session_state.chat_history.append(my_message)
        st.session_state.prompt_history.append(my_message)

        # Get the model response
        response = chat_complete_messages(st.session_state.prompt_history, temperature=0)
        # Limit the line width to, for example, 40 characters
        max_line_width = 60
        formatted_text = limit_line_width(response, max_line_width)
        ai_message = {"role": "assistant", "content": formatted_text}
        st.session_state.chat_history.append(ai_message)
        st.session_state.prompt_history.append(ai_message)

        # Display user message in chat message container
        with st.chat_message("user"): 
            # st.markdown(my_message['content'])
            # st.markdown(ai_message['content'])
            st.write(my_message['content'])
            st.write(ai_message['content'])
    else:
        st.write("!!! Error empty OPENAI_API_KEY !!!")
    
