# LLM calls

from groq import Groq, RateLimitError
import re
import json

import os
from dotenv import load_dotenv
load_dotenv()


class GroqLLM:
    # model = "llama3-8b-8192"
    model = "llama-3.3-70b-versatile"

    def __init__(self):
        self.api_key_turn = 0
        self.api_keys = [
            os.getenv("GROQ_API_KEY__1__BADHAT"), 
            os.getenv("GROQ_API_KEY__2__FSOCIETY"), 
            os.getenv("GROQ_API_KEY__3__ANITON"), 
            os.getenv("GROQ_API_KEY__4__MKNC_PNP"), 
            os.getenv("GROQ_API_KEY__5__SOUTH_OFFICE"), 
            os.getenv("GROQ_API_KEY__6__GAMH"), 
            os.getenv("GROQ_API_KEY__7__MADHAVAMPIRE"), 
            os.getenv("GROQ_API_KEY__8__FERB"), 
            os.getenv("GROQ_API_KEY__9__PHINEASE"), 
            os.getenv("GROQ_API_KEY__10__AKUMARK"), 
        ]
        self.api_key = self.api_keys[self.api_key_turn]
        self.client = Groq(api_key=self.api_key)

    def get_llm_response(self, messages, model=model):
        try:
            response = self.client.chat.completions.create(
                model = model or self.model,
                messages = messages,
            )
            output = response.choices[0].message.content.strip()
            return output
        except RateLimitError as RLE:
            self.api_key_turn = (self.api_key_turn + 1) % len(self.api_keys)
            self.api_key = self.api_keys[self.api_key_turn]
            self.client = Groq(api_key=self.api_key)
            return self.get_llm_response(messages=messages, model=model)
        except Exception as E:
            print(f"[error in groq.get_llm_response] {E}")
            self.api_key_turn = (self.api_key_turn + 1) % len(self.api_keys)
            self.api_key = self.api_keys[self.api_key_turn]
            self.client = Groq(api_key=self.api_key)
            print(f"[Exception in groq.get_llm_response]: {E}\n\nAPI key turn: {self.api_key_turn}")
            return self.get_llm_response(messages=messages, model=model)


# llm
llm = GroqLLM()
PROMPT = """
Extract attendance data from the text and return ONLY valid JSON array. No explanations, no markdown.
Extract: total_mem, present, absent as integers.

Format:
```json
[
    {{
        "date": "01-01-2010 (Friday)",
        "data": [
            {{"team_name": "District Name", "total_mem": 0, "present": 0, "absent": 0}},
            ...
        ]
    }},
    ... other dates (if any)
]
```

Attendance data:

{data}
""".strip()


def extract_json_from_text(text: str) -> dict:
    text = text.strip()
    fenced_pattern = re.compile(r"```json\s*(\[.*?\])\s*```", re.DOTALL | re.IGNORECASE)
    fenced_match = fenced_pattern.search(text)

    if fenced_match:
        json_str = fenced_match.group(1).strip()
    else:
        standalone_pattern = re.compile(r"(\[.*?\])", re.DOTALL)
        standalone_match = standalone_pattern.search(text)

        if standalone_match:
            json_str = standalone_match.group(1).strip()
        else:
            raise ValueError("Invalid JSON format: No JSON found.")

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format: Failed to parse JSON.")

