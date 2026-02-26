/**
 * InsightX API Service
 * Typed client for the FastAPI backend.
 */

export interface ApiResponse {
    question: string;
    sql: string;
    data: Record<string, unknown>[];
    answer: string;
    follow_up_questions: string[];
    /** Only present on voice-ask responses */
    transcription?: string;
    /** Only present on ocr-ask responses */
    ocr_text?: string;
    original_question?: string;
}

export interface ChatHistoryMessage {
    role: "user" | "assistant";
    content: string;
}

const BASE_URL = "/api";

// ── Text Query ────────────────────────────────────────────────────────────────

export async function askQuestion(
    question: string,
    chatHistory: ChatHistoryMessage[] = []
): Promise<ApiResponse> {
    const res = await fetch(`${BASE_URL}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, chat_history: chatHistory }),
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail ?? `Request failed (${res.status})`);
    }
    return res.json();
}

// ── Voice Query ───────────────────────────────────────────────────────────────

export async function voiceAsk(
    audioBlob: Blob,
    chatHistory: ChatHistoryMessage[] = []
): Promise<ApiResponse> {
    const form = new FormData();
    form.append("audio", audioBlob, "recording.webm");
    // voice-ask goes through a unified pipeline — pass history as JSON string
    if (chatHistory.length > 0) {
        form.append("chat_history", JSON.stringify(chatHistory));
    }

    const res = await fetch(`${BASE_URL}/voice-ask`, {
        method: "POST",
        body: form,
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail ?? `Voice request failed (${res.status})`);
    }
    return res.json();
}

// ── OCR / Image Query ─────────────────────────────────────────────────────────

export async function ocrAsk(
    imageFile: File,
    text?: string,
    chatHistory: ChatHistoryMessage[] = []
): Promise<ApiResponse> {
    const form = new FormData();
    form.append("image", imageFile);
    if (text?.trim()) {
        form.append("text", text.trim());
    }
    if (chatHistory.length > 0) {
        form.append("chat_history", JSON.stringify(chatHistory));
    }

    const res = await fetch(`${BASE_URL}/ocr-ask`, {
        method: "POST",
        body: form,
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail ?? `OCR request failed (${res.status})`);
    }
    return res.json();
}

// ── Helpers ───────────────────────────────────────────────────────────────────

/**
 * Convert API response data (array of records) into table columns + rows
 * that DataVisualizer can render.
 */
export function dataToTable(
    data: Record<string, unknown>[]
): { columns: string[]; rows: string[][] } | null {
    if (!data || data.length === 0) return null;
    const columns = Object.keys(data[0]);
    const rows = data.map((row) =>
        columns.map((col) => {
            const v = row[col];
            if (v === null || v === undefined) return "—";
            if (typeof v === "number") {
                const formatted = v.toLocaleString("en-IN");
                return /amount|value|total|sum|credit|debit/i.test(col)
                    ? `₹${formatted}`
                    : formatted;
            }
            return String(v);
        })
    );
    return { columns, rows };
}
