from dotenv import load_dotenv
import tiktoken
import time
import os
import sys
import json
import requests
from tenacity import retry, wait_random_exponential, stop_after_attempt

class Util:
    def parse_command(self, input_str: str):
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
    
    def output_by_stream_type(self, response, type):
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
    
    def output_by_no_stream(self, response):
        content = response["choices"][0]["message"]["content"]
        print(content, flush=True)

        return content

class GPT:
    # Specs:
    # - OpenAI API KEY, api key
    # - Token Limit, int
    # - Model Type, string of model name 'gpt-3.5-turbo-0613'
    # - Stream Type, [0, 1, 2], read .env
    # - Tools, [functions]
    def __init__(self, specs) -> None:
        self.__OPENAI_API_KEY = specs["OPENAI_API_KEY"]
        self.__TOKEN_LIMIT = specs["TOKEN_LIMIT"]
        self.__MODEL_TYPE = specs["MODEL_TYPE"]
        self.__STREAM_TYPE = specs["STREAM_TYPE"]
        self.__STREAM_ALLOWED = self.__STREAM_ALLOWED != 0
        self.__TOOLS = specs["TOOLS"]
        self.messages = []

        self.util = Util()


    @retry(wait=wait_random_exponential(multiplier=1, max=40, stop=stop_after_attempt(3)))
    def chat_completion_request(self, messages):
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.__OPENAI_API_KEY
        }
        json_data = {"model": self.__MODEL_TYPE, "messages": messages}
        
        if self.__TOOLS is not None:
            json_data.update({"tools": self.__TOOLS})
        
        if self.__STREAM_ALLOWED:
            json_data.update({"stream": self.__STREAM_ALLOWED})

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
    
    def num_tokens_from_messages(self):
        try:
            encoding = tiktoken.encoding_for_model(self.__MODEL_TYPE)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")

        tokens_per_message = 3
        tokens_per_name = 1
        num_tokens = 0
        for message in self.messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens

    def trim_messages(self):
        limit = self.__TOKEN_LIMIT // 3
        T = 0
        for i in range(len(self.messages)-1, -1, -1):
            T += self.num_tokens_from_messages([self.messages[i]])
            if T > limit:
                return self.messages[i:]
        
        return self.messages
