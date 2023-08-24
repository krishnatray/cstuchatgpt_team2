# app.py
# Team 2: CSTU Chat GPT App
# Sushil Sharma, Fang Wang, Lam Dao
# 07/29 Added Fang's chnages, Aded sidebar for OPENAI key input
#
import streamlit as st
import pandas as pd
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

st.title("Welcome to AdminGPT 💬")
#st.sidebar.image("robo.gif")


#dotenv_path = '.env'  # Specify the path to the .env file
env = load_dotenv() # Copy .env file to the same directory before running

if env: 
    # st.error("Enviroment file error. Please check .env file in your directory.")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    openai.api_key = OPENAI_API_KEY
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
else:
    OPENAI_API_KEY = st.sidebar.text_input("Enter OpenAI key", type="password")
    openai.api_key = OPENAI_API_KEY
    try:
        # OPENAI_API_KEY = st.secrets.OPENAI_API_KEY
        PINECONE_API_KEY = st.secrets.PINECONE_API_KEY
        SENDGRID_API_KEY = st.secrets.SENDGRID_API_KEY
    except Exception as e:
        st.error("Enviroment file error!")
        st.error(e)


embed_model = "text-embedding-ada-002"
index_name = 'cstugpt-kb'
pinecone.init( # initialize connection to pinecone
    api_key=PINECONE_API_KEY,
    environment="us-west1-gcp-free")
index = pinecone.Index(index_name) # connect to pinecone index

if "chat_history" not in st.session_state: 
    st.session_state.chat_history = []    

# Initialize chat history
delimiter = ""
if "prompt_history" not in st.session_state: # Initialize the chat history with the system message if it doesn't exist
        st.session_state.prompt_history = [
            {'role': 'system', 'content': f"""\
You are a chat agent providing concise answers to questions to California Science and Technology University (CSTU) admins based on contents provided at system role.\
At begining, welcome Admin users to CSTU. 
If admin user wants to see the registered students for a course, ask for the course name and call function get_registration with course name and display the results.
If admin user wants to the registered students for all courses, call function get_registration_all without any parameters and display the results.

                                                   """} ]
# During the coversation, refer to chat history and the information delimited by {delimiter}.
def chat_complete_messages(messages, temperature=0):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        temperature=temperature, # this is the degree of randomness of the model's output
        functions = [
        {
            "name": "get_registration",
            "description": "To reconfirm registration, get the student's registration details",
            "parameters": {
                "type": "object",
                "properties": {
                    "course_name": {"type": "string", "description": "Course Name",}
                },
                "required": ["course_name"],
            }
         },
         {
            "name": "get_registration_all",
            "description": "To reconfirm registration, get the student's registration details",
             "parameters": {"type": "object",
                "properties": {}
             }
         },
        
        # {
        #     "name": "get_grades",
        #     "description": "To get the student's grades",
        #     "parameters": {
        #         "type": "object",
        #         "properties": {
        #             "student_email": {"type": "string", "description": "The email of the student user",}
        #         },
        #         "required": ["student_email"],
        #     }
        #  },


        ],
       function_call="auto",
    )
    return response.choices[0]["message"]


def limit_line_width(text, max_line_width):
    """ Function to limit the line width of the text """
    if text is None: return ""
    lines = textwrap.wrap(text, width=max_line_width)
    return "\n".join(lines)

def get_registration(course_name):
    try:
        df = pd.read_csv("registration_records.csv")
        result = df[df['COURSE NAME']==course_name].to_dict()
        del df
    except Exception as e:
        result = e

    return result

def get_registration_all():
    try:
        df = pd.read_csv("registration_records.csv")
        result = df.to_dict()
        # result = df[df["EMAIL ADDRESS"] == student_email].to_dict()
        del df
    except Exception as e:
        result = e

    return result



# Display chat messages from history on app rerun
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
# Accept user input
if user_input := st.chat_input("Welcome to CSTU AdminChatGPT! 🤖"):
    if OPENAI_API_KEY:
        res = openai.Embedding.create(
            input=[user_input],
            engine=embed_model
            )
        kb_res = index.query(res['data'][0]['embedding'], top_k=1, include_metadata=True, namespace='cstu')
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

        if response.get("function_call"): # e.g. Sending email

            function_name = response["function_call"]["name"]
            # print("function_name: ",function_name)
            
            # function_to_call = available_functions[function_name]
            # print("function_to_call: ", function_to_call)

            function_args = json.loads(response["function_call"]["arguments"])
            if function_name == 'get_registration':
                result = get_registration(function_args.get("course_name")) 
                formatted_text = f"{result}"
            elif function_name == 'get_registration_all':
                result = get_registration_all() 
                formatted_text = f"{result}"
        
            # elif function_name == 'get_grades':
            #     result = get_grades(function_args.get("student_email")) 
            #     formatted_text = f"{result}"
            # else:
            #     print("function_name: ",function_name)
                
        
        else:
            # formatted_text = limit_line_width(response["content"], max_line_width)
            formatted_text = response["content"]

        ai_message = {"role": "assistant", "content": formatted_text}
        st.session_state.chat_history.append(ai_message)
        st.session_state.prompt_history.append(ai_message)

        # Display message in chat message container
        with st.chat_message("user"):
            st.write(user_message['content'])
        with st.chat_message("assistant"):
            try:
                st.write(pd.DataFrame(result))
            except Exception as e: 
                st.write(ai_message['content'])

    else:
        st.write("!!! Error: You need to enter OPENAI_API_KEY!")
    
# def show_grades():
#     st.header("Registered Students")
#     df = pd.read_csv("registtration_records.csv")
#     st.write(df)


# upload_grades = st.button("Upload Grades", key="upload_grades")

# if upload_grades:
grades_csv = st.file_uploader("Please select grades CSV file...", type="csv")
# print(grades_csv)
if grades_csv:
    try:
        df = pd.read_csv(grades_csv)
        if os.path.exists("./grades.csv"):
            print("Grades file found! appending")
            df.to_csv("./grades.csv", mode="a", index=False, header=False)
        else:
            df.to_csv("./grades.csv", index=False)
        st.write("Grades Uploaded!")
        st.balloons()
        del grades_csv 
    except Exception as e:
        st.write(e)