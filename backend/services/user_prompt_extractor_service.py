import os
import json
import requests
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.envutils import EnvUtils

class UserPromptExtractor:
    def __init__(self):
        """
        This class uses the raw requests approach (like a curl) 
        to call the SambaNova ChatCompletion endpoint,
        extracting user prompts into a structured JSON.

        Make sure your environment includes SAMBANOVA_API_KEY.
        """
        self.env_utils = EnvUtils()
        self.api_key = self.env_utils.get_required_env("SAMBANOVA_API_KEY")

        # We'll use an example model name "gpt-4o-mini" 
        # as in your curl snippet. Adjust if needed:
        self.model_name = "Meta-Llama-3.1-8B-Instruct"  
        self.url = "https://api.sambanova.ai/v1/chat/completions"

    def extract_lead_info(self, prompt: str) -> dict:
        """
        Make a POST request via 'requests' to the OpenAI ChatCompletion endpoint 
        (similar to the raw curl call).
        We instruct the model to return JSON with keys:
          'industry', 'company_stage', 'geography', 'funding_stage', 'product'.
        """

        # You can customize system/user messages to ensure the LLM returns only JSON
        system_message = (
            "You are an expert system that extracts structured JSON "
            "from a user prompt. Always respond ONLY with valid JSON "
            "containing these keys: 'industry', 'company_stage', 'geography', "
            "'funding_stage', 'product'. If a key is not found, leave it empty."
        )
        user_message = f"""
        The user prompt is:
        {prompt}

        Extract the data into a JSON object with exactly these keys:
        industry, company_stage, geography, funding_stage, product.

        Example output:
        {{
          "industry": "",
          "company_stage": "",
          "geography": "",
          "funding_stage": "",
          "product": ""
        }}

        Return ONLY that JSON object, with no extra text or markdown.
        """

        # Build the request payload
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7  # or 0.0 if you want it more deterministic
        }

        # Build headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            # Make the POST request
            response = requests.post(
                self.url,
                headers=headers,
                data=json.dumps(payload),
                timeout=30
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"HTTP error calling SambaNova ChatCompletion: {e}")
            return {
                "industry": "",
                "company_stage": "",
                "geography": "",
                "funding_stage": "",
                "product": ""
            }

        # Parse the JSON response
        try:
            json_response = response.json()
        except json.JSONDecodeError:
            print("Error: Could not parse JSON from OpenAI response.")
            return {
                "industry": "",
                "company_stage": "",
                "geography": "",
                "funding_stage": "",
                "product": ""
            }

        # Extract the content from the first choice
        if "choices" not in json_response or len(json_response["choices"]) == 0:
            print("Error: No choices found in OpenAI response.")
            return {
                "industry": "",
                "company_stage": "",
                "geography": "",
                "funding_stage": "",
                "product": ""
            }

        content = json_response["choices"][0]["message"]["content"].strip()
        content = content.replace("```json", "").replace("```", "").strip()

        # Attempt to parse the LLM's content as JSON
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON from LLM content: {content}")
            parsed = {}

        # Ensure the five keys exist
        for key in ["industry", "company_stage", "geography", "funding_stage", "product"]:
            if key not in parsed:
                parsed[key] = ""

        return parsed

def main():
    extractor = UserPromptExtractor()
    prompt = "Generate leads for AI Chip Startups in Silicon Valley"
    result = extractor.extract_lead_info(prompt)
    print("Extracted lead info:")
    print(result)

if __name__ == "__main__":
    main()
