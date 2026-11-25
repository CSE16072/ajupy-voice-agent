
from google import genai
from config import GEMINI_API_KEY
import time

client = genai.Client(api_key=GEMINI_API_KEY)

MODELS = [
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite"
]


def generate_response(user_message, chat_history=None):

    prompt = """
    You are AJUPY AI, a friendly and professional AI voice assistant.

    Use the conversation history to understand follow-up questions.
    Remember the context of the current conversation.
    Answer clearly and naturally.
    Keep answers concise because they will be spoken aloud.

    """

    # Add previous conversation
    if chat_history:
        prompt += "\nPrevious conversation:\n"

        for message in chat_history[-10:]:
            role = message["role"]
            content = message["content"]

            if role == "user":
                prompt += f"User: {content}\n"
            else:
                prompt += f"AJUPY AI: {content}\n"

    prompt += f"\nUser's latest message: {user_message}\nAJUPY AI:"

    for model in MODELS:
        try:
            print(f"Trying Gemini model: {model}")

            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            if response.text:
                print(f"Successful model: {model}")
                return response.text

        except Exception as error:
            print(f"Gemini API Error: {error}")

            error_message = str(error)

            if "503" in error_message or "UNAVAILABLE" in error_message:
                time.sleep(2)
                continue

    return "Sorry, my AI service is temporarily unavailable. Please try again."
