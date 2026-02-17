"""
demo_vanna.py — Demo: Ask Vanna a natural language question and get SQL + results.
"""

import os
import time
from pathlib import Path

from dotenv import load_dotenv

from vanna.legacy.chromadb.chromadb_vector import ChromaDB_VectorStore
from vanna.legacy.openai.openai_chat import OpenAI_Chat

# ── Path resolution (always relative to backend root) ────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = str(PROJECT_ROOT / "data" / "upi_transactions.db")
VECTOR_STORE_PATH = str(PROJECT_ROOT / "vector_store")

# ── Load environment variables ────────────────────────────────────────────────
load_dotenv(PROJECT_ROOT / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not found. Create a .env file in backend/ (see .env.example).")


class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, client=None, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, client=client, config=config)


# Initialize with Groq (OpenAI-compatible API)
from openai import OpenAI

groq_client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

vn = MyVanna(client=groq_client, config={
    "model": GROQ_MODEL,
    "path": VECTOR_STORE_PATH,
})

vn.connect_to_sqlite(DB_PATH)

# === ASK VANNA ===
question = "In the July month give me the top 5 transactions by amount by an adult in weekend"

print("=" * 60)
print(f"  QUESTION: {question}")
print("=" * 60)

# Step 1: Generate SQL (with retry for rate limits)
sql = None
for attempt in range(3):
    try:
        sql = vn.generate_sql(question)
        break
    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower() or "rate" in str(e).lower():
            wait = 60 * (attempt + 1)
            print(f"  [Rate limited] Retrying in {wait}s... (attempt {attempt + 1}/3)")
            time.sleep(wait)
        else:
            raise e

if sql is None:
    print("  ERROR: Could not generate SQL after 3 attempts. Try again later.")
    exit(1)

print(f"\n  GENERATED SQL:\n  {sql}\n")

# Step 2: Execute the SQL
print("-" * 60)
try:
    df = vn.run_sql(sql)
    print("  RESULTS:")
    print(df.to_string(index=False))
except Exception as e:
    print(f"  ERROR executing SQL: {e}")

print("=" * 60)
