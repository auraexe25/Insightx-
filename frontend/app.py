"""
frontend/app.py — InsightX Chainlit Conversational AI Interface.

Connects to the headless FastAPI backend at /api/ask and renders
executive answers, data tables, SQL proofs, and follow-up suggestions.

Supports voice input via the microphone button — audio is sent to
/api/voice-ask for transcription + analysis in one request.

Usage:
  cd frontend
  chainlit run app.py -w
"""

import io
import chainlit as cl
import requests
import pandas as pd

# ── Backend Endpoints ────────────────────────────────────────────────────────

API_URL = "http://localhost:8000/api/ask"
VOICE_API_URL = "http://localhost:8000/api/voice-ask"


# ── Chat Initialization ─────────────────────────────────────────────────────

@cl.on_chat_start
async def start():
    await cl.Message(
        content=(
            "👋 **Welcome to the InsightX Executive Dashboard.**\n\n"
            "Ask me anything about your UPI transaction data — "
            "I'll fetch the numbers, analyze them, and suggest what to explore next.\n\n"
            "🎤 **Voice Input**: Click the microphone button to ask your question by voice!\n\n"
            "_What business metrics would you like to analyze today?_"
        )
    ).send()


# ── Core Message Handler ────────────────────────────────────────────────────

@cl.on_message
async def main(message: cl.Message):
    # Immediately show a loading state
    msg = cl.Message(content="⏳ *Analyzing transaction data...*")
    await msg.send()

    try:
        # ── Call the FastAPI backend ──────────────────────────────────────
        response = requests.post(API_URL, json={"question": message.content})
        response.raise_for_status()
        data = response.json()

        await _render_response(msg, data)

    except requests.exceptions.ConnectionError:
        msg.content = (
            "❌ **Backend Unreachable**\n\n"
            "Could not connect to the InsightX API at `localhost:8000`.\n"
            "Make sure the backend is running:\n"
            "```bash\ncd backend\nuvicorn app.main:app --host 0.0.0.0 --port 8000 --reload\n```"
        )
        await msg.update()

    except requests.exceptions.HTTPError as e:
        msg.content = f"❌ **API Error ({e.response.status_code})**\n\n`{e.response.text}`"
        await msg.update()

    except Exception as e:
        msg.content = f"❌ **Unexpected Error**\n\n`{str(e)}`"
        await msg.update()


# ── Audio / Voice Input Handlers ─────────────────────────────────────────────

@cl.on_audio_start
async def on_audio_start():
    print("[DEBUG] on_audio_start triggered")
    return True

@cl.on_audio_chunk
async def on_audio_chunk(chunk: cl.InputAudioChunk):
    """Collect audio chunks from the browser microphone."""
    print(f"[DEBUG] on_audio_chunk: isStart={chunk.isStart}, mimeType={chunk.mimeType}, data_len={len(chunk.data)}")
    if chunk.isStart:
        # Initialize a buffer for this recording session
        buffer = io.BytesIO()
        buffer.name = "voice_input.webm"
        cl.user_session.set("audio_buffer", buffer)
        cl.user_session.set("audio_mime", chunk.mimeType)

    # Append chunk data to the buffer
    buffer = cl.user_session.get("audio_buffer")
    if buffer:
        buffer.write(chunk.data)


@cl.on_audio_end
async def on_audio_end(elements):
    """When recording stops, send audio to the voice-ask endpoint."""
    print("[DEBUG] on_audio_end triggered")
    buffer: io.BytesIO = cl.user_session.get("audio_buffer")
    mime_type = cl.user_session.get("audio_mime", "audio/webm")

    if not buffer:
        print("[DEBUG] No buffer found in session")
        await cl.Message(content="❌ No audio was captured. Please try again.").send()
        return

    # Reset buffer position to the beginning for reading
    buffer.seek(0)
    audio_bytes = buffer.read()
    print(f"[DEBUG] Audio captured: {len(audio_bytes)} bytes")

    if len(audio_bytes) == 0:
        await cl.Message(content="❌ Empty audio recording. Please try again.").send()
        return

    # Show loading message
    msg = cl.Message(content="🎤 *Transcribing your voice and analyzing...*")
    await msg.send()

    try:
        # Send audio to the combined voice-ask endpoint
        files = {"audio": ("voice_input.webm", audio_bytes, mime_type)}
        response = requests.post(VOICE_API_URL, files=files)
        response.raise_for_status()
        data = response.json()

        # Show what was transcribed
        transcription = data.get("transcription", "")
        if transcription:
            await cl.Message(
                content=f"🗣️ *You said:* \"{transcription}\"",
                author="User",
            ).send()

        await _render_response(msg, data)

    except requests.exceptions.ConnectionError:
        msg.content = (
            "❌ **Backend Unreachable**\n\n"
            "Could not connect to the InsightX API at `localhost:8000`.\n"
            "Make sure the backend is running."
        )
        await msg.update()

    except requests.exceptions.HTTPError as e:
        msg.content = f"❌ **API Error ({e.response.status_code})**\n\n`{e.response.text}`"
        await msg.update()

    except Exception as e:
        msg.content = f"❌ **Unexpected Error**\n\n`{str(e)}`"
        await msg.update()

    finally:
        # Cleanup session audio data
        cl.user_session.set("audio_buffer", None)
        cl.user_session.set("audio_mime", None)


# ── Shared Response Renderer ────────────────────────────────────────────────

async def _render_response(msg: cl.Message, data: dict):
    """Format and display the pipeline response (used by both text & voice)."""
    # ── Extract components ───────────────────────────────────────────
    answer = data.get("answer", "No answer available.")
    sql = data.get("sql", "-- No SQL generated")
    raw_data = data.get("data", [])
    follow_up_questions = data.get("follow_up_questions", [])

    # ── Format the answer + data table ───────────────────────────────
    final_text = f"📊 **Executive Summary**\n\n{answer}"

    if raw_data:
        df = pd.DataFrame(raw_data)
        table_md = df.to_markdown(index=False)
        final_text += f"\n\n---\n\n📋 **Data Table** ({len(df)} rows)\n\n{table_md}"

    # ── SQL Proof (expandable element) ───────────────────────────────
    sql_element = cl.Text(
        name="View Mathematical Proof (SQL)",
        content=f"```sql\n{sql}\n```",
        display="inline",
    )

    # ── Follow-Up Action Buttons ─────────────────────────────────────
    actions = []
    for question in follow_up_questions:
        actions.append(
            cl.Action(
                name="follow_up",
                value=question,
                label=f"💡 {question}",
            )
        )

    # ── Update the message with full content ─────────────────────────
    msg.content = final_text
    msg.elements = [sql_element]
    msg.actions = actions
    await msg.update()


# ── Follow-Up Button Callback ───────────────────────────────────────────────

@cl.action_callback("follow_up")
async def on_follow_up(action: cl.Action):
    # Show the clicked question as if the user typed it
    await cl.Message(content=action.value, author="User").send()

    # Trigger the main pipeline with the follow-up question
    await main(cl.Message(content=action.value))
