import os
from mistralai import Mistral
from dotenv import load_dotenv

api_key = None
model = None
client = None

def initModel():
    global api_key
    global model
    global client
    load_dotenv()

    api_key = os.getenv("MISTRAL_API_KEY")
    model = "mistral-large-latest"

    client = Mistral(api_key=api_key)


def sendMessage(context : list, user_message : str, system_prompt : str):
    context.append({"role": "user", "content": user_message})
    chat_response = client.chat.complete(
        model= model,
        messages = context + [{"role": "system", "content": system_prompt}]
    )
    agent_answer = chat_response.choices[0].message.content
    context.append({"role": "assistant", "content": agent_answer})
    return context


user_input = ""
context = []

initModel()

standard_prompt = "You are a helpful assistant."

if __name__ == "__main__":
    while True:
        user_input = input("> ")
        if user_input == "exit":
            break

        context = sendMessage(context, user_input, standard_prompt)
        print(f"\n\nAgent: {context[-1]['content']}\n")