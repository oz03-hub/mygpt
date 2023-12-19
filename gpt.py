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

from gpt_functions import write_to_file, print_help, TOOLS

load_dotenv()
OPENAI_API_KEY = str(os.environ["OPENAI_API_KEY"])
TOKEN_LIMIT = int(os.environ["TOKEN_LIMIT"])
MODEL_TYPE = str(os.environ["MODEL_TYPE"])
STREAM_TYPE = int(os.environ["STREAM_TYPE"])
STREAM_ALLOWED = STREAM_TYPE != 0

def signal_handler(sig, frame):
    print('\nExiting gracefully.')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

### Export to functions_testing.py
### Import from functions_testing.py
### Under Construction ###
@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, tools=TOOLS, tool_choice=None, model=MODEL_TYPE):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + OPENAI_API_KEY,
    }
    json_data = {"model": model, "messages": messages, "stream": STREAM_ALLOWED}
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
        return response.json()
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e

# def getCompletion(messages, client, model=MODEL_TYPE):
#     response = client.chat.completions.create(
#         model=model,
#         messages=messages,
#         stream=STREAM_ALLOWED
#     )

#     return response

### Under Construction ###

def num_tokens_from_messages(messages, model=MODEL_TYPE):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens

def trim_messages(messages, limit=(TOKEN_LIMIT/3)):
    T = 0
    for i in range(len(messages)-1, -1, -1):
        T += num_tokens_from_messages([messages[i]])
        if T > limit:
            return messages[i:]
    
    return messages

def parse_command(input_str: str):
    commands = []
    prompt = ""

    words = input_str.split()
    for i, word in enumerate(words):
        if word.startswith('!'):
            commands.append(word[1:])
        else:
            prompt = ' '.join(words[i:])
            prompt = prompt.strip()
            break

    return commands, prompt

def extract_prompt_from_file(file_name):
    try:
        with open(file_name, 'r') as file:
            file_content = file.read()
            return file_content
    except FileNotFoundError:
        print("[bold red]File {} not found...[/bold red]".format(file_name))
        return None
    except Exception as e:
        print("[bold red]An error occurred: {}[/bold red]".format(e))
        return None
    
def output_by_stream_type(response, type):
    if type == 1: # character
        def char_routine(content: str):
            for c in content:
                print(c, end='')
                time.sleep(0.01)

        callback_fn = char_routine
    else: # 2, chunk
        def chunk_routine(content: str):
            print(content, end='')
            time.sleep(0.01)
        
        callback_fn = chunk_routine

    content = ''
    for chunk in response:
        chunk_content = chunk.choices[0].delta.content or ''
        content += chunk_content
        callback_fn(chunk_content)
    print(flush=True)

    return content

def output_by_no_stream(response):
    content = response["choices"][0]["message"]["content"]
    print(content, flush=True)

    return content

if __name__ == "__main__":
    client = OpenAI()
    messages = []
    token_limit = TOKEN_LIMIT

    previous_message = None

    while True:
        user_input = input('User: ')
        commands, prompt = parse_command(user_input)
        continue_processing = True

        for command in commands:
            if command == 'help':
                print_help()
                continue_processing = False
                break
            elif command == 'new':
                messages = []
            elif command == 'pre':
                prompt = previous_message
            elif command == 'extract':
                prompt = extract_prompt_from_file(prompt)
                if prompt == None:
                    continue_processing = False

        if not continue_processing:
            continue

        print("[italic yellow]CMD: {}, P: {}...[/italic yellow]".format(commands, prompt[:10]))
        previous_message = prompt
        messages.append({"role": "user", "content": prompt})
        print("[bold blue]Processing...[/bold blue]")
        print('Assistant: ', end='')
        response = chat_completion_request(messages=messages, tools=TOOLS)

        if STREAM_ALLOWED:
            content = output_by_stream_type(response, STREAM_TYPE)
        else:
            content = output_by_no_stream(response)

        messages.append({"role": "assistant", "content": content})
    
        if num_tokens_from_messages(messages) > token_limit:
            messages = trim_messages(messages)
