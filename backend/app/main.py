"""
app/main.py -- InsightX Agentic API (Dual-AI Pipeline).

Pipeline:
  User Question -> Vanna AI (Local ChromaDB + Groq LLM for SQL)
  -> Groq LLM (Executive Summary + Follow-ups)
  -> Unified JSON Response

No external Vanna API key needed -- all training data lives in local ChromaDB.
"""

import json
import os
import tempfile
import sys

# Force UTF-8 stdout so unicode print statements work on Windows terminals
sys.stdout.reconfigure(encoding="utf-8")

import traceback

from app import chat_db

# Add scripts directory to path to import EasyOCRModel
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
sys.path.append(os.path.join(PROJECT_ROOT, "scripts"))

import numpy as np
import pandas as pd
import uvicorn
import whisper  # type: ignore  # Package: openai-whisper
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from groq import Groq
from openai import OpenAI
from pydantic import BaseModel
from vanna.legacy.chromadb.chromadb_vector import ChromaDB_VectorStore
from vanna.legacy.openai.openai_chat import OpenAI_Chat

try:
    from ocr_easyocr import EasyOCRModel
except ImportError:
    print("[!] Could not import EasyOCRModel. Make sure easyocr is installed.")
    EasyOCRModel = None

# -- Path Resolution -----------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, "data", "upi_transactions.db")
VECTOR_STORE_PATH = os.path.join(PROJECT_ROOT, "vector_store")

# -- Load Environment Variables ------------------------------------------------

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not found. Create a .env file in backend/ (see .env.example).")


# -- Vanna AI -- Local ChromaDB + Groq (OpenAI-compatible) ---------------------

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
print(f"[OK] Vanna AI initialized (local ChromaDB: {VECTOR_STORE_PATH})")
print(f"[OK] Connected to SQLite: {DB_PATH}")

# Groq native client for answer synthesis
groq_client = Groq(api_key=GROQ_API_KEY)
print(f"[OK] Groq LLM initialized (model: {GROQ_MODEL})")

# -- Whisper STT Model ---------------------------------------------------------

WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL", "base")
print(f"Loading Whisper '{WHISPER_MODEL_NAME}' model...")
whisper_model = whisper.load_model(WHISPER_MODEL_NAME)
print(f"[OK] Whisper STT initialized (model: {WHISPER_MODEL_NAME})")

# -- OCR Model (EasyOCR) ------------------------------------------------------

print("Loading EasyOCR model...")
try:
    ocr_model = EasyOCRModel(languages=['en'], gpu=False)
    print("[OK] EasyOCR initialized")
except Exception as e:
    print(f"[!] OCR Init Failed: {e}")
    ocr_model = None

# -- Chat History DB -----------------------------------------------------------

chat_db.init_db()
print("[OK] Chat history database initialized")

# -- FastAPI App ---------------------------------------------------------------

app = FastAPI(title="InsightX Agentic API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# -- Pydantic Models -----------------------------------------------------------

class ChatMessage(BaseModel):
    role: str       # "user" | "assistant"
    content: str

class QueryRequest(BaseModel):
    question: str
    chat_history: list[ChatMessage] = []
    session_id: str | None = None


# -- DB Schema (used to ground follow-up question generation) ------------------

DB_SCHEMA = """
Table: transactions
Columns:
  transaction_id TEXT       -- unique ID e.g. TXN0000000001
  timestamp TEXT            -- datetime e.g. 2024-10-08 15:17:28
  transaction_type TEXT     -- P2P | P2M | Bill Payment | Recharge
  merchant_category TEXT    -- Food | Grocery | Shopping | Fuel | Utilities | Entertainment | Healthcare | Transport | Education | Other (NULL for P2P)
  amount_inr INTEGER        -- transaction amount in INR
  transaction_status TEXT   -- SUCCESS | FAILED
  sender_age_group TEXT     -- 18-25 | 26-35 | 36-45 | 46-55 | 56+
  receiver_age_group TEXT   -- same as sender (NULL for non-P2P)
  sender_state TEXT         -- Indian state e.g. Delhi, Maharashtra, Karnataka
  sender_bank TEXT          -- SBI | HDFC | ICICI | Axis | Kotak | PNB | Yes Bank | IndusInd
  receiver_bank TEXT        -- same options as sender_bank
  device_type TEXT          -- Android | iOS | Web
  network_type TEXT         -- 3G | 4G | 5G | WiFi
  fraud_flag INTEGER        -- 0 (not fraud) | 1 (fraud)
  hour_of_day INTEGER       -- 0-23
  day_of_week TEXT          -- Monday - Sunday
  is_weekend INTEGER        -- 0 (weekday) | 1 (weekend)
  day_part TEXT             -- Morning | Afternoon | Evening | Night
  amount_tier TEXT          -- Small (<500) | Medium (500-5000) | Large (5000-50000)
  sender_age_label TEXT     -- Young (18-25) | Adult (26-55) | Old (56+)
  receiver_age_label TEXT   -- Young | Adult | Old (NULL for non-P2P)
"""

# -- Groq Synthesis Prompt -----------------------------------------------------

SYNTHESIS_PROMPT = """You are an elite data analyst for InsightX.
The user asked: "{question}".
The database returned this exact data:
{df_markdown}

--- DATABASE SCHEMA ---
{schema}
--- END SCHEMA ---

Task 1: Write a concise executive summary (2-3 sentences) of the data above.
Highlight the single most important business finding. Use \u20b9 for INR values.

Task 2: Suggest exactly 3 follow-up questions. STRICT RULES:
- Every question MUST be answerable using only the columns and values listed in the schema.
- Reference real column names and real values (e.g. sender_bank = 'HDFC', transaction_type = 'P2P').
- Do NOT invent columns, tables, or data that are not in the schema.
- Questions should be a natural, different-angle continuation of the current analysis.

Return valid JSON with exactly these keys: "answer" (string), "follow_up_questions" (list of 3 strings)."""


# -- Core Endpoint: /api/ask ---------------------------------------------------

@app.post("/api/ask")
async def ask_insightx(request: QueryRequest):
    """
    Full Dual-AI Pipeline:
      Question -> Vanna (SQL + Data) -> Groq (Summary + Follow-ups) -> JSON
    """
    try:
        question = request.question.strip()
        if not question:
            raise HTTPException(status_code=400, detail="Question cannot be empty.")

        # -- Step 0: Intent Guardrail ------------------------------------------
        intent_check = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{
                "role": "user",
                "content": (
                    f"Is this a data or analytics question about UPI transactions or financial data? "
                    f"Reply with exactly one word: YES or NO.\n\nInput: \"{question}\""
                )
            }],
            temperature=0.0,
            max_tokens=5,
        )
        intent = intent_check.choices[0].message.content.strip().upper()

        if not intent.startswith("YES"):
            # Not a data question -- friendly conversational response with history
            history_msgs = [
                {"role": msg.role, "content": msg.content}
                for msg in request.chat_history[-10:]
            ]
            chat_reply = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are InsightX, an AI assistant for UPI transaction analytics. "
                            "You remember everything the user has told you in this conversation. "
                            "If the user sends a greeting or off-topic message, reply briefly and "
                            "guide them to ask a data question. Keep it friendly and concise."
                        ),
                    },
                    *history_msgs,
                    {"role": "user", "content": question},
                ],
                temperature=0.7,
                max_tokens=150,
            )
            reply_text = chat_reply.choices[0].message.content.strip()
            response_payload = {
                "question": question,
                "sql": "",
                "data": [],
                "answer": reply_text,
                "follow_up_questions": [
                    "Show total UPI transaction volume",
                    "Which bank had the most transactions?",
                    "What are the top 5 transactions by amount?",
                ],
            }

            # Save to DB
            if request.session_id:
                try:
                    chat_db.add_message(request.session_id, "user", question)
                    chat_db.add_message(request.session_id, "assistant", reply_text)
                    msgs = chat_db.get_messages(request.session_id)
                    if len(msgs) <= 2:
                        chat_db.auto_title(request.session_id, question)
                except Exception:
                    pass

            return response_payload

        # -- Step A: Vanna AI -- Generate SQL & Execute ------------------------
        generated_sql = vn.generate_sql(question)

        if generated_sql is None or generated_sql.strip() == "":
            generated_sql = "-- Could not generate SQL"

        df = None
        if not generated_sql.startswith("--"):
            try:
                df = vn.run_sql(generated_sql)
            except Exception:
                df = None

        # -- Step B: Data Formatting -------------------------------------------
        if df is None or (isinstance(df, pd.DataFrame) and df.empty):
            df_markdown = "No data found."
            data_dict = []
        else:
            df_markdown = df.to_markdown(index=False)
            data_dict = df.fillna("None").to_dict(orient="records")

        # -- Step C: Groq Synthesis with chat history --------------------------
        prompt = SYNTHESIS_PROMPT.format(
            question=question,
            df_markdown=df_markdown,
            schema=DB_SCHEMA,
        )

        history_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.chat_history[-6:]
        ]

        groq_response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are InsightX, an expert data analyst for UPI transaction data. "
                        "You answer questions about the transactions SQLite database."
                    ),
                },
                *history_messages,
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=1024,
            response_format={"type": "json_object"},
        )

        raw_content = groq_response.choices[0].message.content.strip()

        # -- Step D: Response Parsing ------------------------------------------
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

        # -- Step E: Persist to DB & Return ------------------------------------
        response_payload = {
            "question": question,
            "sql": generated_sql,
            "data": data_dict,
            "answer": answer,
            "follow_up_questions": follow_ups,
        }

        if request.session_id:
            try:
                chat_db.add_message(request.session_id, "user", question)
                chat_db.add_message(
                    session_id=request.session_id,
                    role="assistant",
                    content=answer,
                    sql_text=generated_sql,
                    data_json=json.dumps(response_payload, default=str),
                )
                msgs = chat_db.get_messages(request.session_id)
                if len(msgs) <= 2:
                    chat_db.auto_title(request.session_id, question)
            except Exception:
                pass

        return response_payload

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# -- Speech-to-Text Endpoint --------------------------------------------------

@app.post("/api/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """Accepts audio file upload and returns transcribed text using local Whisper."""
    ALLOWED_TYPES = {
        "audio/wav", "audio/x-wav", "audio/wave",
        "audio/webm", "audio/ogg", "audio/mpeg", "audio/mp3",
        "audio/mp4", "audio/x-m4a", "audio/aac",
        "video/webm",
    }

    if audio.content_type and audio.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio type: {audio.content_type}. Accepted: wav, webm, mp3, ogg, m4a.",
        )

    try:
        suffix = ".webm"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contents = await audio.read()
            tmp.write(contents)
            tmp_path = tmp.name

        result = whisper_model.transcribe(tmp_path)
        transcription = result["text"].strip()
        os.unlink(tmp_path)

        return {"transcription": transcription}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@app.post("/api/voice-ask")
async def voice_ask(audio: UploadFile = File(...)):
    """Combined: Transcribe audio -> run full Dual-AI Pipeline."""
    transcription_response = await transcribe_audio(audio)
    transcription = transcription_response["transcription"]

    if not transcription:
        raise HTTPException(status_code=400, detail="Could not transcribe any speech from the audio.")

    pipeline_result = await ask_insightx(QueryRequest(question=transcription))
    pipeline_result["transcription"] = transcription
    return pipeline_result


# -- OCR / Image Endpoint -----------------------------------------------------

@app.post("/api/ocr-ask")
async def ocr_ask(
    image: UploadFile = File(...),
    text: Optional[str] = Form(None)
):
    """Accepts image + optional text -> OCR -> Groq interpretation -> Vanna Pipeline."""
    if ocr_model is None:
        raise HTTPException(status_code=503, detail="OCR service is not available.")

    ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp"}
    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported image type: {image.content_type}")

    try:
        suffix = os.path.splitext(image.filename)[1] or ".jpg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contents = await image.read()
            tmp.write(contents)
            tmp_path = tmp.name

        print(f"Running OCR on {tmp_path}...")
        extracted_text = ocr_model.extract_text(tmp_path)
        os.unlink(tmp_path)

        if not extracted_text or len(extracted_text.strip()) < 5:
            raise HTTPException(status_code=400, detail="No readable text found in the image.")

        print(f"OCR Extracted: {extracted_text[:100]}...")

        base_prompt = (
            f"I have extracted the following text from an image (chart, report, or screenshot):\n"
            f"\"\"\"{extracted_text}\"\"\"\n"
        )

        if text and text.strip():
            base_prompt += f"\nThe user also provided this specific note/question: \"{text}\"\n"
            task_instruction = (
                "Task: Combine the image text and the user's note to formulate a single, clear, "
                "and specific business question that can be answered by querying the 'upi_transactions' database.\n"
                "Prioritize the user's note if it refines the context."
            )
        else:
            task_instruction = (
                "Task: Based on this text, formulate a single, clear, and specific business question "
                "that can be answered by querying the 'upi_transactions' database."
            )

        interpretation_prompt = f"{base_prompt}\n{task_instruction}\nReturn ONLY the question, nothing else."

        groq_resp = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": interpretation_prompt}],
            temperature=0.3,
            max_tokens=100,
        )
        formulated_question = groq_resp.choices[0].message.content.strip()
        print(f"Formulated Question: {formulated_question}")

        pipeline_result = await ask_insightx(QueryRequest(question=formulated_question))
        pipeline_result["ocr_text"] = extracted_text
        pipeline_result["original_question"] = formulated_question

        return pipeline_result

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"OCR pipeline failed: {str(e)}")


# -- Session CRUD Endpoints ----------------------------------------------------

@app.get("/api/sessions")
async def list_sessions():
    """List all chat sessions, newest first."""
    return chat_db.list_sessions()

@app.post("/api/sessions")
async def create_session():
    """Create a new chat session."""
    return chat_db.create_session()

@app.get("/api/sessions/{session_id}/messages")
async def get_session_messages(session_id: str):
    """Get all messages for a session."""
    return chat_db.get_messages(session_id)

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a chat session and all its messages."""
    deleted = chat_db.delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"ok": True}


# -- Health Check --------------------------------------------------------------

@app.get("/")
async def health_check():
    return {"status": "ok", "service": "InsightX Agentic API"}


# -- Run -----------------------------------------------------------------------

if __name__ == "__main__":
    print("[OK] Starting InsightX Agentic API on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
