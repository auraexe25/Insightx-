import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Mic, MicOff } from "lucide-react";
import DashboardSidebar from "@/components/DashboardSidebar";
import ChatMessage, { type Message } from "@/components/ChatMessage";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";

const MOCK_RESPONSES: Record<string, Message["data"]> = {
  spending: {
    type: "chart",
    chartType: "line",
    title: "Monthly Spending Trend",
    data: [
      { name: "Jan", value: 12400 },
      { name: "Feb", value: 9800 },
      { name: "Mar", value: 15200 },
      { name: "Apr", value: 11600 },
      { name: "May", value: 18300 },
      { name: "Jun", value: 14700 },
    ],
    summary: "Your spending shows an upward trend over the last 6 months, with a peak of ₹18,300 in May.",
  },
  top: {
    type: "table",
    title: "Top 5 Transactions",
    columns: ["Date", "Description", "Amount", "Category"],
    rows: [
      ["2025-06-15", "Amazon India", "₹12,499", "Shopping"],
      ["2025-06-10", "Rent Payment", "₹25,000", "Housing"],
      ["2025-06-08", "Flight Booking", "₹8,750", "Travel"],
      ["2025-06-03", "Electronics Store", "₹6,999", "Shopping"],
      ["2025-06-01", "Insurance Premium", "₹5,200", "Insurance"],
    ],
    summary: "Here are your top 5 transactions by amount. Housing and Shopping dominate your expenses.",
  },
  total: {
    type: "kpi",
    title: "Total Spent This Month",
    value: "₹1,24,850",
    change: "+12.3%",
    changeDirection: "up" as const,
    summary: "Your total UPI spending this month is ₹1,24,850, up 12.3% compared to last month.",
  },
};

function classifyQuery(query: string): Message["data"] {
  const q = query.toLowerCase();
  if (q.includes("trend") || q.includes("spending")) return MOCK_RESPONSES.spending;
  if (q.includes("top") || q.includes("transaction")) return MOCK_RESPONSES.top;
  if (q.includes("total") || q.includes("spent")) return MOCK_RESPONSES.total;
  return {
    type: "text",
    title: "Analysis",
    content: "Based on your transaction data, I can see regular UPI payments across multiple categories. Try asking about your **spending trend**, **top transactions**, or **total spent** for specific visualizations.",
    summary: "",
  };
}

const Dashboard = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    const userMsg: Message = { id: Date.now().toString(), role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    await new Promise((r) => setTimeout(r, 1500 + Math.random() * 1000));

    const data = classifyQuery(input);
    const aiMsg: Message = {
      id: (Date.now() + 1).toString(),
      role: "ai",
      content: data.summary || "",
      data,
    };
    setMessages((prev) => [...prev, aiMsg]);
    setIsLoading(false);
  };

  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full bg-background">
        <DashboardSidebar />
        <div className="flex-1 flex flex-col min-h-screen">
          {/* Header */}
          <header className="flex items-center gap-3 px-4 py-3 border-b border-border/50 bg-background/80 backdrop-blur-sm">
            <SidebarTrigger />
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-md glow-button flex items-center justify-center text-[10px] font-bold">
                IX
              </div>
              <span className="font-semibold text-foreground text-sm">InsightX</span>
            </div>
          </header>

          {/* Chat Area */}
          <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 md:px-8 py-6">
            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.5 }}
                >
                  <div className="w-16 h-16 rounded-2xl glow-button flex items-center justify-center text-2xl font-bold mb-6 mx-auto">
                    IX
                  </div>
                  <h2 className="text-2xl font-bold text-foreground mb-2">
                    Welcome to InsightX
                  </h2>
                  <p className="text-muted-foreground max-w-md">
                    Ask anything about your UPI transactions. Try "Show my spending trend" or "Top 5 transactions."
                  </p>
                  <div className="flex flex-wrap gap-2 mt-6 justify-center">
                    {["Show my spending trend", "Top 5 transactions", "Total spent this month"].map(
                      (q) => (
                        <button
                          key={q}
                          onClick={() => {
                            setInput(q);
                          }}
                          className="px-4 py-2 rounded-xl text-sm border border-border/50 bg-secondary/50 text-muted-foreground hover:text-foreground hover:border-primary/30 transition-all"
                        >
                          {q}
                        </button>
                      )
                    )}
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
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex gap-3 items-start"
                >
                  <div className="w-8 h-8 rounded-lg glow-button flex items-center justify-center text-[10px] font-bold shrink-0">
                    IX
                  </div>
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
          <div className="sticky bottom-0 px-4 md:px-8 py-4 bg-gradient-to-t from-background via-background to-background/0">
            <div className="max-w-3xl mx-auto">
              <div className="glass-card flex items-center gap-2 px-4 py-2">
                <button
                  onClick={() => setIsRecording(!isRecording)}
                  className={`relative p-2.5 rounded-xl transition-all ${
                    isRecording
                      ? "bg-accent/20 text-accent"
                      : "text-muted-foreground hover:text-foreground hover:bg-secondary"
                  }`}
                >
                  {isRecording && <span className="pulse-ring" />}
                  {isRecording ? (
                    <MicOff className="w-5 h-5 relative z-10" />
                  ) : (
                    <Mic className="w-5 h-5" />
                  )}
                </button>

                {isRecording && (
                  <div className="flex items-center gap-1 px-2">
                    {[...Array(5)].map((_, i) => (
                      <div
                        key={i}
                        className="w-1 bg-accent rounded-full"
                        style={{
                          animation: `waveform 0.6s ease-in-out ${i * 0.1}s infinite`,
                          height: "4px",
                        }}
                      />
                    ))}
                  </div>
                )}

                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && handleSend()}
                  placeholder="Ask about your transaction history..."
                  className="flex-1 bg-transparent border-none outline-none text-foreground placeholder:text-muted-foreground text-sm py-2"
                />
                <button
                  onClick={handleSend}
                  disabled={!input.trim() || isLoading}
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
