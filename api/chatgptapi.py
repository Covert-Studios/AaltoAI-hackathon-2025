from dotenv import load_dotenv
import os
import openai

# Load environment variables from .env file
load_dotenv()

# Set up the OpenAI client with the API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Generate a response
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",  # Use gpt-3.5-turbo instead of gpt-4
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "How do I check if a Python object is an instance of a class?"}
    ]
)

# Print the response
print(response['choices'][0]['message']['content'])