import os
import aiofiles
from openai import OpenAI
import orjson
from app.utils.prompts import system_prompt_dict, instruction_dict
import json
from dotenv import load_dotenv
from pathlib import Path
from app.services.database_service import AISetupService
from app.database import SessionLocal
load_dotenv()
SAMPLE_DATA_DIR = Path(os.getenv("SAMPLE_DATA_DIR", "./sample"))


class AIParser:
    def __init__(self, source: str, temperature: int = 0):
        self.source = source
        self.model = 'openai-gpt-54'
        self.max_tokens = 130_000
        self.client = OpenAI(
            api_key=os.getenv("VENICE_API_KEY"),
            base_url="https://api.venice.ai/api/v1"
        )
        self.instructions = instruction_dict.get(source, "No instructions found for this source")
        self.prompt = system_prompt_dict.get(source, "No system prompt found for this source")
        self.temperature = temperature
        db = SessionLocal()
        try:
            ai_setup = AISetupService.get_prompt(db, source=source)
            if ai_setup:
                self.instructions = ai_setup["instructions"]
                self.prompt = ai_setup["prompt"]
                self.temperature = ai_setup["temperature"] / 100.0  # Convert from 0-100 to 0.0-1.0
        finally:
            db.close()

    def call_ai(self, data: str, history: list[dict] = None):
        """
        history: list of dicts [{"role":"user/assistant", "content": "..."}, ...]
        """
        messages = [{"role": "system", "content": self.prompt}]

        if history:
            messages.extend(history)

        messages.append({"role": "user", "content": self.instructions + data})

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=messages,
            temperature=self.temperature
        )
        return self.parse_response(response.choices[0].message.content)

    def parse_response(self, response_content: str):
        try:
            parsed_data = json.loads(response_content)
            return parsed_data
        except json.JSONDecodeError:
            return {"text": response_content}


async def load_json(
    filename: str,
    ip_address: str,
    max_chars: int = 10_000,
):
    # Add _sample suffix before .jsonl extension
    if filename.endswith('.jsonl'):
        filename = filename.replace('.jsonl', '_sample.jsonl')
    else:
        filename = f"{filename}_sample.jsonl"

    filepath = SAMPLE_DATA_DIR / ip_address / filename

    data = []
    total_chars = 0
    if not filepath.exists():
        raise FileNotFoundError(f"Index file {filepath} does not exist")
    async with aiofiles.open(filepath, 'r') as f:
        async for line in f:
            line = line.strip()
            if not line:
                continue
            total_chars += len(line)
            if total_chars > max_chars:
                break
            data.append(orjson.loads(line))

    return data
