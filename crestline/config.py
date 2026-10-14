import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DIMENSIONS = 384


def database_url():
    return os.getenv("DATABASE_URL", "postgresql:///crestline?host=/tmp/crestline-socket&user=app")


def gemini_model():
    return os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
