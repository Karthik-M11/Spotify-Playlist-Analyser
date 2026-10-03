from google import genai
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# The client automatically picks up the GEMINI_API_KEY environment variable
client = genai.Client()

# Initialize the chat session
chat = client.chats.create(model="gemini-3.8-flash")


# get the response from the model
response = chat.send_message("How are you today?")
print(response.text)