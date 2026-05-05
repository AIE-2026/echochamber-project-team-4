"""
EchoChamber Studio — app.py
===========================
A simulation of discursive bubbles using Romanian political comments.
Each "agent" responds from the perspective of its own political community.

This file is intentionally kept simple and well-commented.
Sociology students: you don't need to understand every line —
focus on the functions that interest you and modify them freely.

Structure:
  1. IMPORTS & SETUP
  2. DESIGN CONSTANTS  (colors, fonts, HTML templates)
  3. HELPER FUNCTIONS  (fetch article, neutral summary, etc.)
  4. TAB 1 — Agents   (all agents respond to same stimulus)
  5. TAB 2 — News     (load article → summarize → chat)
  6. TAB 3 — Debate   (agentic thread with LLM router)
  7. BUILD UI          (assemble the Gradio interface)
  8. LAUNCH
"""

# ─────────────────────────────────────────────────────────────────────────────
# 1. IMPORTS & SETUP
# ─────────────────────────────────────────────────────────────────────────────
import os
import sys
import json
from pathlib import Path
 
import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI
from openai import RateLimitError, APIError, AuthenticationError
 
 # Allow app/app.py to import from core/
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
 
 
# Team configuration selected after C2
from core.config import (
    PROVIDER_PRINCIPAL,
    MODEL_PRINCIPAL,
    PROVIDER_FALLBACK,
    MODEL_FALLBACK,
    TEMPERATURE,
)

# ==================================================
# 2. PROVIDERS AND API KEYS
# ==================================================
 
# Configurăm providerii și cheile API din fișierul .env
 
load_dotenv(PROJECT_ROOT / ".env")
 
BASE_URLS = {
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/",
    "openrouter": "https://openrouter.ai/api/v1"
}
 
API_KEYS = {
    "gemini": os.getenv("GEMINI_API_KEY"),
    "openrouter": os.getenv("OPENROUTER_API_KEY")
}
 
 
def make_client(provider):
    """Creează clientul API pentru providerul ales."""
    return OpenAI(
        api_key=API_KEYS[provider],
        base_url=BASE_URLS[provider]
    )
 
 # ==================================================
# 3. MODEL CALL
# ==================================================
 
def ask(provider, model, prompt, system=None, temperature=0.7, json_schema=None):
    """Trimite un prompt la model. Poate returna text simplu sau JSON structurat."""
 
    client = make_client(provider)
 
    messages = []
 
    if system:
        messages.append({"role": "system", "content": system})
 
    messages.append({"role": "user", "content": prompt})
 
    extra_args = {}
 
    if json_schema:
        extra_args["response_format"] = {
            "type": "json_schema",
            "json_schema": json_schema
        }
 
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            **extra_args
        )
 
        text = response.choices[0].message.content.strip()
 
        if json_schema:
            return json.loads(text)
 
        return text
 
    except RateLimitError:
        return f"[Eroare: quota/rate limit pentru modelul {model}.]"
 
    except AuthenticationError:
        return "[Eroare: API key invalidă sau lipsă. Verifică .env.]"
 
    except APIError as e:
        return f"[Eroare API: {e}]"
 
    except Exception as e:
        return f"[Eroare: {type(e).__name__} — {e}]"
 

 # ==================================================
# 4. APP LOGIC
# ==================================================
 
def chat(prompt):
    """Trimite promptul la modelul principal. Dacă apare eroare, încearcă fallback-ul."""
 
    if not prompt.strip():
        return "Scrie un prompt mai întâi."
 
    answer = ask(
        provider=PROVIDER_PRINCIPAL,
        model=MODEL_PRINCIPAL,
        prompt=prompt,
        temperature=TEMPERATURE
    )
 
    if isinstance(answer, str) and answer.startswith("[Eroare"):
        answer = ask(
            provider=PROVIDER_FALLBACK,
            model=MODEL_FALLBACK,
            prompt=prompt,
            temperature=TEMPERATURE
        )
 
    return answer

 
# ==================================================
# 6. GRADIO UI
# ==================================================
 
demo = gr.Interface(
    fn=chat,
    inputs=gr.Textbox(
        label="Prompt",
        value="Explică în 2 propoziții ce este un LLM.",
        lines=4
    ),
    outputs=gr.Textbox(
        label="Răspuns",
        lines=8
    ),
    title="EchoChamber — Minimal C2 App",
    description=(
        "Trimite un prompt la modelul ales de echipă. "
        "Dacă modelul principal eșuează, aplicația folosește fallback-ul."
    )
)
 
 


 
# ==================================================
# 7. LAUNCH
# ==================================================
 
if __name__ == "__main__":
    demo.launch()
 
"""
EchoChamber — Minimal C2 App
---------------------------
 
First Gradio app for the project.
 
It uses the same make_client() and ask() logic from the C2 notebook.
The app:
- reads API keys from .env
- reads the team model choice from core/config.py
- sends one prompt to the main model
- uses the fallback model if the main model fails
"""
 
# ==================================================
# 1. IMPORTS AND PROJECT SETUP
# ==================================================
 
import os
import sys
import json
from pathlib import Path
 
import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI
from openai import RateLimitError, APIError, AuthenticationError
 
 
# Allow app/app.py to import from core/
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))
 
 
# Team configuration selected after C2
from core.config import (
    PROVIDER_PRINCIPAL,
    MODEL_PRINCIPAL,
    PROVIDER_FALLBACK,
    MODEL_FALLBACK,
    TEMPERATURE,
)
 
 
# ==================================================
# 2. PROVIDERS AND API KEYS
# ==================================================
 
# Configurăm providerii și cheile API din fișierul .env
 
load_dotenv(PROJECT_ROOT / ".env")
 
BASE_URLS = {
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/",
    "openrouter": "https://openrouter.ai/api/v1"
}
 
API_KEYS = {
    "gemini": os.getenv("GEMINI_API_KEY"),
    "openrouter": os.getenv("OPENROUTER_API_KEY")
}
 
 
def make_client(provider):
    """Creează clientul API pentru providerul ales."""
    return OpenAI(
        api_key=API_KEYS[provider],
        base_url=BASE_URLS[provider]
    )
 
 
# ==================================================
# 3. MODEL CALL
# ==================================================
 
def ask(provider, model, prompt, system=None, temperature=0.7, json_schema=None):
    """Trimite un prompt la model. Poate returna text simplu sau JSON structurat."""
 
    client = make_client(provider)
 
    messages = []
 
    if system:
        messages.append({"role": "system", "content": system})
 
    messages.append({"role": "user", "content": prompt})
 
    extra_args = {}
 
    if json_schema:
        extra_args["response_format"] = {
            "type": "json_schema",
            "json_schema": json_schema
        }
 
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            **extra_args
        )
 
        text = response.choices[0].message.content.strip()
 
        if json_schema:
            return json.loads(text)
 
        return text
 
    except RateLimitError:
        return f"[Eroare: quota/rate limit pentru modelul {model}.]"
 
    except AuthenticationError:
        return "[Eroare: API key invalidă sau lipsă. Verifică .env.]"
 
    except APIError as e:
        return f"[Eroare API: {e}]"
 
    except Exception as e:
        return f"[Eroare: {type(e).__name__} — {e}]"
 
 
# ==================================================
# 4. APP LOGIC
# ==================================================
 
def chat(prompt):
    """Trimite promptul la modelul principal. Dacă apare eroare, încearcă fallback-ul."""
 
    if not prompt.strip():
        return "Scrie un prompt mai întâi."
 
    answer = ask(
        provider=PROVIDER_PRINCIPAL,
        model=MODEL_PRINCIPAL,
        prompt=prompt,
        temperature=TEMPERATURE
    )
 
    if isinstance(answer, str) and answer.startswith("[Eroare"):
        answer = ask(
            provider=PROVIDER_FALLBACK,
            model=MODEL_FALLBACK,
            prompt=prompt,
            temperature=TEMPERATURE
        )
 
    return answer
 
 
# ==================================================
# 5. TODO FOR NEXT COURSES
# ==================================================
 
# TODO C3:
# Load comments or articles from data/raw/ and data/cleaned/.
 
# TODO C4:
# Add political comment annotation with structured output.
 
# TODO C5:
# Add retrieval / RAG over the collected corpus.
 
# TODO C6:
# Add agents with different discursive roles.
 
# TODO C7:
# Add multi-agent debate or simulation.
 
 
# ==================================================
# 6. GRADIO UI
# ==================================================
 
demo = gr.Interface(
    fn=chat,
    inputs=gr.Textbox(
        label="Prompt",
        value="Explică în 2 propoziții ce este un LLM.",
        lines=4
    ),
    outputs=gr.Textbox(
        label="Răspuns",
        lines=8
    ),
    title="EchoChamber — Minimal C2 App",
    description=(
        "Trimite un prompt la modelul ales de echipă. "
        "Dacă modelul principal eșuează, aplicația folosește fallback-ul."
    )
)
 
 
# ==================================================
# 7. LAUNCH
# ==================================================
 
if __name__ == "__main__":
    demo.launch()
 