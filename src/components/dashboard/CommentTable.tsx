import React from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { MoreVertical, Flag, Trash2, Shield, SearchX } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

interface Comment {
  id: string;
  content: string;
  author: string;
  spamProbability: number;
  timestamp: string;
  videoTitle: string;
}

interface CommentTableProps {
  comments?: Comment[];
  onDelete?: (id: string) => void;
  onReport?: (id: string) => void;
  onWhitelist?: (id: string) => void;
  selectedComments?: string[];
  onSelectComment?: (id: string) => void;
}

// Demo comments for UI display
const demoComments: Comment[] = [
  {
    id: "1",
    content: "Check out this amazing offer at www.fakeoffer.com! 90% discount today only!",
    author: "SpamUser123",
    spamProbability: 0.95,
    timestamp: "2023-05-15T10:30:00Z",
    videoTitle: "Tech Reviews #42"
  },
  {
    id: "2",
    content: "I made $5000 working from home using this secret method! Click here: www.scamlink.com",
    author: "GetRichQuick87",
    spamProbability: 0.89,
    timestamp: "2023-05-15T12:45:00Z",
    videoTitle: "Product Launch 2023"
  },
  {
    id: "3",
    content: "Free subscribers at my channel www.fakechannel.com! Subscribe and get 1000 subs back!",
    author: "SubBooster2023",
    spamProbability: 0.78,
    timestamp: "2023-05-14T18:20:00Z",
    videoTitle: "Tutorial: Getting Started"
  }
];

const CommentTable = ({
  comments = demoComments, // Use demo comments by default
  onDelete = () => {},
  onReport = () => {},
  onWhitelist = () => {},
  selectedComments = [],
  onSelectComment = () => {},
}: CommentTableProps) => {
  const getSpamBadge = (probability: number) => {
    if (probability >= 0.8) {
      return <Badge variant="destructive">High Risk</Badge>;
    } else if (probability >= 0.4) {
      return <Badge variant="warning">Medium Risk</Badge>;
    }
    return <Badge variant="secondary">Low Risk</Badge>;
  };

  return (
    <div className="w-full bg-background border rounded-lg overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[50px]">
              <Checkbox />
            </TableHead>
            <TableHead>Comment</TableHead>
            <TableHead>Author</TableHead>
            <TableHead>Video</TableHead>
            <TableHead>Spam Probability</TableHead>
            <TableHead>Time</TableHead>
            <TableHead className="w-[100px]">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {comments.length > 0 ? (
            comments.map((comment) => (
              <TableRow key={comment.id}>
                <TableCell>
                  <Checkbox
                    checked={selectedComments.includes(comment.id)}
                    onCheckedChange={() => onSelectComment(comment.id)}
                  />
                </TableCell>
                <TableCell className="font-medium max-w-xs truncate">{comment.content}</TableCell>
                <TableCell>{comment.author}</TableCell>
                <TableCell className="max-w-[150px] truncate">{comment.videoTitle}</TableCell>
                <TableCell>{getSpamBadge(comment.spamProbability)}</TableCell>
                <TableCell>
                  {new Date(comment.timestamp).toLocaleDateString()}
                </TableCell>
                <TableCell>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon">
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={() => onDelete(comment.id)}>
                        <Trash2 className="mr-2 h-4 w-4" />
                        Delete
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => onReport(comment.id)}>
                        <Flag className="mr-2 h-4 w-4" />
                        Report
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => onWhitelist(comment.id)}>
                        <Shield className="mr-2 h-4 w-4" />
                        Whitelist
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))
          ) : (
            <TableRow>
              <TableCell colSpan={7} className="text-center py-8">
                <div className="flex flex-col items-center justify-center text-muted-foreground">
                  <SearchX className="h-12 w-12 mb-2" />
                  <p>No comments found</p>
                  <p className="text-sm">Connect your YouTube channel to start monitoring comments</p>
                </div>
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
};

export default CommentTable; 