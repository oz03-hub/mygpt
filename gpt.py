from openai import OpenAI
from dotenv import load_dotenv
import tiktoken
from rich import print
import time
import signal
import os
import sys

load_dotenv()
TOKEN_LIMIT = int(os.environ["TOKEN_LIMIT"])
STREAM_RESPONSE = True

def print_help():
    help_menu = [
        {"command": "!help", "description": "help menu"},
        {"command": "!new", "description": "reset chat instance"},
        {"command": "!pre", "description": "reload last prompt"},
        {"command": "!extract \[filename]", "description": "reads prompt from file"}
    ]

    for item in help_menu:
        print(f"[bold cyan]{item['command']}:[/bold cyan] [italic yellow]{item['description']}[/italic yellow]")


def signal_handler(sig, frame):
    print('\nExiting gracefully.')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def getCompletion(messages, client, model='gpt-3.5-turbo-0613'):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=STREAM_RESPONSE
    )

    return response

def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):
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
        response = getCompletion(messages, client)

        content = ''
        if STREAM_RESPONSE:
            for chunk in response:
                chunk_content = chunk.choices[0].delta.content or ''
                content += chunk_content
                for c in chunk_content:
                    print(c, end='')
                    time.sleep(0.02)
            print(flush=True)
        else:
            content = response.choices[0].message.content
            print(content, flush=True)

        messages.append({"role": "assistant", "content": content})
    
        if num_tokens_from_messages(messages) > token_limit:
            messages = trim_messages(messages)
