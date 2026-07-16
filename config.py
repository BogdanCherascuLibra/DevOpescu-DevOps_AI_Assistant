"""
Application configuration.

This module contains all configurable settings used by the AI agent.

Future exercises may extend this file with:
- Model configuration
- API credentials
- Prompt templates
- Embedding settings
- Logging configuration
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent


# MODEL_NAME = "qwen3:8b"
EMBEDDINGS_MODEL = "bge-m3:latest"
EMBEDDINGS_ENDPOINT = "http://localhost:11434/api/embed"
EMBEDDINGS_FILE = BASE_DIR / "data" / "embeddings.json"

CHUNK_SIZE = 100
SEMANTIC_SEARCH_FIRST_N = 3
SEMANTIC_SEARCH_MIN_SIMILARITY = 0.45

INPUT_TOKEN_PRICE_PER_MILLION = 2.0
OUTPUT_TOKEN_PRICE_PER_MILLION = 10.0

MODEL_ENDPOINT = ("http://localhost:11434/api/chat")
SYSTEM_PROMPT = ""
AZURE_ENDPOINT = "https://ai-academy-foundry.services.ai.azure.com/openai/v1"
MODEL_NAME = "gpt-5-mini"
API_KEY = os.getenv("API_KEY")