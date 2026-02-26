import { useEffect, useState, useCallback } from "react";
import { Plus, MessageSquare, Settings, Home, Trash2 } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import { listSessions, deleteSession, type ChatSession } from "@/lib/api";

// -- Relative time helper -----------------------------------------------------

function timeAgo(isoStr: string): string {
  const diff = Date.now() - new Date(isoStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins} min ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  if (days === 1) return "Yesterday";
  return `${days} days ago`;
}

// -- Props --------------------------------------------------------------------

interface DashboardSidebarProps {
  activeSessionId?: string | null;
  onNewChat: () => void;
  refreshKey?: number;
}

// -- Component ----------------------------------------------------------------

const DashboardSidebar = ({ activeSessionId, onNewChat, refreshKey }: DashboardSidebarProps) => {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const navigate = useNavigate();

  const loadSessions = useCallback(async () => {
    try {
      const data = await listSessions();
      setSessions(data);
    } catch {
      // silently ignore
    }
  }, []);

  // Load on mount + whenever refreshKey changes (new Q&A was sent)
  useEffect(() => {
    loadSessions();
  }, [loadSessions, refreshKey]);

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    try {
      await deleteSession(id);
      setSessions((prev) => prev.filter((s) => s.id !== id));
      if (activeSessionId === id) {
        onNewChat();
      }
    } catch {
      // ignore
    }
  };

  return (
    <Sidebar className="border-r border-border/50">
      <SidebarContent className="pt-4">
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <Link to="/" className="flex items-center gap-2 text-muted-foreground hover:text-foreground">
                    <Home className="w-4 h-4" />
                    <span>Home</span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton
                  className="w-full flex items-center gap-2 bg-primary/10 text-primary hover:bg-primary/20 cursor-pointer"
                  onClick={onNewChat}
                >
                  <Plus className="w-4 h-4" />
                  <span>New Chat</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel className="text-xs text-muted-foreground uppercase tracking-wider">
            Recent
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {sessions.length === 0 && (
                <div className="px-3 py-2 text-xs text-muted-foreground/60">No chats yet</div>
              )}
              {sessions.map((session) => {
                const isActive = session.id === activeSessionId;
                return (
                  <SidebarMenuItem key={session.id}>
                    <SidebarMenuButton
                      className={`group flex items-center gap-2 cursor-pointer transition-colors ${isActive
                          ? "text-foreground bg-secondary/70"
                          : "text-muted-foreground hover:text-foreground"
                        }`}
                      onClick={() => navigate(`/dashboard/${session.id}`)}
                    >
                      <MessageSquare className="w-3.5 h-3.5 shrink-0" />
                      <div className="flex-1 min-w-0">
                        <span className="text-sm truncate block">{session.title}</span>
                        <span className="text-[10px] text-muted-foreground/60">{timeAgo(session.updated_at)}</span>
                      </div>
                      <button
                        onClick={(e) => handleDelete(e, session.id)}
                        className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-destructive/20 hover:text-destructive transition-all"
                        title="Delete chat"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <div className="mt-auto p-4">
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton className="flex items-center gap-2 text-muted-foreground hover:text-foreground cursor-pointer">
                <Settings className="w-4 h-4" />
                <span>Settings</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </div>
      </SidebarContent>
    </Sidebar>
  );
};

export default DashboardSidebar;
