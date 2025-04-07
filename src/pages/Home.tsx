import { useState } from "react";
import DashboardHeader from "@/components/dashboard/DashboardHeader";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertTriangle, BarChart, List, MessageCircle, Shield, TrendingUp } from "lucide-react";
import MLSettingsPanel from "@/components/dashboard/MLSettingsPanel";

interface HomeProps {
  userName?: string;
  userAvatar?: string;
  isDarkMode?: boolean;
  onThemeToggle?: () => void;
}

const Home = ({
  userName = "John Doe",
  userAvatar = "https://api.dicebear.com/7.x/avataaars/svg?seed=John",
  isDarkMode = false,
  onThemeToggle = () => {},
}: HomeProps) => {
  const [isMLSettingsOpen, setIsMLSettingsOpen] = useState(false);

  // Stats for metrics cards
  const stats = {
    totalComments: 1245,
    totalCommentsChange: "+24%",
    flaggedSpam: 87,
    flaggedSpamChange: "-12%",
    spamRate: "7%",
    spamRateContext: "Below industry average (12%)",
    mostActiveVideo: "Tech Reviews #42",
    mostActiveVideoComments: "42 comments today"
  };

  // Recent activity items
  const recentActivity = [
    { id: "1", text: "Check out this amazing offer at...", time: "2 hours ago" },
    { id: "2", text: "I made $5000 working from home using...", time: "5 hours ago" },
    { id: "3", text: "Free subscribers at my channel www...", time: "1 day ago" },
  ];

  const handleMLSettingsSave = (settings: any) => {
    console.log("Saving ML settings:", settings);
    setIsMLSettingsOpen(false);
  };

  return (
    <div className="min-h-screen bg-background">
      <DashboardHeader
        userName={userName}
        userAvatar={userAvatar}
        isDarkMode={isDarkMode}
        onThemeToggle={onThemeToggle}
      />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="mb-6">
          <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
          <p className="text-muted-foreground mt-1">
            Monitor and manage spam comments on your YouTube channel.
          </p>
        </div>

        {/* Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-sm font-medium">Total Comments</CardTitle>
              <MessageCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalComments}</div>
              <p className="text-xs text-muted-foreground">
                {stats.totalCommentsChange} from last month
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-sm font-medium">Flagged Spam</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.flaggedSpam}</div>
              <p className="text-xs text-muted-foreground">
                {stats.flaggedSpamChange} from last month
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-sm font-medium">Spam Rate</CardTitle>
              <BarChart className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.spamRate}</div>
              <p className="text-xs text-muted-foreground">
                {stats.spamRateContext}
              </p>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-sm font-medium">Most Active Video</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold truncate">{stats.mostActiveVideo}</div>
              <p className="text-xs text-muted-foreground">
                {stats.mostActiveVideoComments}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content - Recent Activity and Quick Actions */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Activity */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <p className="text-sm text-muted-foreground">
                Recent spam comments detected on your videos
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              {recentActivity.map((activity) => (
                <div key={activity.id} className="flex items-start gap-3">
                  <div className="text-amber-500 mt-0.5">
                    <AlertTriangle className="h-5 w-5" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium mb-1">{activity.text}</p>
                    <p className="text-xs text-muted-foreground">{activity.time}</p>
                  </div>
                </div>
              ))}
              <Button 
                variant="outline" 
                className="w-full mt-4"
              >
                Refresh Data
              </Button>
            </CardContent>
          </Card>
          
          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <p className="text-sm text-muted-foreground">
                Manage your YouTube channel protection
              </p>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <Button variant="outline" className="w-full justify-start items-center h-12 text-sm">
                  <span className="flex items-center">
                    <List className="h-4 w-4 mr-2" />
                    View All Comments
                  </span>
                </Button>
                <Button variant="outline" className="w-full justify-start items-center h-12 text-sm">
                  <span className="flex items-center">
                    <Shield className="h-4 w-4 mr-2" />
                    Protection Settings
                  </span>
                </Button>
                <Button variant="outline" className="w-full justify-start items-center h-12 text-sm">
                  <span className="flex items-center">
                    <BarChart className="h-4 w-4 mr-2" />
                    Analytics
                  </span>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        <MLSettingsPanel
          open={isMLSettingsOpen}
          onOpenChange={setIsMLSettingsOpen}
          onSave={handleMLSettingsSave}
        />
      </div>

      <footer className="border-t py-4 mt-8">
        <div className="max-w-7xl mx-auto flex justify-between text-xs text-muted-foreground px-4 sm:px-6 lg:px-8">
          <div>© 2023 SpamShield. All rights reserved.</div>
          <div>Privacy Policy · Terms of Service</div>
        </div>
      </footer>
    </div>
  );
};

export default Home; 