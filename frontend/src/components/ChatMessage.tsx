import { motion } from "framer-motion";
import { Download } from "lucide-react";
import DataVisualizer from "@/components/DataVisualizer";

export interface Message {
  id: string;
  role: "user" | "ai";
  content: string;
  data?: {
    type: "kpi" | "chart" | "table" | "text";
    title: string;
    summary?: string;
    // KPI
    value?: string;
    change?: string;
    changeDirection?: "up" | "down";
    // Chart
    chartType?: "line" | "bar" | "pie";
    data?: Array<{ name: string; value: number }>;
    // Table
    columns?: string[];
    rows?: string[][];
    // Text
    content?: string;
    // SQL (collapsible detail)
    sql?: string;
    // Follow-up questions
    followUpQuestions?: string[];
  };
  onFollowUp?: (question: string) => void;
}

interface ChatMessageProps {
  message: Message;
}

const ChatMessage = ({ message }: ChatMessageProps) => {
  const isUser = message.role === "user";

  const handleExport = () => {
    const blob = new Blob([JSON.stringify(message.data, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `insightx-export-${message.id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex gap-3 ${isUser ? "justify-end" : "items-start"}`}
    >
      {!isUser && (
        <div className="w-8 h-8 rounded-lg glow-button flex items-center justify-center text-[10px] font-bold shrink-0 mt-1">
          IX
        </div>
      )}

      <div className={`max-w-[85%] ${isUser ? "chat-user-msg px-4 py-3" : "space-y-3"}`}>
        {isUser ? (
          <p className="text-sm text-foreground">{message.content}</p>
        ) : (
          <>
            {message.data && (
              <div className="chat-ai-msg p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground font-medium uppercase tracking-wider">
                    {message.data.title}
                  </span>
                  <button
                    onClick={handleExport}
                    className="p-1.5 rounded-lg hover:bg-secondary text-muted-foreground hover:text-foreground transition-colors"
                    title="Export data"
                  >
                    <Download className="w-3.5 h-3.5" />
                  </button>
                </div>
                <DataVisualizer data={message.data} />
                {message.data.summary && (
                  <p className="text-sm text-muted-foreground pt-2 border-t border-border/30">
                    {message.data.summary}
                  </p>
                )}
                {/* Follow-up questions */}
                {message.data.followUpQuestions && message.data.followUpQuestions.length > 0 && (
                  <div className="pt-2 border-t border-border/30">
                    <p className="text-xs text-muted-foreground mb-2 uppercase tracking-wider">Suggested follow-ups</p>
                    <div className="flex flex-wrap gap-2">
                      {message.data.followUpQuestions.map((q) => (
                        <button
                          key={q}
                          onClick={() => message.onFollowUp?.(q)}
                          className="px-3 py-1.5 rounded-lg text-xs border border-border/50 bg-secondary/50 text-muted-foreground hover:text-foreground hover:border-primary/30 transition-all text-left"
                        >
                          {q}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
                {/* SQL Disclosure */}
                {message.data.sql && (
                  <details className="pt-1">
                    <summary className="text-xs text-muted-foreground/60 cursor-pointer hover:text-muted-foreground transition-colors">
                      View SQL
                    </summary>
                    <pre className="mt-2 text-xs bg-secondary/40 rounded-lg p-3 overflow-x-auto text-muted-foreground font-mono">
                      {message.data.sql}
                    </pre>
                  </details>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </motion.div>
  );
};

export default ChatMessage;
