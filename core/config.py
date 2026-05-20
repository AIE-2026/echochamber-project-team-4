# core/config.py
# ===============
# Central configuration: loads roles.yaml and .env API keys.
# All other modules import from here instead of reading files directly.
#
# Students: you don't need to modify this file.
# If you want to add a new LLM provider, add it to AVAILABLE_MODELS below.

PROVIDER_PRINCIPAL = "gemini"

MODEL_PRINCIPAL = "gemini-2.5-flash"

PROVIDER_FALLBACK = "gemini"

MODEL_FALLBACK = "gemini-2.5-flash-lite"

TEMPERATURE = 0.7