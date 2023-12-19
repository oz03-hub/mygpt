def write_to_file(filename: str, content: str):
    try:
        with open(filename, 'w') as file:
            file.write(content)
        print(f"Content successfully written to {filename}")
    except Exception as e:
        print(f"Error writing to {filename}: {e}")

def print_help():
    help_menu = [
        {"command": "!help", "description": "help menu"},
        {"command": "!new", "description": "reset chat instance"},
        {"command": "!pre", "description": "reload last prompt"},
        {"command": "!extract \[filename]", "description": "reads prompt from file"}
    ]

    for item in help_menu:
        print(f"[bold cyan]{item['command']}:[/bold cyan] [italic yellow]{item['description']}[/italic yellow]")

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "write_to_file",
            "description": "Writes to a file on the user's system",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "The filename.",
                    },
                    "content": {
                        "type": "string",
                        "description": "The string content to write to file."
                    }
                },
                "required": ["filename", "content"],
            },
        }
    }
]
