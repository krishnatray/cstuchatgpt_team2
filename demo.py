import os
import streamlit as st
from dotenv import load_dotenv
import openai
import json
from CourseManagement import CourseManagement

# Initialize Streamlit app
st.title("Chatbot with GPT-3.5 Turbo")
st.write("Enter your message below:")

courseManage = CourseManagement()
dotenv_path = '../.env'  # modify and change to your correct path!
load_dotenv(dotenv_path)
openai.api_key = os.getenv("OPENAI_API_KEY")

def chat_complete(prompt):
    # Query against the model "gpt-3.5-turbo-0613"
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        temperature=0,  # this is the degree of randomness of the model's output
    )
    return response.choices[0]["message"]["content"]

def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    weather_info = {
        "location": location,
        "temperature": "72",
        "unit": unit,
        "forecast": ["sunny", "windy"],
    }
    return json.dumps(weather_info)

def main():
    user_input = st.text_area("User Input")

    if st.button("Send"):
        messages = [{"role": "user", "content": user_input}]

        functions = [
            {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                    "required": ["location"],
                },
            },
            {
                "name": "get_course_information",
                "description": "Get the course information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "course_id": {
                            "type": "string",
                            "description": "The course id"
                        },
                        "course_title": {
                            "type": "string",
                            "description": "The course title"
                        },
                        "course_description": {
                            "type": "string",
                            "description": "The new course description"
                        }
                    },
                    "anyOf": [
                        {"required": ["course_id"]},
                        {"required": ["course_title"]}
                    ]
                }
            }
        ]

        available_functions = {
            "get_current_weather": get_current_weather,
            "get_course_information": courseManage.get_course_information,
        }

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=messages,
            functions=functions,
            function_call="auto",  # auto is default, but we'll be explicit
        )

        response_message = response["choices"][0]["message"]

        # Step 2: check if GPT wanted to call a function
        if response_message.get("function_call"):
            function_name = response_message["function_call"]["name"]
            #st.write("function_name: ", function_name)

            function_to_call = available_functions.get(function_name)
            if function_to_call:
                function_args = json.loads(response_message["function_call"]["arguments"])

                # Step 3: call the function
                # Note: the JSON response may not always be valid; be sure to handle errors
                function_response = function_to_call(
                    **function_args
                )
                #st.write(response_message, function_response)

                # Step 4: send the info on the function call and function response to GPT
                messages.append(response_message)  # extend conversation with assistant's reply
                messages.append(
                    {
                        "role": "function",
                        "name": function_name,
                        "content": function_response,
                    }
                )  # extend conversation with function response

                second_response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo-0613",
                    messages=messages,
                )  # get a new response from GPT where it can see the function response
                #st.write(second_response)
            else:
                st.write("Function not available")
        else:
            st.write("GPT does not want to call")

        st.write(str(second_response["choices"][0]["message"]["content"]))

if __name__ == "__main__":
    main()





