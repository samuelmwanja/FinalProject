import React from "react";
import { Button } from "@/components/ui/button";
import { ShieldIcon } from "lucide-react";
import { useAuth } from "@/lib/auth";

interface DashboardHeaderProps {
  userName?: string;
  userAvatar?: string;
  isDarkMode?: boolean;
  onThemeToggle?: () => void;
}

const DashboardHeader = ({
  userName = "User",
  userAvatar,
  isDarkMode,
  onThemeToggle,
}: DashboardHeaderProps) => {
  const { logout } = useAuth();

  return (
    <header className="w-full h-16 border-b bg-background shadow-sm">
      <div className="max-w-7xl mx-auto h-full px-4 sm:px-6 lg:px-8 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <ShieldIcon className="h-6 w-6 text-primary" />
          <h1 className="text-xl font-bold">SpamShield</h1>
        </div>

        <div className="flex items-center gap-4">
          <span className="text-sm text-muted-foreground">
            Welcome, {userName}
          </span>
          <Button variant="outline" size="sm" onClick={logout}>
            Sign Out
          </Button>
        </div>
      </div>
    </header>
  );
};

export default DashboardHeader; 