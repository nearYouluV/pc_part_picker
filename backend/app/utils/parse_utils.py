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
        self.model = 'llama-3.3-70b-versatile'
        self.max_tokens = 32768
        self.client = OpenAI(
            api_key=os.getenv("VENICE_API_KEY"),
            # base_url="https://api.venice.ai/api/v1"
            base_url="https://api.groq.com/openai/v1",
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
            for message in history:
                if not isinstance(message, dict):
                    continue

                role = str(message.get("role") or "").strip().lower()
                content = message.get("content")
                if role not in {"user", "assistant", "system"}:
                    continue
                if not isinstance(content, str):
                    content = str(content or "")

                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": self.instructions + data})
        print("Messages sent to AI:", messages)

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=self.temperature
        )
        print("AI response:", response.choices[0].message.content)
        return self.parse_response(response.choices[0].message.content)

    def parse_response(self, response_content: str) -> dict:
        try:
            parsed_data = json.loads(response_content)
            return parsed_data
        except json.JSONDecodeError:
            return {"text": response_content}

