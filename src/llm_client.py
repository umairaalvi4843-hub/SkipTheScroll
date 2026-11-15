"""Single wrapper for LLM calls. Update provider section for your API."""
import os
import json
import time
from pathlib import Path
import yaml
from dotenv import load_dotenv

load_dotenv()

CONFIG = yaml.safe_load(Path("configs/model_config.yaml").read_text())

def load_prompt(version: str, stage: str = None) -> str:
    if stage:
        path = Path(f"prompts/{version}_{stage}.txt")
    else:
        path = Path(f"prompts/{version}.txt")
    return path.read_text()

def call_llm(prompt: str, expect_json: bool = False, retries: int = 3) -> str:
    provider = CONFIG["provider"]
    for attempt in range(retries):
        try:
            if provider == "openai":
                from openai import OpenAI
                client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                kwargs = {
                    "model": CONFIG["model_name"],
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": CONFIG["temperature"],
                    "top_p": CONFIG["top_p"],
                    "max_tokens": CONFIG["max_tokens"],
                }
                if expect_json:
                    kwargs["response_format"] = {"type": "json_object"}
                resp = client.chat.completions.create(**kwargs)
                return resp.choices[0].message.content
            elif provider == "anthropic":
                import anthropic
                client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
                resp = client.messages.create(
                    model=CONFIG["model_name"],
                    max_tokens=CONFIG["max_tokens"],
                    temperature=CONFIG["temperature"],
                    messages=[{"role": "user", "content": prompt}],
                )
                return resp.content[0].text
            elif provider == "google":
                import google.generativeai as genai
                genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                model = genai.GenerativeModel(CONFIG["model_name"])
                resp = model.generate_content(
                    prompt,
                    generation_config={"temperature": CONFIG["temperature"], "max_output_tokens": CONFIG["max_tokens"]},
                )
                return resp.text
            else:
                raise ValueError(f"Unknown provider: {provider}")
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)
    return ""
