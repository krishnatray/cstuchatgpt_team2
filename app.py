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
import dotenv
from dotenv import load_dotenv
import os
import pinecone
import os
import csv

# For sending email
import json
import sendgrid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

st.title("Team2 CSTUChatgpt 💬")
#st.sidebar.image("robo.gif")

OPENAI_API_KEY = st.sidebar.text_input("Enter OpenAI key", type="password")
if OPENAI_API_KEY: openai.api_key = OPENAI_API_KEY

#dotenv_path = '.env'  # Specify the path to the .env file
env = load_dotenv() # Copy .env file to the same directory before running
if not env: st.error("Enviroment file error. Please check .env file in your directory.")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

embed_model = "text-embedding-ada-002"
index_name = 'cstugpt-kb'
pinecone.init( # initialize connection to pinecone
    api_key=PINECONE_API_KEY,
    environment="us-west1-gcp-free")
index = pinecone.Index(index_name) # connect to pinecone index

if "chat_history" not in st.session_state: 
    st.session_state.chat_history = []    

# Initialize chat history
delimiter = "####"
if "prompt_history" not in st.session_state: # Initialize the chat history with the system message if it doesn't exist
        st.session_state.prompt_history = [
            {'role': 'system', 'content': f"""\
            You are a smart and friendly virtual assistant designed as a chat agent to answer concisely questions about California Science and Technology University.\
            After greeting, ask for user's name and use it in an appropriate way. During the coversation, use the chat history information if needed and answer their questions\ 
            based on the following knowledge base within the given context delimited by {delimiter}.\
            If users require information about CSTU out of knowledge base, ask them to check the web site www.cstu.edu.\
            If users ask for course registration, assist them to choose current available courses from the list. When listing the courses, you should add a line break after each course line.\
            After collecting courses, summarize them and check if users wish to enroll in any additional course or make confirmation with selected courses.\        
            If it's completed, ask for their email address. If they provide email address, send them a confirmation email about their course registrations\
            """} ]

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
            "name": "send_email_save",
            "description": "Send a confirmation email for user's course registration and save user's registration information",
            "parameters": {
                "type": "object",
                "properties": {
                    "receiver_email": {"type": "string", "description": "The email of user",},
                    "body": {"type": "string", "description": "Confirmation content of CSTU about courses registered by student users",},
                    "courses":{"type":"string", "description":"The courses the user want to register",},
                    "name": {"type":"string","description":"The name of the user",},
                },
                "required": ["receiver_email", "courses","name","body"],
            }
         },
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
def send_email_save(receiver_email, body,courses,name):
# def send_email(receiver_email, body):

    csv_file = "registration_records.csv"
    print(receiver_email,body,name, courses)
    data = [time.strftime("%Y-%m-%d %H:%M:%S"), name, receiver_email, courses]
    if not os.path.exists(csv_file):
        with open(csv_file, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp","student name", "Email", "Courses"])

    with open(csv_file, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(data)

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
            st.info("A registration confirmation message has been sent to your email.")
    
# Display chat messages from history on app rerun
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
# Accept user input
if user_input := st.chat_input("Welcome to Team2 CSTUChatgpt! 🤖"):
    if OPENAI_API_KEY:
        res = openai.Embedding.create(
            input=[user_input],
            engine=embed_model
            )
        kb_res = index.query(res['data'][0]['embedding'], top_k=5, include_metadata=True, namespace='cstu')
        #If the include_metadata parameter is set to True, the query method will only return the id, score, and metadata for each document. The vector for each document will not be returned
        metadata_text_list = [x['metadata']['text'] for x in kb_res['matches']]
        limit = 3600  #set the limit of knowledge base words
        kb_content = " "
        count = 0
        proceed = True
        while proceed and count < len(metadata_text_list):  # append until hitting limit
            if len(kb_content) + len(metadata_text_list[count]) >= limit:
                proceed = False
            else:
                    kb_content += metadata_text_list[count]
            count += 1
        knowledge_message = {"role": "system", "content": f"""
                             {delimiter}{kb_content}{delimiter}
                             """}
       
        # Add user message to chat history
        user_message = {"role": "user", "content": user_input}
        st.session_state.chat_history.append(user_message)
        
        # Add knowledge base and user message to promt history      
        st.session_state.prompt_history.append(knowledge_message)        
        st.session_state.prompt_history.append(user_message)

        # Get the model response
        response = chat_complete_messages(st.session_state.prompt_history, temperature=0)
        #response = chat_complete_messages(C, temperature=0)
        # Limit the line width to, for example, 60 characters
        max_line_width = 60
        #x = response

        if response.get("function_call"): # Sending email

            function_args = json.loads(response["function_call"]["arguments"])
            send_email_save(function_args.get("receiver_email"), function_args.get("body"), function_args.get("courses"),function_args.get("name"))
            formatted_text = "Thank you for providing your email address. A confirmation message for your registration has been sent to your email. Please check it and let me known if there is any further requirement."
            #st.info("The following message has been sent to "+function_args.get("receiver_email")+":\n"+function_args.get("body"))
        else:
            formatted_text = limit_line_width(response["content"], max_line_width)

        ai_message = {"role": "assistant", "content": formatted_text}
        st.session_state.chat_history.append(ai_message)
        st.session_state.prompt_history.append(ai_message)

        # Display message in chat message container
        with st.chat_message("user"):
            st.write(user_message['content'])
        with st.chat_message("assistant"):
            st.write(ai_message['content'])

    else:
        st.write("!!! Error: You need to enter OPENAI_API_KEY!")
    
