# MyGPT - Terminal-based Chatbot/Assistant

MyGPT is a chatbot/assistant built for the terminal. It provides chat 
functionality and some commands to enhance your user experience.

## Features

- Chat functionality: You can have interactive conversations with MyGPT.
- Up arrow key: Pressing the up arrow key reloads your last message, allowing 
you to make quick edits and resend it.

## Requirements

- Python 3 (version X or higher)
- Internet connection

## Installation

1. Clone this repository:

   ```shell
   git clone https://github.com/oz03-hub/mygpt.git
   ```

2. Navigate to the project directory:

   ```shell
   cd mygpt
   ```

3. Copy the `env-example.txt` to `.env`:

Get you own OpenAI api-key from [OpenAI](openai.com)

3. Install the dependencies using pip:

   ```shell
   pip install -r requirements.txt
   ```

4. Make a `user_files` in the same directory to store your prompt files (highly recommended)

## Usage

1. Open your terminal and navigate to the project directory.

2. Start the MyGPT chatbot:

   ```shell
   python mygpt.py
   ```

3. You will see a prompt inviting you to start a conversation.

4. Begin typing your messages and press Enter to send them.

5. Utilize commands at your disposal to boost your interaction.

## Commands

```
!help: help menu
!new: reset chat instance
!pre: reload last prompt
!extract [filename]: reads prompt from file, list this command in last with your prompt being the file path
```

## Examples

Here are some examples of how to use MyGPT:

- Start a conversation:
  ```
  User: Hi there!
  MyGPT: Hello! How can I assist you today?
  ```

- Reset instance:
  ```
  // Previous conversation
  User: !new how to say good morning in Spanish?
  MyGPT: Buenos Dias!
  ```

- Reload last prompt:
   ```
   User: !pre
   MyGPT: Good morning in Spanish would be Buenos Dias!
   ```

- Extract prompt from a file:
   ```
   User: !extract /path/to/your/file.txt
   MyGPT: To write a python function that calculates...
   ```

   TIP: You can still reload the file prompt

   ```
   User: !pre
   MyGPT: Let's see how we can develop  a python function that...
   ```

- You can chain some commands:
   ```
   // Building from spanish examples
   User: !new !pre
   MyGPT: Spanish good morning is Buenos Dias!
   ```

## Contributing

Contributions are welcome! If you find any bugs or have suggestions for 
improvement, please open a new issue or submit a pull request.

## License

This project is licensed under the [MIT 
License](https://opensource.org/licenses/MIT).

## Acknowledgements

- [OpenAI GPT-3](https://openai.com) for providing the underlying language 
model.

---
