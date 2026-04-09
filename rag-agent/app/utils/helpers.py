import os

def load_prompt(filename: str) -> str:
    """Loads a prompt template from the app/prompts directory."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    prompt_path = os.path.join(base_dir, "prompts", filename)
    
    try:
        with open(prompt_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: Prompt file '{filename}' not found at {prompt_path}")
        return ""