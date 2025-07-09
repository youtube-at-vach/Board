# llm_api.py

import random
import os
from openai import OpenAI
import google.generativeai as genai
from utils import debug_print # Import debug_print from utils.py

debug_print("Loading llm_api.py (real OpenAI and Gemini APIs)")

# Mapping for response length to max_tokens and prompt instruction
RESPONSE_LENGTH_SETTINGS = {
    "short": {"max_tokens": 50, "instruction": "簡潔に、2〜3文で回答してください。"},
    "medium": {"max_tokens": 150, "instruction": "要点をまとめて、5〜7文で回答してください。"},
    "long": {"max_tokens": 300, "instruction": "詳細に、具体的な例を交えて回答してください。"},
}

# --- OpenAI API Implementation ---
class OpenAIAPI:
    def __init__(self):
        debug_print("OpenAIAPI __init__ called")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        self.client = OpenAI(api_key=api_key)

    def generate(self, prompt, model_name, response_length="medium"):
        settings = RESPONSE_LENGTH_SETTINGS.get(response_length, RESPONSE_LENGTH_SETTINGS["medium"])
        instruction = settings["instruction"]
        max_tokens = settings["max_tokens"]

        full_prompt = f"{prompt}\n\n{instruction}"

        debug_print(f"OpenAIAPI generate called with model '{model_name}', length '{response_length}' and prompt: {full_prompt[:100]}...")
        try:
            chat_completion = self.client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=max_tokens
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            debug_print(f"Error calling OpenAI API: {e}")
            return f"[OpenAI API Error]: {e}"

# --- Mock API Implementations (for DeepSeek) ---
class DeepSeekAPI:
    def __init__(self):
        debug_print("DeepSeekAPI __init__ called (mock)")

    def generate(self, prompt, model_name, response_length="medium"):
        settings = RESPONSE_LENGTH_SETTINGS.get(response_length, RESPONSE_LENGTH_SETTINGS["medium"])
        instruction = settings["instruction"]
        
        return f"[DeepSeek Mock Response]: {random.choice(['なるほど、それは考慮すべき点ですね。', '私の知る限りでは、そのデータは正確ではありません。', 'より詳細な分析が必要です。', 'その提案は現実的ではありません。'])} (Model: {model_name}, Length: {response_length}, Prompt: {prompt[:50]}...)"

class GeminiAPI:
    def __init__(self):
        debug_print("GeminiAPI __init__ called")
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        genai.configure(api_key=api_key)

    def generate(self, prompt, model_name, response_length="medium"):
        settings = RESPONSE_LENGTH_SETTINGS.get(response_length, RESPONSE_LENGTH_SETTINGS["medium"])
        instruction = settings["instruction"]
        max_tokens = settings["max_tokens"]

        full_prompt = f"{prompt}\n\n{instruction}"

        debug_print(f"GeminiAPI generate called with model '{model_name}', length '{response_length}' and prompt: {full_prompt[:100]}...")
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(full_prompt)
            # Gemini API does not have a direct max_tokens parameter for generate_content
            # We will rely on the prompt instruction for conciseness.
            return response.text
        except Exception as e:
            debug_print(f"Error calling Gemini API: {e}")
            return f"[Gemini API Error]: {e}"

API_CLIENTS = {
    "openai": OpenAIAPI(),
    "deepseek": DeepSeekAPI(),
    "gemini": GeminiAPI(),
}

LLM_API_MAP = {}

def initialize_llm_api_map(models_config):
    global LLM_API_MAP
    for model_name, details in models_config['models'].items():
        api_type = details['api']
        LLM_API_MAP[model_name] = {
            "client": API_CLIENTS[api_type],
            "model_name_for_api": details['name']
        }
    debug_print("LLM_API_MAP initialized:", LLM_API_MAP.keys())