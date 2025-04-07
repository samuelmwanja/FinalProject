import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { ArrowUp, ArrowDown, Bot, Flag, PlayCircle, BarChart } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: number;
  icon: React.ReactNode;
}

interface MetricsPanelProps {
  metrics?: {
    totalFlagged: number;
    botDetectionRate: number;
    totalComments: number;
    mostTargetedVideos: Array<{ title: string; spamCount: number }>;
  };
}

const MetricCard = ({ title, value, change, icon }: MetricCardProps) => {
  return (
    <Card className="overflow-hidden">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">{title}</p>
            <p className="text-2xl font-bold">{value}</p>
            {typeof change !== "undefined" && (
              <div className="flex items-center space-x-1">
                {change >= 0 ? (
                  <ArrowUp className="h-4 w-4 text-green-500" />
                ) : (
                  <ArrowDown className="h-4 w-4 text-red-500" />
                )}
                <span
                  className={`text-sm ${change >= 0 ? "text-green-500" : "text-red-500"}`}
                >
                  {Math.abs(change)}%
                </span>
              </div>
            )}
          </div>
          <div className="p-3 bg-primary/10 rounded-full">{icon}</div>
        </div>
      </CardContent>
    </Card>
  );
};

const defaultMetrics = {
  totalFlagged: 0,
  botDetectionRate: 0,
  totalComments: 0,
  mostTargetedVideos: [],
};

const MetricsPanel = ({ metrics = defaultMetrics }: MetricsPanelProps) => {
  const hasData = metrics.totalComments > 0;

  // For demo purposes, replace with actual data
  const demoMetrics = {
    totalComments: 1245,
    totalFlagged: 87,
    botDetectionRate: 7,
    mostTargetedVideos: [
      { title: "Tech Reviews #42", spamCount: 42 },
      { title: "Product Launch 2023", spamCount: 28 },
      { title: "Tutorial: Getting Started", spamCount: 15 },
    ],
  };

  const displayMetrics = demoMetrics;

  return (
    <div className="w-full">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          title="Total Comments"
          value={displayMetrics.totalComments}
          change={24}
          icon={<BarChart className="h-6 w-6 text-primary" />}
        />
        <MetricCard
          title="Flagged Spam"
          value={displayMetrics.totalFlagged}
          change={-12}
          icon={<Flag className="h-6 w-6 text-primary" />}
        />
        <MetricCard
          title="Spam Rate"
          value={`${displayMetrics.botDetectionRate}%`}
          icon={<Bot className="h-6 w-6 text-primary" />}
        />
        <Card className="overflow-hidden">
          <CardContent className="p-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-medium">Most Active Video</h3>
                <PlayCircle className="h-6 w-6 text-primary" />
              </div>
              <div className="space-y-1">
                <div className="font-semibold text-xl truncate">{displayMetrics.mostTargetedVideos[0]?.title || "No data"}</div>
                <div className="text-sm text-muted-foreground">
                  {displayMetrics.mostTargetedVideos[0]?.spamCount || 0} comments today
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default MetricsPanel; 