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

from dotenv import load_dotenv

load_dotenv()

# MODEL_NAME = "qwen3:8b"
EMBEDDINGS_MODEL = "bge-m3:latest"
EMBEDDINGS_ENDPOINT = "http://localhost:11434/api/embed"
MODEL_ENDPOINT = (
    "http://localhost:11434/api/chat"
)
SYSTEM_PROMPT = ""
AZURE_ENDPOINT = "https://ai-academy-foundry.services.ai.azure.com/openai/v1"
MODEL_NAME = "gpt-5-mini"
API_KEY = os.getenv("API_KEY")