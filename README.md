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

## Usage

1. Open your terminal and navigate to the project directory.

2. Start the MyGPT chatbot:

   ```shell
   python mygpt.py
   ```

3. You will see a prompt inviting you to start a conversation.

4. Begin typing your messages and press Enter to send them.

5. To reload your last message, press the up arrow key and make necessary edits.

## Examples

Here are some examples of how to use MyGPT:

- Start a conversation:
  ```
  User: Hi there!
  MyGPT: Hello! How can I assist you today?
  ```

- Reload and edit the last message:
  ```
  User: {up arrow key}
  User: Hi there, I wanted to ask...
  MyGPT: Hello! How can I assist you today?
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
