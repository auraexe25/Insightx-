"""
app/main.py â€” InsightX Agentic API (Dual-AI Pipeline).

Pipeline:
  User Question â†’ Vanna AI (Local ChromaDB + Groq LLM for SQL)
  â†’ Groq LLM (Executive Summary + Follow-ups)
  â†’ Unified JSON Response

No external Vanna API key needed â€” all training data lives in local ChromaDB.
"""

import json
import os
import tempfile
import sys

# Force UTF-8 stdout so unicode print statements work on Windows terminals
sys.stdout.reconfigure(encoding="utf-8")

import traceback

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

# â”€â”€ Path Resolution â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, "data", "upi_transactions.db")
VECTOR_STORE_PATH = os.path.join(PROJECT_ROOT, "vector_store")

# â”€â”€ Load Environment Variables â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not found. Create a .env file in backend/ (see .env.example).")


# â”€â”€ Vanna AI â€” Local ChromaDB + Groq (OpenAI-compatible) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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
print(f"[âœ“] Vanna AI initialized (local ChromaDB: {VECTOR_STORE_PATH})")
print(f"[âœ“] Connected to SQLite: {DB_PATH}")

# Groq native client for answer synthesis
groq_client = Groq(api_key=GROQ_API_KEY)
print(f"[âœ“] Groq LLM initialized (model: {GROQ_MODEL})")

# â”€â”€ Whisper STT Model â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL", "base")
print(f"Loading Whisper '{WHISPER_MODEL_NAME}' model...")
whisper_model = whisper.load_model(WHISPER_MODEL_NAME)
print(f"[âœ“] Whisper STT initialized (model: {WHISPER_MODEL_NAME})")

# â”€â”€ OCR Model (EasyOCR) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

print("Loading EasyOCR model...")
try:
    ocr_model = EasyOCRModel(languages=['en'], gpu=False)  # CPU by default for safety
    print("[âœ“] EasyOCR initialized")
except Exception as e:
    print(f"[!] OCR Init Failed: {e}")
    ocr_model = None


# â”€â”€ FastAPI App â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

app = FastAPI(title="InsightX Agentic API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# â”€â”€ Pydantic Models â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class QueryRequest(BaseModel):
    question: str


# â”€â”€ Groq Synthesis Prompt â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

SYNTHESIS_PROMPT = """You are an elite data analyst for InsightX. \
The user asked: "{question}". \
The database returned this exact data:
{df_markdown}

Task 1: Write a concise, highly professional executive summary (2-3 sentences) of this data. \
Highlight the most important business finding. Format it beautifully. \
Include rupee symbols (â‚¹) for currency.
Task 2: Suggest exactly 3 logical follow-up questions to dig deeper.

You MUST return your response as a valid JSON object. \
Use exactly these keys: "answer" (string) and "follow_up_questions" (list of strings)."""


# â”€â”€ Core Endpoint â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.post("/api/ask")
async def ask_insightx(request: QueryRequest):
    """
    Full Dual-AI Pipeline:
      Question â†’ Vanna (SQL + Data via local ChromaDB) â†’ Groq (Summary + Follow-ups) â†’ JSON
    """
    try:
        question = request.question.strip()
        if not question:
            raise HTTPException(status_code=400, detail="Question cannot be empty.")

        # â”€â”€ Step A: Vanna AI â€” Generate SQL & Execute â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        generated_sql = vn.generate_sql(question)

        if generated_sql is None or generated_sql.strip() == "":
            generated_sql = "-- Could not generate SQL"

        df = None
        if not generated_sql.startswith("--"):
            try:
                df = vn.run_sql(generated_sql)
            except Exception:
                df = None

        # â”€â”€ Step B: Data Formatting â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        if df is None or (isinstance(df, pd.DataFrame) and df.empty):
            df_markdown = "No data found."
            data_dict = []
        else:
            df_markdown = df.to_markdown(index=False)
            data_dict = df.fillna("None").to_dict(orient="records")

        # â”€â”€ Step C + D: Groq Synthesis â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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

        # â”€â”€ Step E: Response Parsing â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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

        # â”€â”€ Step F: Final Return â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
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


# â”€â”€ Speech-to-Text Endpoint â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.post("/api/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """
    Accepts an audio file upload (wav, webm, mp3, ogg, m4a) and returns
    the transcribed text using local Whisper.
    """
    ALLOWED_TYPES = {
        "audio/wav", "audio/x-wav", "audio/wave",
        "audio/webm", "audio/ogg", "audio/mpeg", "audio/mp3",
        "audio/mp4", "audio/x-m4a", "audio/aac",
        "video/webm",  # browsers often send webm as video/webm
    }

    if audio.content_type and audio.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio type: {audio.content_type}. "
                   f"Accepted: wav, webm, mp3, ogg, m4a.",
        )

    try:
        # Save uploaded audio to a temp file (Whisper needs a file path)
        suffix = ".webm"  # safe default; Whisper/ffmpeg auto-detects format
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contents = await audio.read()
            tmp.write(contents)
            tmp_path = tmp.name

        # Transcribe
        result = whisper_model.transcribe(tmp_path)
        transcription = result["text"].strip()

        # Cleanup
        os.unlink(tmp_path)

        return {"transcription": transcription}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@app.post("/api/voice-ask")
async def voice_ask(audio: UploadFile = File(...)):
    """
    Combined endpoint: Transcribe audio â†’ run the full Dual-AI Pipeline.
    Returns transcription + executive summary + follow-ups in one request.
    """
    # Step 1: Transcribe
    transcription_response = await transcribe_audio(audio)
    transcription = transcription_response["transcription"]

    if not transcription:
        raise HTTPException(status_code=400, detail="Could not transcribe any speech from the audio.")

    # Step 2: Run through the existing pipeline
    pipeline_result = await ask_insightx(QueryRequest(question=transcription))

    # Step 3: Return combined response
    pipeline_result["transcription"] = transcription
    return pipeline_result


# â”€â”€ OCR / Image Endpoint â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.post("/api/ocr-ask")
async def ocr_ask(
    image: UploadFile = File(...),
    text: Optional[str] = Form(None)
):
    """
    Accepts an image upload + optional text â†’ Extracts text (OCR) â†’ Formulates Question (Groq)
    â†’ Runs Vanna Pipeline.
    """
    if ocr_model is None:
        raise HTTPException(status_code=503, detail="OCR service is not available.")

    ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp"}
    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported image type: {image.content_type}")

    try:
        # 1. Save temp file
        suffix = os.path.splitext(image.filename)[1] or ".jpg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contents = await image.read()
            tmp.write(contents)
            tmp_path = tmp.name

        # 2. Extract Text via OCR
        print(f"Running OCR on {tmp_path}...")
        extracted_text = ocr_model.extract_text(tmp_path)
        os.unlink(tmp_path)  # Cleanup

        if not extracted_text or len(extracted_text.strip()) < 5:
            raise HTTPException(status_code=400, detail="No readable text found in the image.")

        print(f"OCR Extracted: {extracted_text[:100]}...")

        # 3. Interpret Text -> Question (Groq)
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

        # 4. Run Vanna Pipeline
        pipeline_result = await ask_insightx(QueryRequest(question=formulated_question))

        # 5. Add metadata
        pipeline_result["ocr_text"] = extracted_text
        pipeline_result["original_question"] = formulated_question  # The question derived from OCR

        return pipeline_result

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"OCR pipeline failed: {str(e)}")


# â”€â”€ Health Check â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@app.get("/")
async def health_check():
    return {"status": "ok", "service": "InsightX Agentic API"}


# â”€â”€ Run â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

if __name__ == "__main__":
    print("[âœ“] Starting InsightX Agentic API on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
