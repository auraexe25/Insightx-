"""
app/main.py — InsightX Agentic API (Dual-AI Pipeline).

Pipeline:
  User Question → Vanna AI (Local ChromaDB + Groq LLM for SQL)
  → Groq LLM (Executive Summary + Follow-ups)
  → Unified JSON Response

No external Vanna API key needed — all training data lives in local ChromaDB.
"""

import json
import os
import traceback

import pandas as pd
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from openai import OpenAI
from pydantic import BaseModel
from vanna.legacy.chromadb.chromadb_vector import ChromaDB_VectorStore
from vanna.legacy.openai.openai_chat import OpenAI_Chat

# ── Path Resolution ──────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, "data", "upi_transactions.db")
VECTOR_STORE_PATH = os.path.join(PROJECT_ROOT, "vector_store")

# ── Load Environment Variables ───────────────────────────────────────────────

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not found. Create a .env file in backend/ (see .env.example).")


# ── Vanna AI — Local ChromaDB + Groq (OpenAI-compatible) ────────────────────

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, client=None, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, client=client, config=config)


# Groq as OpenAI-compatible client for Vanna's SQL generation
vanna_client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

vn = MyVanna(client=vanna_client, config={
    "model": GROQ_MODEL,
    "path": VECTOR_STORE_PATH,
})
vn.connect_to_sqlite(DB_PATH)
print(f"[✓] Vanna AI initialized (local ChromaDB: {VECTOR_STORE_PATH})")
print(f"[✓] Connected to SQLite: {DB_PATH}")

# Groq native client for answer synthesis
groq_client = Groq(api_key=GROQ_API_KEY)
print(f"[✓] Groq LLM initialized (model: {GROQ_MODEL})")


# ── FastAPI App ──────────────────────────────────────────────────────────────

app = FastAPI(title="InsightX Agentic API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Pydantic Models ──────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    question: str


# ── Groq Synthesis Prompt ────────────────────────────────────────────────────

SYNTHESIS_PROMPT = """You are an elite data analyst for InsightX. \
The user asked: "{question}". \
The database returned this exact data:
{df_markdown}

Task 1: Write a concise, highly professional executive summary (2-3 sentences) of this data. \
Highlight the most important business finding. Format it beautifully. \
Include rupee symbols (₹) for currency.
Task 2: Suggest exactly 3 logical follow-up questions to dig deeper.

You MUST return your response as a valid JSON object. \
Use exactly these keys: "answer" (string) and "follow_up_questions" (list of strings)."""


# ── Core Endpoint ────────────────────────────────────────────────────────────

@app.post("/api/ask")
async def ask_insightx(request: QueryRequest):
    """
    Full Dual-AI Pipeline:
      Question → Vanna (SQL + Data via local ChromaDB) → Groq (Summary + Follow-ups) → JSON
    """
    try:
        question = request.question.strip()
        if not question:
            raise HTTPException(status_code=400, detail="Question cannot be empty.")

        # ── Step A: Vanna AI — Generate SQL & Execute ────────────────────────
        generated_sql = vn.generate_sql(question)

        if generated_sql is None or generated_sql.strip() == "":
            generated_sql = "-- Could not generate SQL"

        df = None
        if not generated_sql.startswith("--"):
            try:
                df = vn.run_sql(generated_sql)
            except Exception:
                df = None

        # ── Step B: Data Formatting ──────────────────────────────────────────
        if df is None or (isinstance(df, pd.DataFrame) and df.empty):
            df_markdown = "No data found."
            data_dict = []
        else:
            df_markdown = df.to_markdown(index=False)
            data_dict = df.fillna("None").to_dict(orient="records")

        # ── Step C + D: Groq Synthesis ───────────────────────────────────────
        prompt = SYNTHESIS_PROMPT.format(
            question=question,
            df_markdown=df_markdown,
        )

        groq_response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=1024,
            response_format={"type": "json_object"},
        )

        raw_content = groq_response.choices[0].message.content.strip()

        # ── Step E: Response Parsing ─────────────────────────────────────────
        try:
            llm_result = json.loads(raw_content)
        except json.JSONDecodeError:
            llm_result = {
                "answer": raw_content,
                "follow_up_questions": [
                    "Can you break this down by transaction type?",
                    "What does the trend look like over time?",
                    "Are there any anomalies in this data?",
                ],
            }

        answer = llm_result.get("answer", raw_content)
        follow_ups = llm_result.get("follow_up_questions", [])[:3]

        # ── Step F: Final Return ─────────────────────────────────────────────
        return {
            "question": question,
            "sql": generated_sql,
            "data": data_dict,
            "answer": answer,
            "follow_up_questions": follow_ups,
        }

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ── Health Check ─────────────────────────────────────────────────────────────

@app.get("/")
async def health_check():
    return {"status": "ok", "service": "InsightX Agentic API"}


# ── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("[✓] Starting InsightX Agentic API on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
