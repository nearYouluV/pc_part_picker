import os
import aiofiles
from openai import OpenAI
import orjson
from app.utils.prompts import system_prompt_dict, instruction_dict
import json
from dotenv import load_dotenv
from pathlib import Path
load_dotenv()


class AIParser:
    def __init__(self, source: str, temperature: int = 0):
        self.source = source
        self.model = 'gemini-3-flash-preview'
        self.max_tokens = 130_000
        self.client = OpenAI(
            api_key=os.getenv("VENICE_API_KEY"),
            # base_url="https://api.venice.ai/api/v1"
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.instructions = instruction_dict.get(source, "No instructions found for this source")
        self.prompt = system_prompt_dict.get(source, "No system prompt found for this source")
        self.temperature = temperature

    def call_ai(self, data: str, history: list[dict] = None):
        """
        history: list of dicts [{"role":"user/assistant", "content": "..."}, ...]
        """
        messages = [{"role": "system", "content": self.prompt}]

        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": self.instructions + data})
        print("Messages sent to AI:", messages)

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=messages,
            temperature=self.temperature
        )
        print("AI response:", response.choices[0].message.content)
        return self.parse_response(response.choices[0].message.content)

    def parse_response(self, response_content: str):
        try:
            parsed_data = json.loads(response_content)
            return parsed_data
        except json.JSONDecodeError:
            return {"text": response_content}

