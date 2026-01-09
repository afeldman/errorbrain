from decouple import config

LLM_ENABLED = config("ERRORBRAIN_REASONING_MODE", default="rules") == "llm"

LLM_KEY = config("LLM_KEY", default=None)
LLM_HOST = config("LLM_HOST", default="http://localhost:1234/v1")
LLM_MODEL = config("LLM_MODEL", default="openai/gpt-oss-20b")
