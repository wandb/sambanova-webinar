import json
import re
from typing import Optional, Union, Dict, Any

def extract_json_from_string(content: str) -> Optional[Dict[str, Any]]:
    """
    Attempts to extract and parse a JSON object from a string that may contain markdown,
    explanatory text, or code blocks.
    
    Args:
        content (str): The input string that may contain a JSON object
        
    Returns:
        Optional[Dict[str, Any]]: The parsed JSON object if found and valid, None otherwise
        
    """
    if not isinstance(content, str):
        return None
        
    # Clean the input string
    content = content.strip()
    
    # Try to find JSON in code blocks first
    code_block_pattern = r"```(?:json)?\s*({[\s\S]*?})\s*```"
    code_blocks = re.findall(code_block_pattern, content)
    
    # If found in code blocks, try the first one
    if code_blocks:
        try:
            return json.loads(code_blocks[0])
        except json.JSONDecodeError:
            pass
    
    # If no valid JSON in code blocks, try to find any {...} pattern
    # Using a more precise pattern that matches balanced braces
    def find_json_objects(s: str) -> list[str]:
        objects = []
        stack = []
        start = -1
        
        for i, char in enumerate(s):
            if char == '{':
                if not stack:
                    start = i
                stack.append(char)
            elif char == '}':
                if stack:
                    stack.pop()
                    if not stack and start != -1:
                        objects.append(s[start:i+1])
                        start = -1
        
        return objects
    
    # Find all potential JSON objects with balanced braces
    matches = find_json_objects(content)
    
    # Try each potential JSON match
    for match in matches:
        try:
            # Clean the match by removing markdown code block syntax
            cleaned = match.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)
        except json.JSONDecodeError:
            continue
            
    # If the entire content looks like a JSON object, try that
    if content.startswith("{") and content.endswith("}"):
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
            
    return None 