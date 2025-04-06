import os
from mistralai import Mistral
import openai
from dotenv import load_dotenv

api_key = None
model = None
client = None

def initModel():
    global model
    load_dotenv()

    openai.api_key = os.getenv("OPENAI_API_KEY")
    model = "gpt-4"

def sendMessage(context: list, user_message: str, system_prompt: str):
    context.append({"role": "user", "content": user_message})
    chat_response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "system", "content": system_prompt}] + context
    )
    agent_answer = chat_response["choices"][0]["message"]["content"]
    context.append({"role": "assistant", "content": agent_answer})
    return context


user_input = ""
context = []

standard_prompt = "You are a helpful assistant."

if __name__ == "__main__":
    initModel()
    while True:
        user_input = input("> ") ### input part
        if user_input == "exit":
            break

        context = sendMessage(context, user_input, standard_prompt)
        print(f"\n\nAgent: {context[-1]['content']}\n") ### Redepart