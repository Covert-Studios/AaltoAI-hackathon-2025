import os
import openai  # Use the correct OpenAI library

# Set up the OpenAI client with the API key from the environment variable
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Generate a response
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a coding assistant that talks like a pirate."},
        {"role": "user", "content": "How do I check if a Python object is an instance of a class?"}
    ]
)

# Print the response
print(response['choices'][0]['message']['content'])