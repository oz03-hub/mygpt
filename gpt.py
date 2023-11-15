from openai import OpenAI
from dotenv import load_dotenv
import tiktoken
from rich import print
import signal
import os
import sys

load_dotenv()
TOKEN_LIMIT = int(os.environ["TOKEN_LIMIT"])

def signal_handler(sig, frame):
    print('\nExiting gracefully.')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def getCompletion(messages, client, model='gpt-3.5-turbo-0613'):
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )

    return response.choices[0].message

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

if __name__ == "__main__":
    client = OpenAI()
    messages = []
    tokenLimit = TOKEN_LIMIT

    previousMessage = None

    while True:
        userIn = input('User: ')
        if userIn == '\x1b[A':
            if previousMessage == None:
                print("[bold red]No previous prompt...[/bold red]")
                continue
            
            userIn = previousMessage
            print("[bold blue]RE: {}...[/bold blue]".format(userIn[:20]))

        previousMessage = userIn
        messages.append({"role": "user", "content": userIn})
        print("[bold blue]Processing...[/bold blue]")
        response = getCompletion(messages, client)
        messages.append({"role": response.role, "content": response.content})
        print('Assistant: ', end='')
        print(messages[-1]['content'])

        if num_tokens_from_messages(messages) > tokenLimit:
            messages = trim_messages(messages)
