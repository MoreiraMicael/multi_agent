import re
import requests
import json
import logging
from typing import List

logger = logging.getLogger(__name__)

def extract_python_code_blocks(content: str) -> List[str]:
    code_blocks = []
    python_blocks = re.findall(r"```python\n(.*?)\n```", content, re.DOTALL)
    code_blocks.extend(python_blocks)
    generic_blocks = re.findall(r"```\n(.*?)\n```", content, re.DOTALL)
    for block in generic_blocks:
        if (
            "def " in block
            or "import " in block
            or "class " in block
            or "if __name__" in block
            or "print(" in block
        ):
            code_blocks.append(block)
    return code_blocks

def save_generated_code(code_blocks: List[str], output_file: str) -> bool:
    """
    Save the last code block from a list to a file.
    
    Args:
        code_blocks (List[str]): List of code blocks extracted from conversation
        output_file (str): Path to output file
        
    Returns:
        bool: True if successful, False otherwise
    """
    if not code_blocks:
        logger.warning("No Python code blocks found in the conversation.")
        return False
    final_code = code_blocks[-1].strip()
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(final_code)
        logger.info(f"Generated code saved to: {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error saving code to {output_file}: {e}")
        return False

# Load Ollama config from OAI_CONFIG_LIST
with open('OAI_CONFIG_LIST', 'r', encoding='utf-8') as f:
    config_list = json.load(f)
    ollama_config = config_list[0]

OLLAMA_MODEL = ollama_config.get('model', 'llama3:8b')
OLLAMA_BASE_URL = ollama_config.get('base_url', 'http://localhost:11434/v1')
OLLAMA_API_KEY = ollama_config.get('api_key', 'ollama')

def call_ollama(prompt: str, system_message: str = '', role: str = 'user', model: str = None, base_url: str = None) -> str:
    """
    Call the local Ollama LLM for code generation or review.
    Args:
        prompt (str): The prompt to send to the LLM.
        system_message (str): Optional system message for the LLM.
        role (str): Role for the message (default 'user').
        model (str): Model name (default from config).
        base_url (str): Ollama API base URL (default from config).
    Returns:
        str: The LLM's response content.
    """
    url = f"{base_url or OLLAMA_BASE_URL}/chat/completions"
    headers = {"Authorization": f"Bearer {OLLAMA_API_KEY}"}
    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": role, "content": prompt})
    data = {
        "model": model or OLLAMA_MODEL,
        "messages": messages,
        "stream": False
    }
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]
