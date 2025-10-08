import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
# Configure your API key (replace with your actual key or environment variable)
def model_giving():
    api_key = os.getenv("GOOGLE_API_KEY")
    genai.configure(api_key=api_key)

    # Initialize the generative model
    # You can choose different models like 'gemini-pro', 'gemini-2.5-flash', etc.
    model = genai.GenerativeModel('gemini-2.5-pro')
    return model

# # Generate content
# prompt = "Explain large language models in a concise way."
# response = model.generate_content(prompt)

# # Print the generated text
# print(response.text)