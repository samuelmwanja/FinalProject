import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Filter, Trash2, Flag, Shield, RefreshCw, AlertTriangle } from "lucide-react";
import CommentTable from "./CommentTable";
import { cn } from "@/lib/utils";

interface CommentModerationPanelProps {
  onDelete?: (ids: string[]) => void;
  onReport?: (ids: string[]) => void;
  onWhitelist?: (ids: string[]) => void;
  className?: string;
}

const CommentModerationPanel = ({
  onDelete = () => {},
  onReport = () => {},
  onWhitelist = () => {},
  className,
}: CommentModerationPanelProps) => {
  const [selectedComments, setSelectedComments] = useState<string[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState("all");
  const [isLoading, setIsLoading] = useState(false);

  const handleSelectComment = (id: string) => {
    setSelectedComments((prev) =>
      prev.includes(id)
        ? prev.filter((commentId) => commentId !== id)
        : [...prev, id],
    );
  };

  const handleBulkAction = (action: (ids: string[]) => void) => {
    action(selectedComments);
    setSelectedComments([]);
  };

  const handleRefresh = () => {
    setIsLoading(true);
    // Simulate API call
    setTimeout(() => {
      setIsLoading(false);
    }, 1000);
  };

  // Recent activity items
  const recentActivity = [
    { id: "1", text: "Check out this amazing offer at...", time: "2 hours ago" },
    { id: "2", text: "I made $5000 working from home using...", time: "5 hours ago" },
    { id: "3", text: "Free subscribers at my channel www...", time: "1 day ago" },
  ];

  return (
    <div className={cn("space-y-6", className)}>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Recent spam comments detected on your videos</CardDescription>
          </div>
          <Button 
            variant="outline" 
            size="sm" 
            className="text-xs"
            onClick={handleRefresh}
            disabled={isLoading}
          >
            <RefreshCw className={`h-3 w-3 mr-1 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh Data
          </Button>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentActivity.map((activity) => (
              <div key={activity.id} className="flex items-start space-x-4 rounded-md border p-3">
                <AlertTriangle className="mt-1 h-5 w-5 text-amber-500" />
                <div>
                  <p className="text-sm font-medium">{activity.text}</p>
                  <p className="text-xs text-muted-foreground">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Comment Moderation</CardTitle>
            <CardDescription>Manage spam comments on your videos</CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            <Button 
              variant="outline" 
              size="sm" 
              className="text-xs"
              onClick={handleRefresh}
              disabled={isLoading}
            >
              <RefreshCw className={`h-3 w-3 mr-1 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Button variant="outline" size="sm" className="text-xs">
              <Filter className="h-3 w-3 mr-1" />
              Filters
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col space-y-4">
            {/* Filters and Search */}
            <div className="flex flex-wrap gap-4">
              <div className="flex-1">
                <Input
                  placeholder="Search comments..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full"
                />
              </div>
              <Select value={filterType} onValueChange={setFilterType}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Filter by" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Comments</SelectItem>
                  <SelectItem value="high_risk">High Risk</SelectItem>
                  <SelectItem value="medium_risk">Medium Risk</SelectItem>
                  <SelectItem value="low_risk">Low Risk</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Bulk Actions */}
            <div className="flex gap-2 flex-wrap">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleBulkAction(onDelete)}
                disabled={selectedComments.length === 0}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete Selected
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleBulkAction(onReport)}
                disabled={selectedComments.length === 0}
              >
                <Flag className="h-4 w-4 mr-2" />
                Report Selected
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleBulkAction(onWhitelist)}
                disabled={selectedComments.length === 0}
              >
                <Shield className="h-4 w-4 mr-2" />
                Whitelist Selected
              </Button>
            </div>

            {/* Comments Table */}
            <CommentTable
              selectedComments={selectedComments}
              onSelectComment={handleSelectComment}
              onDelete={(id) => onDelete([id])}
              onReport={(id) => onReport([id])}
              onWhitelist={(id) => onWhitelist([id])}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default CommentModerationPanel; 