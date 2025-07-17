# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
OPENAI_PROJECT_ID = os.getenv("OPENAI_PROJECT_ID")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# Model Configuration
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "openai")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")

# Google Cloud Storage
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME","your-default-name")
# Make sure GOOGLE_APPLICATION_CREDENTIALS is set in your environment

# Redis and Celery
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")