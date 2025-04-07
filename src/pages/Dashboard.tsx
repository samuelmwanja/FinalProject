import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from "@/components/ui/card";
import { useAuth } from "@/lib/auth";
import { 
  BarChart, 
  Shield, 
  MessageCircle, 
  AlertTriangle, 
  TrendingUp, 
  List,
  Youtube
} from "lucide-react";
import { fetchDashboardMetrics } from "@/lib/api";
import { useToast } from "@/components/ui/use-toast";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import VideoAnalysisPanel from "@/components/dashboard/VideoAnalysisPanel";

const Dashboard = () => {
  const { user, logout } = useAuth();
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [metrics, setMetrics] = useState({
    total_comments: 0,
    flagged_spam: 0,
    spam_rate: 0,
    total_comments_change: 0,
    flagged_spam_change: 0,
    industry_average: 12,
    most_active_video: null as { title: string; spam_count: number } | null,
    recent_detections: [] as Array<{ id: string; text: string; time: string }>
  });

  // Fetch dashboard data when component mounts
  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const data = await fetchDashboardMetrics();
      setMetrics(data);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
      toast({
        title: "Error loading dashboard data",
        description: "Please try again later",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    try {
      await fetchDashboardData();
      toast({
        title: "Data refreshed",
        description: "Dashboard has been updated with the latest data",
      });
    } catch (error) {
      // Error is already handled in fetchDashboardData
    }
  };

  return (
    <div className="flex min-h-screen bg-background flex-col">
      <header className="sticky top-0 z-10 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex h-16 items-center justify-between py-4">
          <div className="flex items-center gap-2">
            <Shield className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold">SpamShield</span>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-sm text-muted-foreground">
              Welcome, {user?.email}
            </div>
            <Button variant="outline" size="sm" onClick={() => logout()}>
              Sign Out
            </Button>
          </div>
        </div>
      </header>
      
      <main className="flex-1">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="mb-8">
            <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
            <p className="text-muted-foreground">
              Monitor and manage spam comments on your YouTube channel.
            </p>
          </div>
          
          <Tabs defaultValue="overview" className="space-y-6">
            <TabsList>
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="video-analysis" className="flex items-center">
                <Youtube className="h-4 w-4 mr-2" />
                Video Analysis
              </TabsTrigger>
            </TabsList>
            
            <TabsContent value="overview" className="space-y-8">
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                    <CardTitle className="text-sm font-medium">Total Comments</CardTitle>
                    <MessageCircle className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{metrics.total_comments}</div>
                    <p className="text-xs text-muted-foreground">
                      {metrics.total_comments_change >= 0 ? '+' : ''}{metrics.total_comments_change}% from last month
                    </p>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                    <CardTitle className="text-sm font-medium">Flagged Spam</CardTitle>
                    <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{metrics.flagged_spam}</div>
                    <p className="text-xs text-muted-foreground">
                      {metrics.flagged_spam_change >= 0 ? '+' : ''}{metrics.flagged_spam_change}% from last month
                    </p>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                    <CardTitle className="text-sm font-medium">Spam Rate</CardTitle>
                    <BarChart className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{metrics.spam_rate}%</div>
                    <p className="text-xs text-muted-foreground">
                      Below industry average ({metrics.industry_average}%)
                    </p>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
                    <CardTitle className="text-sm font-medium">Most Active Video</CardTitle>
                    <TrendingUp className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold truncate">
                      {metrics.most_active_video?.title || "No data"}
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {metrics.most_active_video 
                        ? `${metrics.most_active_video.spam_count} spam comments`
                        : "No spam detected"
                      }
                    </p>
                  </CardContent>
                </Card>
              </div>
              
              <div className="grid gap-4 md:grid-cols-3">
                <Card className="md:col-span-2">
                  <CardHeader>
                    <CardTitle>Recent Activity</CardTitle>
                    <CardDescription>
                      Recent spam comments detected on your videos
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {metrics.recent_detections.length > 0 ? (
                        metrics.recent_detections.map((detection) => (
                          <div key={detection.id} className="flex items-start space-x-4 rounded-md border p-3">
                            <AlertTriangle className="mt-1 h-5 w-5 text-amber-500" />
                            <div>
                              <p className="text-sm font-medium">{detection.text}</p>
                              <p className="text-xs text-muted-foreground">{detection.time}</p>
                            </div>
                          </div>
                        ))
                      ) : (
                        <div className="text-center py-4 text-muted-foreground">
                          No recent spam detections
                        </div>
                      )}
                    </div>
                    
                    <Button 
                      variant="outline" 
                      className="w-full mt-4"
                      onClick={handleRefresh}
                      disabled={loading}
                    >
                      {loading ? "Refreshing..." : "Refresh Data"}
                    </Button>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardHeader>
                    <CardTitle>Quick Actions</CardTitle>
                    <CardDescription>
                      Manage your YouTube channel protection
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <Button className="w-full justify-start h-12" variant="outline">
                        <List className="mr-2 h-4 w-4" />
                        View All Comments
                      </Button>
                      <Button className="w-full justify-start h-12" variant="outline">
                        <Shield className="mr-2 h-4 w-4" />
                        Protection Settings
                      </Button>
                      <Button className="w-full justify-start h-12" variant="outline">
                        <BarChart className="mr-2 h-4 w-4" />
                        Analytics
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
            
            <TabsContent value="video-analysis">
              <VideoAnalysisPanel />
            </TabsContent>
          </Tabs>
        </div>
      </main>
      
      <footer className="border-t py-4">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between text-xs text-muted-foreground">
          <div>© 2023 SpamShield. All rights reserved.</div>
          <div>Privacy Policy · Terms of Service</div>
        </div>
      </footer>
    </div>
  );
};

export default Dashboard; 