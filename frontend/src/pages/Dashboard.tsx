import { useState, useRef, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Mic, MicOff, ImagePlus, X, Download } from "lucide-react";
import { toast } from "sonner";
import DashboardSidebar from "@/components/DashboardSidebar";
import ChatMessage, { type Message } from "@/components/ChatMessage";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import {
  askQuestion,
  voiceAsk,
  ocrAsk,
  createSession,
  getSessionMessages,
  type ApiResponse,
  type ChatHistoryMessage,
} from "@/lib/api";

// -- Helpers ------------------------------------------------------------------

function apiResponseToMessageData(res: ApiResponse): Message["data"] {
  const hasData = res.data && res.data.length > 0;
  return {
    title: "InsightX Analysis",
    summary: res.answer,
    rawData: hasData ? res.data : undefined,
    chartType: res.chart_type ?? (hasData ? "table" : "text"),
    xAxis: res.x_axis ?? null,
    yAxis: res.y_axis ?? null,
    textContent: !hasData ? res.answer : undefined,
    sql: res.sql,
    followUpQuestions: res.follow_up_questions,
  };
}

function buildChatHistory(messages: Message[]): ChatHistoryMessage[] {
  return messages
    .filter((m) => m.content.trim() && !m.content.startsWith("\ud83c\udfa4 Voice"))
    .map((m) => ({
      role: (m.role === "user" ? "user" : "assistant") as "user" | "assistant",
      content: m.role === "ai" ? (m.data?.summary ?? m.content) : m.content,
    }));
}

const SUGGESTIONS = [
  "Show total UPI transactions",
  "Top 5 transactions by amount",
  "Transaction volume by bank",
];

// -- Dashboard Component ------------------------------------------------------

const Dashboard = () => {
  const { sessionId: urlSessionId } = useParams<{ sessionId?: string }>();
  const navigate = useNavigate();

  const [sessionId, setSessionId] = useState<string | null>(urlSessionId ?? null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sidebarRefreshKey, setSidebarRefreshKey] = useState(0);

  // Voice recording
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  // Image upload
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollRef = useRef<HTMLDivElement>(null);

  // Sync URL param to state
  useEffect(() => {
    setSessionId(urlSessionId ?? null);
  }, [urlSessionId]);

  // Load messages when sessionId changes
  useEffect(() => {
    if (!sessionId) {
      setMessages([]);
      return;
    }
    (async () => {
      try {
        const stored = await getSessionMessages(sessionId);
        const loaded: Message[] = stored.map((m, i) => {
          if (m.role === "user") {
            return { id: `s-${i}`, role: "user" as const, content: m.content };
          }
          // assistant
          let data: Message["data"] | undefined;
          try {
            const full = typeof m.data === "string" ? JSON.parse(m.data) : m.data;
            if (full && full.answer) {
              const hasData = full.data && full.data.length > 0;
              data = {
                title: "InsightX Analysis",
                summary: full.answer,
                rawData: hasData ? full.data : undefined,
                chartType: full.chart_type ?? (hasData ? "table" : "text"),
                xAxis: full.x_axis ?? null,
                yAxis: full.y_axis ?? null,
                textContent: !hasData ? full.answer : undefined,
                sql: full.sql ?? m.sql_text ?? "",
                followUpQuestions: full.follow_up_questions ?? [],
              };
            }
          } catch {
            // fallback
          }
          if (!data) {
            data = {
              title: "InsightX Analysis",
              summary: m.content,
              textContent: m.content,
              chartType: "text",
              xAxis: null,
              yAxis: null,
            };
          }
          return {
            id: `s-${i}`,
            role: "ai" as const,
            content: m.content,
            data,
          };
        });
        setMessages(loaded);
      } catch {
        // session might be invalid — just clear
        setMessages([]);
      }
    })();
  }, [sessionId]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, isLoading]);

  // Ensure session exists (auto-create if needed)
  const ensureSession = useCallback(async (): Promise<string> => {
    if (sessionId) return sessionId;
    const session = await createSession();
    setSessionId(session.id);
    navigate(`/dashboard/${session.id}`, { replace: true });
    return session.id;
  }, [sessionId, navigate]);

  // -- Send text / image question ---------------------------------------------

  const sendQuestion = useCallback(
    async (question: string, snapshot?: ChatHistoryMessage[]) => {
      if (!question.trim() || isLoading) return;

      const sid = await ensureSession();
      const history = snapshot ?? buildChatHistory(messages);

      const userMsg: Message = { id: Date.now().toString(), role: "user", content: question };
      setMessages((prev) => [...prev, userMsg]);
      setInput("");
      setIsLoading(true);

      const imgToSend = selectedImage;
      setSelectedImage(null);

      try {
        let res: ApiResponse;
        if (imgToSend) {
          res = await ocrAsk(imgToSend, question, history);
          toast.success("Image analysed successfully");
        } else {
          res = await askQuestion(question, history, sid);
        }

        const data = apiResponseToMessageData(res);
        const aiMsg: Message = {
          id: (Date.now() + 1).toString(),
          role: "ai",
          content: res.answer,
          data,
          onFollowUp: (q) => {
            const nextHistory = buildChatHistory([
              ...messages,
              userMsg,
              { id: "tmp", role: "ai", content: res.answer, data: { title: "", summary: res.answer, textContent: res.answer, chartType: "text", xAxis: null, yAxis: null } },
            ]);
            sendQuestion(q, nextHistory);
          },
        };
        setMessages((prev) => [...prev, aiMsg]);
        setSidebarRefreshKey((k) => k + 1);
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Unknown error";
        toast.error(`Error: ${msg}`);
        setMessages((prev) => [
          ...prev,
          {
            id: (Date.now() + 1).toString(),
            role: "ai",
            content: "",
            data: { title: "Error", textContent: msg, summary: "", chartType: "text", xAxis: null, yAxis: null },
          },
        ]);
      } finally {
        setIsLoading(false);
      }
    },
    [isLoading, selectedImage, messages, ensureSession],
  );

  const handleSend = () => {
    const question = input.trim() || (selectedImage ? "Analyse this image" : "");
    if (!question && !selectedImage) return;
    sendQuestion(question);
  };

  // -- New Chat ---------------------------------------------------------------

  const handleNewChat = useCallback(() => {
    setSessionId(null);
    setMessages([]);
    setInput("");
    navigate("/dashboard");
  }, [navigate]);

  // -- Voice Recording --------------------------------------------------------

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mr = new MediaRecorder(stream, { mimeType: "audio/webm" });
      audioChunksRef.current = [];
      mr.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };
      mr.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        const blob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        setIsLoading(true);
        const history = buildChatHistory(messages);
        const userMsg: Message = { id: Date.now().toString(), role: "user", content: "\ud83c\udfa4 Voice query..." };
        setMessages((prev) => [...prev, userMsg]);
        try {
          const res = await voiceAsk(blob, history);
          setMessages((prev) =>
            prev.map((m) => (m.id === userMsg.id ? { ...m, content: `\ud83c\udfa4 "${res.transcription}"` } : m)),
          );
          const data = apiResponseToMessageData(res);
          const aiMsg: Message = {
            id: (Date.now() + 1).toString(),
            role: "ai",
            content: res.answer,
            data,
            onFollowUp: (q) => sendQuestion(q),
          };
          setMessages((prev) => [...prev, aiMsg]);
        } catch (err) {
          const msg = err instanceof Error ? err.message : "Transcription failed";
          toast.error(msg);
        } finally {
          setIsLoading(false);
        }
      };
      mr.start();
      mediaRecorderRef.current = mr;
      setIsRecording(true);
    } catch {
      toast.error("Microphone access denied.");
    }
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setIsRecording(false);
  };
  const toggleRecording = () => (isRecording ? stopRecording() : startRecording());

  // -- PDF Export --------------------------------------------------------------

  const exportToPDF = async () => {
    const element = document.getElementById("insightx-report-container");
    if (!element) {
      toast.error("Nothing to export yet.");
      return;
    }

    toast.info("Generating PDF report…");

    // Hide elements that shouldn't appear in the PDF
    const style = document.createElement("style");
    style.id = "pdf-export-styles";
    style.textContent = `
      .pdf-exclude { display: none !important; }
      #insightx-input-area { display: none !important; }
      #insightx-report-container { overflow: visible !important; height: auto !important; }
    `;
    document.head.appendChild(style);

    try {
      const html2pdf = (await import("html2pdf.js")).default;
      const opt = {
        margin: [0.4, 0.4, 0.4, 0.4],
        filename: "InsightX_Executive_Report.pdf",
        image: { type: "jpeg" as const, quality: 1.0 },
        html2canvas: { scale: 2, useCORS: true, backgroundColor: "#0f172a", letterRendering: true },
        jsPDF: { unit: "in" as const, format: "a4", orientation: "portrait" as const },
        pagebreak: { mode: ["css", "legacy"], avoid: ".print-avoid-break" },
      };
      await html2pdf().set(opt).from(element).save();
      toast.success("Report downloaded!");
    } catch (err) {
      console.error(err);
      toast.error("Failed to generate PDF.");
    } finally {
      document.getElementById("pdf-export-styles")?.remove();
    }
  };

  // -- Image Upload -----------------------------------------------------------

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedImage(file);
      toast.info(`Image selected: ${file.name}`);
    }
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  // -- Render -----------------------------------------------------------------

  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full bg-background">
        <DashboardSidebar
          activeSessionId={sessionId}
          onNewChat={handleNewChat}
          refreshKey={sidebarRefreshKey}
        />
        <div className="flex-1 flex flex-col min-h-screen">

          {/* Header */}
          <header className="flex items-center justify-between px-4 py-3 border-b border-border/50 bg-background/80 backdrop-blur-sm">
            <div className="flex items-center gap-3">
              <SidebarTrigger />
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-md glow-button flex items-center justify-center text-[10px] font-bold">IX</div>
                <span className="font-semibold text-foreground text-sm">InsightX</span>
              </div>
            </div>
            {messages.length > 0 && (
              <button
                onClick={exportToPDF}
                className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium
                           bg-violet-600 hover:bg-violet-700 text-white
                           shadow-md shadow-violet-600/20 hover:shadow-violet-600/30
                           transition-all duration-200 cursor-pointer"
              >
                <Download className="w-4 h-4" />
                <span className="hidden sm:inline">Export Board Report</span>
              </button>
            )}
          </header>

          {/* Chat Area */}
          <div ref={scrollRef} id="insightx-report-container" className="flex-1 overflow-y-auto px-4 md:px-8 py-6">
            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.5 }}>
                  <div className="w-16 h-16 rounded-2xl glow-button flex items-center justify-center text-2xl font-bold mb-6 mx-auto">IX</div>
                  <h2 className="text-2xl font-bold text-foreground mb-2">Welcome to InsightX</h2>
                  <p className="text-muted-foreground max-w-md">Ask anything about your UPI transactions — by text, voice, or image.</p>
                  <div className="flex flex-wrap gap-2 mt-6 justify-center">
                    {SUGGESTIONS.map((q) => (
                      <button
                        key={q}
                        onClick={() => sendQuestion(q)}
                        className="px-4 py-2 rounded-xl text-sm border border-border/50 bg-secondary/50 text-muted-foreground hover:text-foreground hover:border-primary/30 transition-all"
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                </motion.div>
              </div>
            )}

            <div className="max-w-3xl mx-auto space-y-4">
              <AnimatePresence>
                {messages.map((msg) => (
                  <ChatMessage key={msg.id} message={msg} />
                ))}
              </AnimatePresence>

              {isLoading && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex gap-3 items-start">
                  <div className="w-8 h-8 rounded-lg glow-button flex items-center justify-center text-[10px] font-bold shrink-0">IX</div>
                  <div className="chat-ai-msg px-4 py-3 space-y-2 w-64">
                    <div className="h-3 w-3/4 rounded skeleton-shimmer" />
                    <div className="h-3 w-1/2 rounded skeleton-shimmer" />
                    <div className="h-3 w-2/3 rounded skeleton-shimmer" />
                  </div>
                </motion.div>
              )}
            </div>
          </div>

          {/* Input Area */}
          <div id="insightx-input-area" className="sticky bottom-0 px-4 md:px-8 py-4 bg-gradient-to-t from-background via-background to-background/0">
            <div className="max-w-3xl mx-auto space-y-2">
              {selectedImage && (
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-secondary/60 w-fit text-sm text-muted-foreground border border-border/40">
                  <ImagePlus className="w-3.5 h-3.5" />
                  <span className="max-w-[200px] truncate">{selectedImage.name}</span>
                  <button onClick={() => setSelectedImage(null)} className="ml-1 hover:text-foreground">
                    <X className="w-3 h-3" />
                  </button>
                </div>
              )}

              <div className="glass-card flex items-center gap-2 px-4 py-2">
                <button
                  onClick={toggleRecording}
                  disabled={isLoading}
                  className={`relative p-2.5 rounded-xl transition-all ${isRecording ? "bg-accent/20 text-accent" : "text-muted-foreground hover:text-foreground hover:bg-secondary"} disabled:opacity-40`}
                  title={isRecording ? "Stop recording" : "Start voice query"}
                >
                  {isRecording && <span className="pulse-ring" />}
                  {isRecording ? <MicOff className="w-5 h-5 relative z-10" /> : <Mic className="w-5 h-5" />}
                </button>

                {isRecording && (
                  <div className="flex items-center gap-1 px-2">
                    {[...Array(5)].map((_, i) => (
                      <div
                        key={i}
                        className="w-1 bg-accent rounded-full"
                        style={{ animation: `waveform 0.6s ease-in-out ${i * 0.1}s infinite`, height: "4px" }}
                      />
                    ))}
                  </div>
                )}

                <button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isLoading}
                  className="p-2.5 rounded-xl text-muted-foreground hover:text-foreground hover:bg-secondary transition-all disabled:opacity-40"
                  title="Upload image for OCR analysis"
                >
                  <ImagePlus className="w-5 h-5" />
                </button>
                <input ref={fileInputRef} type="file" accept="image/jpeg,image/png,image/webp,image/bmp" className="hidden" onChange={handleImageChange} />

                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSend()}
                  placeholder={selectedImage ? "Add context or press send to analyse the image\u2026" : "Ask about your transaction history\u2026"}
                  disabled={isRecording}
                  className="flex-1 bg-transparent border-none outline-none text-foreground placeholder:text-muted-foreground text-sm py-2 disabled:opacity-40"
                />

                <button
                  onClick={handleSend}
                  disabled={(!input.trim() && !selectedImage) || isLoading || isRecording}
                  className="p-2.5 rounded-xl glow-button text-primary-foreground disabled:opacity-30 disabled:shadow-none transition-all"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </SidebarProvider>
  );
};

export default Dashboard;
