# app.py
# Team 2: CSTU Chat GPT App
# Sushil Sharma, Fang Wang, Lam Dao
# 07/29 Added Fang's chnages, Aded sidebar for OPENAI key input
#  
import streamlit as st
import random
import time
import openai
import textwrap3 as textwrap

# For sending email
import json
import sendgrid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

st.title("Team2 CSTUChatgpt 💬")

#st.sidebar.image("robo.gif")

OPENAI_API_KEY = st.sidebar.text_input("Enter OpenAI key", type="password")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

SENDGRID_API_KEY = st.sidebar.text_input("Enter SendGrid API key", type="password")

if "chat_history" not in st.session_state:
   st.session_state.chat_history = []
     

# Initialize chat history
if "prompt_history" not in st.session_state:
        # Initialize the chat history with the system message if it doesn't exist
        st.session_state.prompt_history = [
            {'role': 'system', 'content': f"""
            You are a smart and friendly virtual assistant designed to enhance student engagement. Please start by greeting the student
            and offering assistance with registering for July and August courses with one sentence.

            If a student wishes to register for a different time period, kindly apologize and explain that registration
            is currently only open for July. If a student requires other functions besides registration, ask them to
            check other corresponding web pages.

            Begin by greeting the student and then proceed with the registration process by asking them choose courses from available course list.

            After collecting all registrations, summarize them and check if the student wishes to enroll in any additional courses. 
            After the student finish registrations, ask for his/her email address. If they provide email address, inform them that they will receive a confirmation email and send them a confirmation email about their course registrations.

            Please refer to the following available course list for the July and August and display a new line after each course when listing them:\n
            (1) UX/Product Design Instructor: Xinyu, Time Saturday morning 9:30-11:30;\n
            (2) AI and Reinforcement Learning, Instructor: YC,  Time: Monday night 19:30-21:00 and Saturday 15:10-17:10;\n
            (3) Data Visualization, Instuctor: George,  Time: Tuesday night 19:30-21:00 and Saturday 13:30 - 15:00;\n
            (4) CSTUGPT，Instructor: Michael,Time: Wednesday night 19:30-21:30;\n(5) Python, Insturctor: Glen, Time: Thursday night: 19:30-21:30;\n
            (6) Security (Seminor), Insturctor: Wickey Wang Time: Friday night 19:30-21:30\n
            """}
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
        functions = [
         {
            "name": "send_email",
            "description": "Send a confirmation email for user's course registration",
            "parameters": {
                "type": "object",
                "properties": {
                    "receiver_email": {"type": "string", "description": "The email of user",},
                    "body": {"type": "string", "description": "Confirmation content of CSTU about courses registered by student users",},
                },
                "required": ["receiver_email"],
            }
         }
        ],
       function_call="auto",
    )
    return response.choices[0]["message"]


def limit_line_width(text, max_line_width):
    """ Function to limit the line width of the text """
    if text is None: return ""
    lines = textwrap.wrap(text, width=max_line_width)
    return "\n".join(lines)

# Define a function sending confirmation email for registration
def send_email(receiver_email, body):
    message = Mail(
        from_email='cstu02@gmail.com',
        to_emails=receiver_email,
        subject='Course registration confirmation from CSTU',
        html_content=body)
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        #print(response.status_code)
        #print(response.body)
        #print(response.headers)
    except Exception as e:
            print(e.message)
    
# Display chat messages from history on app rerun
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if user_input := st.chat_input("Welcome to Team2 CSTUChatgpt! 🤖"):

    if OPENAI_API_KEY and SENDGRID_API_KEY:
        my_message = {"role": "user", "content": user_input}
        
        # Add user message to chat history
        st.session_state.chat_history.append(my_message)
        st.session_state.prompt_history.append(my_message)

        # Get the model response
        response = chat_complete_messages(st.session_state.prompt_history, temperature=0)
        #response = chat_complete_messages(C, temperature=0)
        # Limit the line width to, for example, 40 characters
        max_line_width = 60
        
        if response.get("function_call"): # Sending email 
            function_args = json.loads(response["function_call"]["arguments"])
            send_email(function_args.get("receiver_email"), function_args.get("body")) 
            formatted_text = "Thank you for providing your email address. A confirmation message for your registration has been sent to your email. Please check it and let me known if there is any further requirement."
            #st.info("The following message has been sent to "+function_args.get("receiver_email")+":\n"+function_args.get("body"))
        else: 
            formatted_text = limit_line_width(response["content"], max_line_width)
        
        ai_message = {"role": "assistant", "content": formatted_text}
        st.session_state.chat_history.append(ai_message)
        st.session_state.prompt_history.append(ai_message)

        # Display message in chat message container
        with st.chat_message("user"):
            st.write(my_message['content'])
        with st.chat_message("assistant"):
            st.write(ai_message['content'])

    else:
        st.write("!!! Error: Empty OPENAI_API_KEY or SENDGRID_API_KEY!!!")
    
