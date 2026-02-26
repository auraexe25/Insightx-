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
    transcription?: string;
    ocr_text?: string;
    original_question?: string;
}

export interface ChatHistoryMessage {
    role: "user" | "assistant";
    content: string;
}

export interface ChatSession {
    id: string;
    title: string;
    created_at: string;
    updated_at: string;
}

export interface StoredMessage {
    id: number;
    role: "user" | "assistant";
    content: string;
    sql_text: string;
    data: Record<string, unknown>;
    created_at: string;
}

const BASE_URL = "/api";

// -- Text Query ---------------------------------------------------------------

export async function askQuestion(
    question: string,
    chatHistory: ChatHistoryMessage[] = [],
    sessionId?: string | null,
): Promise<ApiResponse> {
    const res = await fetch(`${BASE_URL}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            question,
            chat_history: chatHistory,
            session_id: sessionId ?? null,
        }),
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail ?? `Request failed (${res.status})`);
    }
    return res.json();
}

// -- Voice Query --------------------------------------------------------------

export async function voiceAsk(
    audioBlob: Blob,
    chatHistory: ChatHistoryMessage[] = [],
): Promise<ApiResponse> {
    const form = new FormData();
    form.append("audio", audioBlob, "recording.webm");
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

// -- OCR / Image Query --------------------------------------------------------

export async function ocrAsk(
    imageFile: File,
    text?: string,
    chatHistory: ChatHistoryMessage[] = [],
): Promise<ApiResponse> {
    const form = new FormData();
    form.append("image", imageFile);
    if (text?.trim()) form.append("text", text.trim());
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

// -- Session CRUD -------------------------------------------------------------

export async function listSessions(): Promise<ChatSession[]> {
    const res = await fetch(`${BASE_URL}/sessions`);
    if (!res.ok) throw new Error("Failed to load sessions");
    return res.json();
}

export async function createSession(): Promise<ChatSession> {
    const res = await fetch(`${BASE_URL}/sessions`, { method: "POST" });
    if (!res.ok) throw new Error("Failed to create session");
    return res.json();
}

export async function getSessionMessages(sessionId: string): Promise<StoredMessage[]> {
    const res = await fetch(`${BASE_URL}/sessions/${sessionId}/messages`);
    if (!res.ok) throw new Error("Failed to load messages");
    return res.json();
}

export async function deleteSession(sessionId: string): Promise<void> {
    const res = await fetch(`${BASE_URL}/sessions/${sessionId}`, { method: "DELETE" });
    if (!res.ok) throw new Error("Failed to delete session");
}

// -- Helpers ------------------------------------------------------------------

export function dataToTable(
    data: Record<string, unknown>[],
): { columns: string[]; rows: string[][] } | null {
    if (!data || data.length === 0) return null;
    const columns = Object.keys(data[0]);
    const rows = data.map((row) =>
        columns.map((col) => {
            const v = row[col];
            if (v === null || v === undefined) return "\u2014";
            if (typeof v === "number") {
                const formatted = v.toLocaleString("en-IN");
                return /amount|value|total|sum|credit|debit/i.test(col)
                    ? `\u20b9${formatted}`
                    : formatted;
            }
            return String(v);
        }),
    );
    return { columns, rows };
}
