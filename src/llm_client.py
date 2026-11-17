"""LLM wrapper with free-tier rate-limit throttling for Gemini."""
import os
import time
from pathlib import Path
import yaml
from dotenv import load_dotenv
import streamlit as st

load_dotenv()
CONFIG = yaml.safe_load(Path("configs/model_config.yaml").read_text())

_GEMINI_MIN_INTERVAL = 60.0 / 13.0
_last_gemini_call = 0.0

def load_prompt(version: str, stage: str = None) -> str:
    path = Path(f"prompts/{version}_{stage}.txt") if stage else Path(f"prompts/{version}.txt")
    return path.read_text()

def call_llm(prompt: str, expect_json: bool = False, retries: int = 5) -> str:
    global _last_gemini_call
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
                    model=CONFIG["model_name"], max_tokens=CONFIG["max_tokens"],
                    temperature=CONFIG["temperature"],
                    messages=[{"role": "user", "content": prompt}],
                )
                return resp.content[0].text
            elif provider == "google":
                elapsed = time.time() - _last_gemini_call
                if elapsed < _GEMINI_MIN_INTERVAL:
                    time.sleep(_GEMINI_MIN_INTERVAL - elapsed)
                import google.generativeai as genai
                
                # Try env first, then streamlit secrets
                api_key = os.getenv("GOOGLE_API_KEY")
                if not api_key:
                    try:
                        api_key = st.secrets["GOOGLE_API_KEY"]
                    except Exception:
                        pass
                
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(CONFIG["model_name"])
                resp = model.generate_content(
                    prompt,
                    generation_config={"temperature": CONFIG["temperature"], "max_output_tokens": CONFIG["max_tokens"]},
                )
                _last_gemini_call = time.time()
                return resp.text
            else:
                raise ValueError(f"Unknown provider: {provider}")
        except Exception as e:
            err_str = str(e).lower()
            is_quota = "429" in str(e) or "resourceexhausted" in err_str or "quota" in err_str
            if is_quota and attempt < retries - 1:
                wait = 30 + (attempt * 15)
                print(f"[rate limit] waiting {wait}s before retry {attempt+1}/{retries}")
                time.sleep(wait)
                continue
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)
    return ""
