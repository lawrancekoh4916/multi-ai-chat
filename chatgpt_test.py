import os
import openai
from dotenv import load_dotenv
from chatgpt_client import ChatGPTClient

# Load environment variables from .env file
load_dotenv()

# Instantiate the ChatGPT client
chatgpt_client = ChatGPTClient(api_key=os.getenv("OPENAI_API_KEY"))

# Define the prompt
prompt = "Hello, ChatGPT! How are you today?"

# Get a response from ChatGPT
response = chatgpt_client.get_response(prompt)
print(response)