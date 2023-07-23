import openai
import os
from dotenv import load_dotenv
dotenv_path = '../.env'  #modify and  change to your correct path!
load_dotenv(dotenv_path)

openai.api_key = os.getenv("OPENAI_API_KEY")
print("Great, you have got you api key work: ", openai.api_key)


def get_answer(context, question):
    # Format the conversation with the given context and question
    conversation = f"User: {question}\nAssistant: {context}"

    # Use the OpenAI API to generate a response
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=conversation,
        max_tokens=150  # Adjust as needed based on your response length preference
    )

    # Extract and return the answer from the response
    answer = response.choices[0].text.strip()
    return answer

# Sample context from the data file (replace with your actual data)
context_from_file = """
California Science and Technology University (CSTU) is
an academic institution of post graduate learning that is
located in Milpitas, and committed to provide a quality education
to individuals whose goals include the development of rational,
systematic, and critical thinking while striving to succeed in their
chosen profession. CSTU was founded in 2011 and is licensed to operate
by the BPPE of California.  Based on the following information, please tell me...
"""

# Sample questions
question_1 = "Tell me about CSTU."
question_2 = "What is the location of CSTU?"
question_3 = "Why should I apply for CSTU?"

# Get answers based on the context
answer_1 = get_answer(context_from_file, question_1)
answer_2 = get_answer(context_from_file, question_2)
answer_3 = get_answer(context_from_file, question_3)

# Print the answers
print("Q: " + question_1)
print("A: " + answer_1)

print("\nQ: " + question_2)
print("A: " + answer_2)

print("\nQ: " + question_3)
print("A: " + answer_3)
