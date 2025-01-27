import os
from dotenv import load_dotenv



load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")
OPEN_AI_TOKEN = os.getenv("OPEN_AI_TOKEN")


DATABASE_PATH = "database.db"
LLM_ID = "gpt-4o"