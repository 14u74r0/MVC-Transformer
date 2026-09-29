import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
VIEWS_DIR = BASE_DIR / "views"


MODEL_ID = os.getenv("VISION_MODEL_ID", "HuggingFaceTB/SmolVLM-500M-Instruct")

MAX_NEW_TOKENS = int(os.getenv("VISION_MAX_TOKENS", "200"))
MAX_UPLOAD_MB = 10
MAX_IMAGE_SIDE = 1024      
MAX_QUESTION_CHARS = 300

PROMPT_DESCRIBE = "Describe this image in detail."

HOST = os.getenv("VISION_HOST", "127.0.0.1")
PORT = int(os.getenv("VISION_PORT", "8000"))
