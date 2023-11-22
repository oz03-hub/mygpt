def write_to_file(filename: str, content: str):
    try:
        with open(filename, 'w') as file:
            file.write(content)
        print(f"Content successfully written to {filename}")
    except Exception as e:
        print(f"Error writing to {filename}: {e}")
