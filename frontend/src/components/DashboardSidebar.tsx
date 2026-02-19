import { Plus, MessageSquare, Settings, Home } from "lucide-react";
import { Link, useLocation } from "react-router-dom";
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

const mockHistory = [
  { id: "1", title: "Spending trend analysis", time: "2 min ago" },
  { id: "2", title: "Top transactions by amount", time: "1 hour ago" },
  { id: "3", title: "Monthly expense breakdown", time: "Yesterday" },
  { id: "4", title: "UPI payment frequency", time: "3 days ago" },
];

const DashboardSidebar = () => {
  const location = useLocation();

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
                  onClick={() => window.location.reload()}
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
              {mockHistory.map((item) => (
                <SidebarMenuItem key={item.id}>
                  <SidebarMenuButton className="flex items-center gap-2 text-muted-foreground hover:text-foreground cursor-pointer">
                    <MessageSquare className="w-3.5 h-3.5 shrink-0" />
                    <div className="flex-1 min-w-0">
                      <span className="text-sm truncate block">{item.title}</span>
                      <span className="text-[10px] text-muted-foreground/60">{item.time}</span>
                    </div>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
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
