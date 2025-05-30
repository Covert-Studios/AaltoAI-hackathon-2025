import openai

# Set your API key
openai.api_key = "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"

# Generate a completion
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "write a haiku about ai"}
    ]
)

# Print the response
print(response['choices'][0]['message']['content'])