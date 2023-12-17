from openai import OpenAI
from dotenv import load_dotenv
import tiktoken
from rich import print
import time
import signal
import os
import sys
import json
import requests
from tenacity import retry, wait_random_exponential, stop_after_attempt
from termcolor import colored

from gpt_functions import write_to_file

load_dotenv()
OPENAI_API_KEY = str(os.environ["OPENAI_API_KEY"])
TOKEN_LIMIT = int(os.environ["TOKEN_LIMIT"])
MODEL_TYPE = str(os.environ["MODEL_TYPE"])
STREAM_TYPE = int(os.environ["STREAM_TYPE"])
STREAM_ALLOWED = STREAM_TYPE != 0

### Under Construction ###
@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, tools=None, tool_choice=None, model=MODEL_TYPE):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + OPENAI_API_KEY,
    }
    json_data = {"model": model, "messages": messages}
    if tools is not None:
        json_data.update({"tools": tools})
    if tool_choice is not None:
        json_data.update({"tool_choice": tool_choice})
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data,
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e

def pretty_print_conversation(messages):
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "tool": "magenta",
    }
    
    for message in messages:
        if message["role"] == "system":
            print(colored(f"system: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "user":
            print(colored(f"user: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and message.get("function_call"):
            print(colored(f"assistant: {message['function_call']}\n", role_to_color[message["role"]]))
        elif message["role"] == "assistant" and not message.get("function_call"):
            print(colored(f"assistant: {message['content']}\n", role_to_color[message["role"]]))
        elif message["role"] == "tool":
            print(colored(f"function ({message['name']}): {message['content']}\n", role_to_color[message["role"]]))

def get_current_weather(args):
    print(args)

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    }
                },
                "required": ["location"],
            },
        }
    }
]

def execute_function_call(message):
    if message["tool_calls"][0]["function"]["name"] == "get_current_weather":
        args = json.loads(message["tool_calls"][0]["function"]["arguments"])["location"]
        results = get_current_weather(args)
    else:
        results = f"Error: function {message['tool_calls'][0]['function']['name']} does not exist"
    return results

messages = []
messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
messages.append({"role": "user", "content": "Hi how is the weather in Ankara, Turkey in celsius"})
chat_response = chat_completion_request(messages, tools)
chat_response = chat_completion_request(messages, tools)
assistant_message = chat_response.json()["choices"][0]["message"]
assistant_message['content'] = str(assistant_message["tool_calls"][0]["function"])
messages.append(assistant_message)
if assistant_message.get("tool_calls"):
    results = execute_function_call(assistant_message)
    messages.append({"role": "tool", "tool_call_id": assistant_message["tool_calls"][0]['id'], "name": assistant_message["tool_calls"][0]["function"]["name"], "content": results})
pretty_print_conversation(messages)

# messages = []
# messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
# messages.append({"role": "user", "content": "What's the weather like today"})
# chat_response = chat_completion_request(
#     messages, tools=tools
# )
# assistant_message = chat_response.json()["choices"][0]["message"]
# messages.append(assistant_message)
# print(assistant_message)

# messages.append({"role": "user", "content": "I'm in Glasgow, Scotland."})
# chat_response = chat_completion_request(
#     messages, tools=tools
# )
# assistant_message = chat_response.json()["choices"][0]["message"]
# messages.append(assistant_message)
# print(assistant_message)

# messages = []
# messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
# messages.append({"role": "user", "content": "what is the weather going to be like in Glasgow, Scotland over the next x days"})
# chat_response = chat_completion_request(
#     messages, tools=tools
# )
# assistant_message = chat_response.json()["choices"][0]["message"]
# messages.append(assistant_message)
# print(assistant_message)


### Under Construction ###
