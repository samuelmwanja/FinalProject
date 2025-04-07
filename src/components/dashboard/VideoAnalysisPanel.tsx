import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Youtube, AlertTriangle, BarChart, MessageCircle, ShieldAlert, Loader2, Info, ThumbsUp, User } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { analyzeYouTubeVideo, fetchYouTubeComments, YouTubeComment, YouTubeAnalysisResponse } from "@/lib/api";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

// Helper function to extract YouTube video ID from URL
const extractVideoId = (url: string): string | null => {
  console.log("Extracting video ID from URL:", url);
  
  if (!url) {
    console.log("Empty URL provided");
    return null;
  }
  
  // Strip any whitespace
  url = url.trim();
  
  // Direct check for the specific video ID 2HRBJCp9XkI
  if (url.includes("2HRBJCp9XkI")) {
    console.log("Found specific video ID 2HRBJCp9XkI in URL");
    return "2HRBJCp9XkI";
  }
  
  // If the URL seems to be just a video ID (no https://, etc.)
  if (url.length >= 5 && url.length <= 30 && !url.includes("/") && !url.includes(".")) {
    // Skip channel handles
    if (url.startsWith("@")) {
      console.log("This appears to be a channel handle, not a video ID:", url);
      return null;
    }
    
    // Check if it matches the standard YouTube ID pattern
    if (/^[a-zA-Z0-9_-]{11}$/.test(url)) {
      console.log("URL appears to be a direct video ID:", url);
      return url;
    }
    
    // Check if it looks like a potential ID with unusual length
    if (/^[a-zA-Z0-9_-]+$/.test(url)) {
      console.log("URL appears to be a direct video ID with unusual length:", url);
      return url;
    }
  }
  
  // Handle shortened youtu.be links
  if (url.includes("youtu.be/")) {
    const parts = url.split("youtu.be/");
    if (parts.length >= 2) {
      const idPart = parts[1].split("?")[0].split("#")[0].split("&")[0];
      if (idPart) {
        console.log("Extracted video ID from youtu.be URL:", idPart);
        return idPart;
      }
    }
  }
  
  try {
    // Comprehensive set of patterns for different YouTube URL formats
    const patterns = [
      // Standard watch URLs
      /(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})(?:&[^&]*)*$/,
      /(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?(?:[^&]*&)*v=([a-zA-Z0-9_-]{11})(?:&[^&]*)*$/,
      // Short URLs
      /(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]{11})(?:\?[^?]*)?$/,
      // Embed URLs
      /(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]{11})(?:\?[^?]*)?$/,
      // HTML5 URLs
      /(?:https?:\/\/)?(?:www\.)?youtube\.com\/v\/([a-zA-Z0-9_-]{11})(?:\?[^?]*)?$/,
      // Share URLs
      /(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})(?:\?[^?]*)?$/,
      // Mobile app URLs
      /(?:https?:\/\/)?(?:www\.)?m\.youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})(?:&[^&]*)*$/,
    ];
    
    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match && match[1]) {
        console.log("Extracted video ID using regex pattern:", match[1]);
        return match[1];
      }
    }
    
    // URL parsing as last resort
    const urlObj = new URL(url);
    const hostname = urlObj.hostname;
    const pathname = urlObj.pathname;
    const searchParams = new URLSearchParams(urlObj.search);
    
    // Handle various hostname and path combinations
    if (hostname.includes('youtu.be')) {
      const id = pathname.split('/')[1];
      console.log("Extracted video ID using youtu.be pathname:", id);
      return id;
    }
    
    if (hostname.includes('youtube.com') || hostname.includes('m.youtube.com')) {
      if (pathname === '/watch') {
        const id = searchParams.get('v');
        if (id) {
          console.log("Extracted video ID from search params:", id);
          return id;
        }
      } else if (pathname.startsWith('/embed/')) {
        const id = pathname.split('/')[2];
        console.log("Extracted video ID from embed path:", id);
        return id;
      } else if (pathname.startsWith('/v/')) {
        const id = pathname.split('/')[2];
        console.log("Extracted video ID from v path:", id);
        return id;
      } else if (pathname.startsWith('/shorts/')) {
        const id = pathname.split('/')[2];
        console.log("Extracted video ID from shorts path:", id);
        return id;
      }
    }
    
    // Last resort: look for an 11-character ID-like pattern in the URL
    const idMatch = url.match(/([a-zA-Z0-9_-]{11})/);
    if (idMatch) {
      console.log("Found potential video ID pattern in URL:", idMatch[1]);
      return idMatch[1];
    }
    
    console.log("Failed to extract video ID from URL");
    return null;
  } catch (error) {
    console.error("Error extracting video ID:", error);
    return null;
  }
};

// Helper function to get risk color based on probability
const getRiskColor = (probability: number): string => {
  if (probability >= 0.7) return "text-red-500";
  if (probability >= 0.4) return "text-amber-500";
  return "text-green-500";
};

// Helper function to get risk badge based on probability
const getRiskBadge = (probability: number, risk_level?: string): JSX.Element => {
  // If risk_level is provided, use it to determine the badge
  if (risk_level) {
    if (risk_level.toLowerCase() === 'high') {
      return <Badge variant="destructive">High Risk</Badge>;
    }
    if (risk_level.toLowerCase() === 'medium') {
      return <Badge variant="warning" className="bg-amber-500">Medium Risk</Badge>;
    }
    return <Badge variant="outline" className="bg-green-100 text-green-800">Low Risk</Badge>;
  }
  
  // Fall back to probability-based determination if risk_level is not provided
  if (probability >= 0.7) {
    return <Badge variant="destructive">High Risk</Badge>;
  }
  if (probability >= 0.4) {
    return <Badge variant="warning" className="bg-amber-500">Medium Risk</Badge>;
  }
  return <Badge variant="outline" className="bg-green-100 text-green-800">Low Risk</Badge>;
};

interface CommentType {
  text: string;
  spam_probability: number;
  risk_level: string;
  method?: string;
  is_spam?: boolean;
}

interface YouTubeCommentType {
  id: string;
  text: string;
  author: string;
  author_profile_image: string;
  author_channel_url: string;
  like_count: number;
  published_at: string;
}

// Using the YouTubeComment type from the API
interface VideoAnalysisProps {
  className?: string;
}

const VideoAnalysisPanel = ({ className }: VideoAnalysisProps) => {
  const { toast } = useToast();
  const [videoUrl, setVideoUrl] = useState("");
  const [videoId, setVideoId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("spam");
  const [youtubeComments, setYoutubeComments] = useState<YouTubeCommentType[]>([]);
  const [spamComments, setSpamComments] = useState<YouTubeComment[]>([]);
  const [nonSpamComments, setNonSpamComments] = useState<YouTubeComment[]>([]);
  const [loadingComments, setLoadingComments] = useState(false);
  const [analyzingComments, setAnalyzingComments] = useState(false);
  const [results, setResults] = useState<null | {
    title: string;
    totalComments: number;
    spamComments: number;
    spamRate: number;
    recentSpam: CommentType[];
    recentNonSpam: CommentType[];
    dataSource?: string;
    warning?: string;
    classifier_method?: string;
  }>(null);

  // Function to fetch YouTube comments
  const fetchComments = async (id: string) => {
    if (!id) return [];
    
    setLoadingComments(true);
    try {
      // Direct YouTube API call
      const API_KEY = 'AIzaSyAkIjS_Z02y-9Cclgv4EgtFFK0CcRa1mcg';
      
      // Array to store all comments
      let allComments: YouTubeCommentType[] = [];
      let commentMap = new Map<string, YouTubeCommentType>(); // Use a map to avoid duplicates
      
      // Helper function to add delay between API calls
      const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));
      
      // Get the total comment count first
      const videoResponse = await fetch(
        `https://www.googleapis.com/youtube/v3/videos?part=statistics&id=${id}&key=${API_KEY}`
      );
      
      if (!videoResponse.ok) {
        throw new Error(`YouTube API error: ${videoResponse.status}`);
      }
      
      const videoData = await videoResponse.json();
      const totalComments = videoData.items && videoData.items[0]?.statistics?.commentCount 
        ? parseInt(videoData.items[0].statistics.commentCount) 
        : 0;
      
      console.log(`Total comments from YouTube statistics: ${totalComments}`);
      
      toast({
        title: "Loading comments",
        description: `Fetching all ${totalComments.toLocaleString()} comments from YouTube...`,
      });
      
      // Try multiple approaches to get all comments
      // Combinations of ordering, textFormat, and moderation settings
      const strategies = [
        { order: 'time', textFormat: 'html' },
        { order: 'relevance', textFormat: 'html' },
        { order: 'time', textFormat: 'plainText' },
        { order: 'relevance', textFormat: 'plainText' },
      ];
      
      // Keep track of total attempts
      let totalAttempts = 0;
      const MAX_TOTAL_ATTEMPTS = 100; // Safety limit to prevent infinite loops
      
      // Define YouTube API response type
      interface YouTubeApiResponse {
        items: Array<{
          id: string;
          snippet: {
            topLevelComment: {
              snippet: {
                textDisplay: string;
                authorDisplayName: string;
                authorProfileImageUrl: string;
                authorChannelUrl: string;
                likeCount: number;
                publishedAt: string;
              }
            }
          }
        }>;
        nextPageToken?: string;
        pageInfo: {
          totalResults: number;
          resultsPerPage: number;
        };
      }
      
      for (const strategy of strategies) {
        console.log(`\n--- Using strategy: order=${strategy.order}, format=${strategy.textFormat} ---`);
        
        let nextPageToken: string | undefined = undefined;
        let previousCount = commentMap.size;
        let consecutiveNoNewComments = 0;
        let pageAttempt = 0;
        
        // Continue fetching pages until we stop getting new comments
        // or hit a reasonable limit
        do {
          pageAttempt++;
          totalAttempts++;
          
          // Show progress periodically
          if (totalAttempts % 2 === 0 || commentMap.size > previousCount + 50) {
            toast({
              title: "Loading comments",
              description: `Loaded ${commentMap.size.toLocaleString()} of ${totalComments.toLocaleString()} comments (${Math.round((commentMap.size / totalComments) * 100)}%)`,
            });
            previousCount = commentMap.size;
          }
          
          // Use all parameters to maximize the chance of getting different comments
          const apiUrlString = `https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId=${id}&maxResults=100&order=${strategy.order}&textFormat=${strategy.textFormat}&key=${API_KEY}${nextPageToken ? `&pageToken=${nextPageToken}` : ''}`;
          
          console.log(`[${strategy.order}/${strategy.textFormat}] Fetching page ${pageAttempt}, comments so far: ${commentMap.size}`);
          
          try {
            const response = await fetch(apiUrlString);
            
            if (!response.ok) {
              const errorText = await response.text();
              console.error(`API error (${response.status}): ${errorText}`);
              
              if (response.status === 403) {
                console.log("Quota limit reached, pausing for longer...");
                await delay(2000);
                continue; // Try again
              }
              
              // If we get a 400 error, the API might be rejecting our request parameters
              // Skip to the next strategy
              if (response.status === 400) {
                console.log("Invalid request, skipping to next strategy");
                break;
              }
              
              throw new Error(`YouTube API error: ${response.status} - ${errorText}`);
            }
            
            const responseData: YouTubeApiResponse = await response.json();
            
            console.log(`[${strategy.order}/${strategy.textFormat}] Got ${responseData.items?.length || 0} comments, nextPageToken: ${responseData.nextPageToken ? 'yes' : 'no'}`);
            
            let newCommentsInPage = 0;
            
            if (responseData.items && responseData.items.length > 0) {
              responseData.items.forEach((item) => {
                const snippet = item.snippet.topLevelComment.snippet;
                if (!commentMap.has(item.id)) {
                  newCommentsInPage++;
                  commentMap.set(item.id, {
                    id: item.id,
                    text: snippet.textDisplay,
                    author: snippet.authorDisplayName,
                    author_profile_image: snippet.authorProfileImageUrl,
                    author_channel_url: snippet.authorChannelUrl,
                    like_count: snippet.likeCount,
                    published_at: snippet.publishedAt
                  });
                }
              });
              
              console.log(`[${strategy.order}/${strategy.textFormat}] Added ${newCommentsInPage} new comments, total now: ${commentMap.size}`);
              
              // If we've added new comments, reset the counter
              if (newCommentsInPage > 0) {
                consecutiveNoNewComments = 0;
              } else {
                consecutiveNoNewComments++;
                console.log(`No new comments for ${consecutiveNoNewComments} consecutive pages`);
              }
            } else {
              console.log(`[${strategy.order}/${strategy.textFormat}] No comments returned`);
              consecutiveNoNewComments++;
            }
            
            // Get the token for the next page
            nextPageToken = responseData.nextPageToken;
            
            // Add a delay to avoid rate limiting
            await delay(300);
            
            // Stop conditions:
            // 1. We've reached a high percentage of total comments
            // 2. We've had too many pages with no new comments
            // 3. We've hit the total attempt limit for safety
            if (commentMap.size >= totalComments * 0.99) {
              console.log(`Reached ${commentMap.size}/${totalComments} comments (99%), stopping`);
              break;
            }
            
            if (consecutiveNoNewComments >= 3) {
              console.log(`No new comments for 3 consecutive pages, trying next strategy`);
              break;
            }
            
            if (totalAttempts >= MAX_TOTAL_ATTEMPTS) {
              console.log(`Reached maximum total attempts (${MAX_TOTAL_ATTEMPTS}), stopping`);
              break;
            }
            
          } catch (error) {
            console.error(`Error fetching page ${pageAttempt} with strategy ${strategy.order}/${strategy.textFormat}:`, error);
            // Continue to the next strategy on error
            break;
          }
          
        } while (nextPageToken);
        
        // If we're close enough to the total, stop trying more strategies
        if (commentMap.size >= totalComments * 0.99) {
          console.log(`Reached ${commentMap.size}/${totalComments} comments (99%), stopping all strategies`);
          break;
        }
        
        // Add a longer delay between strategies
        await delay(1000);
      }
      
      // In a final attempt, try to get the specific remaining comments if we're missing some
      // by using direct comment IDs (if we have this information)
      
      // Convert the map to an array
      allComments = Array.from(commentMap.values());
      
      // Sort comments by published date
      allComments.sort((a, b) => new Date(b.published_at).getTime() - new Date(a.published_at).getTime());
      
      console.log(`Finished fetching comments: ${allComments.length} of ${totalComments} total`);
      
      // Update state with all fetched comments
      setYoutubeComments(allComments);
      
      // Automatically switch to the YouTube comments tab when comments are loaded
      setActiveTab("youtube-comments");
      
      // Show success toast with comment count and percentage
      const percentComplete = Math.round((allComments.length / totalComments) * 100);
      
      toast({
        title: "Comments loaded",
        description: `Loaded ${allComments.length.toLocaleString()} of ${totalComments.toLocaleString()} comments (${percentComplete}%)`,
      });
      
      // Return the comments for use in the calling function
      return allComments;
    } catch (error) {
      console.error("Error fetching YouTube comments:", error);
      toast({
        title: "Error fetching comments",
        description: error instanceof Error ? error.message : "Could not fetch YouTube comments",
        variant: "destructive",
      });
      return [];
    } finally {
      setLoadingComments(false);
    }
  };

  // Function to process fetched comments through spam detection model
  const processCommentsWithSpamModel = async (
    comments: YouTubeCommentType[],
    videoUrl: string
  ) => {
    if (!comments.length) return;
    
    setAnalyzingComments(true);
    
    try {
      toast({
        title: "Processing comments",
        description: `Analyzing ${comments.length.toLocaleString()} comments for spam...`,
      });
      
      // Call the backend API to analyze the video
      const analysisResult = await analyzeYouTubeVideo(videoUrl);
      
      if (analysisResult.error) {
        throw new Error(analysisResult.error);
      }
      
      // Process each comment and classify based on the analysis data
      const processedSpamComments: YouTubeComment[] = [];
      const processedNonSpamComments: YouTubeComment[] = [];
      
      // Helper function to check if a comment is similar to a analyzed comment
      const isSimilarComment = (commentText: string, analysisText: string) => {
        // Simple similarity check - could be improved
        const normalizedComment = commentText.toLowerCase().replace(/<[^>]*>/g, '').trim();
        const normalizedAnalysis = analysisText.toLowerCase().trim();
        
        // Check if one is a substring of the other or if they're highly similar
        return normalizedComment.includes(normalizedAnalysis) || 
               normalizedAnalysis.includes(normalizedComment) ||
               (normalizedComment.length > 10 && normalizedAnalysis.length > 10 && 
                (normalizedComment.substring(0, 15) === normalizedAnalysis.substring(0, 15)));
      };
      
      // First, match comments with analyzed examples
      const matchedCommentIds = new Set<string>();
      
      // Match with spam examples
      analysisResult.recent_spam?.forEach(spamExample => {
        comments.forEach(comment => {
          if (!matchedCommentIds.has(comment.id) && isSimilarComment(comment.text, spamExample.text)) {
            matchedCommentIds.add(comment.id);
            processedSpamComments.push({
              ...comment,
              spam_probability: spamExample.spam_probability,
              risk_level: spamExample.risk_level,
              method: spamExample.method || 'ml-model',
              is_spam: true
            });
          }
        });
      });
      
      // Match with non-spam examples
      analysisResult.recent_non_spam?.forEach(nonSpamExample => {
        comments.forEach(comment => {
          if (!matchedCommentIds.has(comment.id) && isSimilarComment(comment.text, nonSpamExample.text)) {
            matchedCommentIds.add(comment.id);
            processedNonSpamComments.push({
              ...comment,
              spam_probability: nonSpamExample.spam_probability,
              risk_level: nonSpamExample.risk_level,
              method: nonSpamExample.method || 'ml-model',
              is_spam: false
            });
          }
        });
      });
      
      // For unmapped comments, use simple heuristics to classify
      const unmappedComments = comments.filter(comment => !matchedCommentIds.has(comment.id));
      
      // Simple rule-based classification for remaining comments
      unmappedComments.forEach(comment => {
        const text = comment.text.toLowerCase();
        // Simple spam indicators
        const spamIndicators = [
          'check out my channel', 'subscribe to my', 'check my profile',
          'make money', 'earn cash', 'get followers', 'subscribe and i will',
          'free followers', 'free subscribers', 'watch my video', 'visit my channel',
          'click here', 'follow me', 'check this out', 'check my page',
          'easy money', 'get rich', 'work from home', 'make $', '@',
          'earn online', 'dm me', 'dm for', 'message me', 'private message'
        ];
        
        // Count how many indicators are present
        let spamScore = 0;
        spamIndicators.forEach(indicator => {
          if (text.includes(indicator)) {
            spamScore += 1;
          }
        });
        
        // Normalize to probability
        const normalizedProbability = Math.min(0.3 + (spamScore / spamIndicators.length) * 0.7, 1);
        
        // Determine risk level
        let riskLevel = 'low';
        if (normalizedProbability >= 0.7) {
          riskLevel = 'high';
        } else if (normalizedProbability >= 0.4) {
          riskLevel = 'medium';
        }
        
        // Add to appropriate list
        if (normalizedProbability >= 0.5) {
          processedSpamComments.push({
            ...comment,
            spam_probability: normalizedProbability,
            risk_level: riskLevel,
            method: 'rule-based',
            is_spam: true
          });
        } else {
          processedNonSpamComments.push({
            ...comment,
            spam_probability: normalizedProbability,
            risk_level: riskLevel,
            method: 'rule-based',
            is_spam: false
          });
        }
      });
      
      // Sort by probability (highest first for spam, lowest first for non-spam)
      processedSpamComments.sort((a, b) => b.spam_probability - a.spam_probability);
      processedNonSpamComments.sort((a, b) => a.spam_probability - b.spam_probability);
      
      // Update state with processed comments
      setSpamComments(processedSpamComments);
      setNonSpamComments(processedNonSpamComments);
      
      // Update results with new analysis data
      setResults({
        title: analysisResult.title,
        totalComments: analysisResult.total_comments || comments.length,
        spamComments: processedSpamComments.length,
        spamRate: Math.round((processedSpamComments.length / comments.length) * 100),
        recentSpam: analysisResult.recent_spam || [],
        recentNonSpam: analysisResult.recent_non_spam || [],
        dataSource: analysisResult.data_source,
        warning: analysisResult.warning,
        classifier_method: analysisResult.classifier_method || "hybrid"
      });
      
      toast({
        title: "Analysis Complete",
        description: `Identified ${processedSpamComments.length} spam comments out of ${comments.length} total comments`,
      });
      
    } catch (error) {
      console.error("Error analyzing comments for spam:", error);
      toast({
        title: "Error analyzing comments",
        description: error instanceof Error ? error.message : "Failed to process comments through spam detection",
        variant: "destructive",
      });
      
      // Fallback: Use very basic rule-based classification
      const basicClassifiedSpam: YouTubeComment[] = [];
      const basicClassifiedNonSpam: YouTubeComment[] = [];
      
      comments.forEach(comment => {
        const text = comment.text.toLowerCase();
        const basicSpamWords = ['subscribe', 'channel', 'check out', 'follow', 'dm', 'money', 'free', 'click'];
        
        let spamScore = 0;
        basicSpamWords.forEach(word => {
          if (text.includes(word)) spamScore += 1;
        });
        
        const probability = Math.min(spamScore / basicSpamWords.length, 1);
        const riskLevel = probability > 0.7 ? 'high' : probability > 0.4 ? 'medium' : 'low';
        
        if (probability > 0.5) {
          basicClassifiedSpam.push({
            ...comment, 
            spam_probability: probability,
            risk_level: riskLevel,
            method: 'basic-rule',
            is_spam: true
          });
        } else {
          basicClassifiedNonSpam.push({
            ...comment,
            spam_probability: probability,
            risk_level: riskLevel,
            method: 'basic-rule',
            is_spam: false
          });
        }
      });
      
      setSpamComments(basicClassifiedSpam);
      setNonSpamComments(basicClassifiedNonSpam);
      
      // Update results with basic analysis
      if (!results) {
        setResults({
          title: "YouTube Video Analysis",
          totalComments: comments.length,
          spamComments: basicClassifiedSpam.length,
          spamRate: Math.round((basicClassifiedSpam.length / comments.length) * 100),
          recentSpam: [],
          recentNonSpam: [],
          dataSource: "client_side",
          warning: "Using simplified spam detection due to backend error",
          classifier_method: "basic-rule"
        });
      }
    } finally {
      setAnalyzingComments(false);
    }
  };

  // Video Analysis
  const handleAnalyze = async () => {
    try {
      if (!videoUrl.trim()) {
        toast({
          title: "URL Required",
          description: "Please enter a YouTube video URL",
          variant: "destructive"
        });
        return;
      }
      
      // Set loading state
      setLoading(true);
      console.log("Starting analysis of URL:", videoUrl);
      
      // Extract video ID from URL
      const id = extractVideoId(videoUrl);
      console.log("Extracted video ID:", id);
      
      // Validate the extracted ID
      if (!id) {
        console.error("Failed to extract valid YouTube video ID");
        toast({
          title: "Invalid URL",
          description: "Could not extract a valid YouTube video ID",
          variant: "destructive"
        });
        setLoading(false);
        return;
      }
      
      // Set video ID state (triggers iframe update)
      setVideoId(id);
      
      // Use the shared API function that works with both endpoints
      try {
        console.log("Calling analyzeYouTubeVideo from API with URL:", videoUrl);
        const analysisResponse = await analyzeYouTubeVideo(videoUrl);
        console.log("Received analysis response:", analysisResponse);
        
        if (analysisResponse) {
          // Update results state
          setResults({
            title: analysisResponse.title || "YouTube Video",
            totalComments: analysisResponse.total_comments || 0,
            spamComments: analysisResponse.spam_comments || 0,
            spamRate: analysisResponse.spam_rate || 0,
            recentSpam: analysisResponse.recent_spam || [],
            recentNonSpam: analysisResponse.recent_non_spam || [],
            dataSource: analysisResponse.data_source || "api",
            warning: analysisResponse.warning,
            classifier_method: analysisResponse.classifier_method || "hybrid"
          });
          
          // Also update comments lists
          if (analysisResponse.comments) {
            const spamComments = analysisResponse.comments
              .filter(c => c.is_spam)
              .map(c => ({
                ...c,
                method: c.method || 'ml-model',
                is_spam: c.is_spam || false
              }));
              
            const nonSpamComments = analysisResponse.comments
              .filter(c => !c.is_spam)
              .map(c => ({
                ...c,
                method: c.method || 'ml-model',
                is_spam: c.is_spam || false
              }));
              
            setSpamComments(spamComments);
            setNonSpamComments(nonSpamComments);
          }
          
          toast({
            title: "Analysis Complete",
            description: `Found ${analysisResponse.spam_comments} spam comments out of ${analysisResponse.total_comments} total`,
          });
        }
      } catch (apiError) {
        console.error("API Error:", apiError);
        toast({
          title: "API Error",
          description: apiError instanceof Error ? apiError.message : "Failed to analyze video",
          variant: "destructive"
        });
        
        // Fallback to direct YouTube comments as before
        toast({
          title: "Trying alternate method",
          description: "Attempting to fetch comments directly from YouTube...",
        });
        
        // First attempt: directly use the backend API
        const youtubeComments = await fetchComments(id);
        if (youtubeComments && youtubeComments.length > 0) {
          await processCommentsWithSpamModel(youtubeComments, videoUrl);
        } else {
          toast({
            title: "No Comments Found",
            description: "Could not retrieve comments for this video",
            variant: "destructive"
          });
        }
      }
      
    } catch (error) {
      console.error("Error analyzing video:", error);
      toast({
        title: "Analysis Failed",
        description: error instanceof Error ? error.message : "An unknown error occurred",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  // Function to render a comment
  const renderComment = (comment: CommentType, index: number) => (
    <div key={index} className="p-4 hover:bg-muted/50 transition-colors">
      <div className="flex items-start gap-3">
        <div className="mt-0.5 shrink-0">
          {comment.spam_probability > 0.5 ? (
            <AlertTriangle className={`h-5 w-5 ${getRiskColor(comment.spam_probability)}`} />
          ) : (
            <ThumbsUp className="h-5 w-5 text-green-500" />
          )}
        </div>
        <div className="flex-1">
          <div className="flex justify-between items-center mb-1">
            <p className="font-medium">Comment {index + 1}</p>
            <div className="flex items-center gap-2">
              {comment.method && (
                <Badge variant="outline" className={`text-xs ${
                  comment.method === "ml-model" ? "bg-blue-50 text-blue-700" : "bg-purple-50 text-purple-700"
                }`}>
                  {comment.method === "ml-model" ? "ML" : "Rule-based"}
                </Badge>
              )}
              {getRiskBadge(comment.spam_probability, comment.risk_level)}
            </div>
          </div>
          <p className="text-sm mb-2">{comment.text}</p>
          <div className="w-full bg-secondary/50 rounded-full h-1.5 overflow-hidden">
            <div
              className={`h-full ${comment.spam_probability > 0.7 ? 'bg-red-500' : comment.spam_probability > 0.4 ? 'bg-amber-500' : 'bg-green-500'}`}
              style={{ width: `${comment.spam_probability * 100}%` }}
            ></div>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Spam probability: {(comment.spam_probability * 100).toFixed(1)}%
          </p>
        </div>
      </div>
    </div>
  );

  // Function to render a YouTube comment with spam probability
  const renderYouTubeCommentWithSpam = (
    comment: YouTubeComment, 
    index: number
  ) => (
    <div key={`youtube-comment-${index}`} className="mb-4 p-3 bg-white dark:bg-gray-800 border rounded-lg shadow-sm">
      <div className="flex items-start space-x-3">
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="font-medium">{comment.author || "Anonymous"}</span>
              <span className="text-xs text-gray-500">
                {comment.published_at ? new Date(comment.published_at).toLocaleDateString() : "Unknown date"}
              </span>
            </div>
            <div className="flex items-center space-x-2">
              {getRiskBadge(comment.spam_probability, comment.risk_level)}
              <Badge variant="outline" className="bg-blue-100 text-blue-800">{comment.method || "Model"}</Badge>
            </div>
          </div>
          <p className="mt-1 text-sm text-gray-700 dark:text-gray-300">{comment.text}</p>
          <div className="mt-2 text-xs text-gray-500 flex justify-between items-center">
            <span className={`${getRiskColor(comment.spam_probability)} font-semibold`}>
              Spam probability: {(comment.spam_probability * 100).toFixed(0)}%
            </span>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Youtube className="mr-2 h-5 w-5 text-red-500" />
          YouTube Video Analysis
        </CardTitle>
        <CardDescription>
          Test spam detection on any YouTube video using ML model
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="Enter YouTube video URL (e.g., https://www.youtube.com/watch?v=...)"
              value={videoUrl}
              onChange={(e) => setVideoUrl(e.target.value)}
              className="flex-1"
              disabled={loading}
            />
            <Button onClick={handleAnalyze} disabled={loading || !videoUrl}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                "Analyze"
              )}
            </Button>
          </div>

          {loading && !results && (
            <div className="my-8 text-center">
              <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
              <p className="text-muted-foreground">Analyzing YouTube comments...</p>
              <Progress value={45} className="h-1 mt-4" />
            </div>
          )}

          {videoId && results && (
            <div className="mt-6 space-y-6">
              {results.dataSource === "mock_data" && (
                <Alert variant="warning" className="bg-amber-50 border-amber-200">
                  <AlertTriangle className="h-4 w-4 text-amber-600" />
                  <AlertTitle className="text-amber-800">Using estimated data</AlertTitle>
                  <AlertDescription className="text-amber-700">
                    For accurate analysis, configure a YouTube API key in the backend.
                    <br/>
                    <strong>Note:</strong> Your API key must be properly loaded in the environment.
                  </AlertDescription>
                </Alert>
              )}

              {/* Video iframe */}
              <div className="rounded-lg overflow-hidden border">
                <div className="bg-muted p-2 border-b">
                  <h3 className="font-medium truncate">{results.title}</h3>
                </div>
                <div className="aspect-video">
                  <iframe
                    width="100%"
                    height="100%"
                    src={`https://www.youtube.com/embed/${videoId}`}
                    title="YouTube video player"
                    frameBorder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                  ></iframe>
                </div>
              </div>

              {/* Stats cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card className="overflow-hidden">
                  <div className="bg-blue-50 dark:bg-blue-950 p-3 flex items-center justify-between">
                    <CardTitle className="text-sm font-medium">Total Comments</CardTitle>
                    <MessageCircle className="h-4 w-4 text-blue-500" />
                  </div>
                  <CardContent className="p-4">
                    <p className="text-2xl font-bold">{results.totalComments}</p>
                    {results.dataSource === "mock_data" && (
                      <p className="text-xs text-amber-600 mt-1 flex items-center">
                        <Info className="h-3 w-3 mr-1" /> Estimated count
                      </p>
                    )}
                  </CardContent>
                </Card>
                
                <Card className="overflow-hidden">
                  <div className="bg-amber-50 dark:bg-amber-950 p-3 flex items-center justify-between">
                    <CardTitle className="text-sm font-medium">Spam Comments</CardTitle>
                    <ShieldAlert className="h-4 w-4 text-amber-500" />
                  </div>
                  <CardContent className="p-4">
                    <p className="text-2xl font-bold">{results.spamComments}</p>
                    {results.dataSource === "mock_data" && (
                      <p className="text-xs text-amber-600 mt-1 flex items-center">
                        <Info className="h-3 w-3 mr-1" /> Estimated count
                      </p>
                    )}
                  </CardContent>
                </Card>
                
                <Card className="overflow-hidden">
                  <div className="bg-red-50 dark:bg-red-950 p-3 flex items-center justify-between">
                    <CardTitle className="text-sm font-medium">Spam Rate</CardTitle>
                    <BarChart className="h-4 w-4 text-red-500" />
                  </div>
                  <CardContent className="p-4">
                    <p className="text-2xl font-bold">{results.spamRate}%</p>
                    <Progress
                      value={results.spamRate}
                      max={100}
                      className="h-2 mt-2"
                      indicatorClassName={
                        results.spamRate > 20 
                          ? "bg-red-500" 
                          : results.spamRate > 10 
                            ? "bg-amber-500" 
                            : "bg-green-500"
                      }
                    />
                  </CardContent>
                </Card>
              </div>

              {/* Comments section with tabs */}
              <div className="border rounded-lg overflow-hidden">
                <div className="bg-muted p-3 border-b flex items-center justify-between">
                  <h3 className="font-medium">Detected Comments</h3>
                  <div className="flex items-center gap-2">
                    {results.classifier_method && (
                      <Badge variant="outline" className={
                        results.classifier_method === "ml-model" 
                          ? "bg-blue-100 text-blue-800" 
                          : "bg-purple-100 text-purple-800"
                      }>
                        {results.classifier_method === "ml-model" ? "ML Model" : "Rule-based"}
                      </Badge>
                    )}
                  </div>
                </div>
                
                <Tabs defaultValue="spam" value={activeTab} onValueChange={setActiveTab} className="w-full">
                  <div className="px-4 py-2 border-b">
                    <TabsList className="grid grid-cols-3 w-[600px]">
                      <TabsTrigger value="spam" className="flex items-center gap-2">
                        <AlertTriangle className="h-4 w-4" />
                        <span>Spam</span>
                        <Badge variant="secondary">{spamComments.length || results.recentSpam.length}</Badge>
                      </TabsTrigger>
                      <TabsTrigger value="not-spam" className="flex items-center gap-2">
                        <ThumbsUp className="h-4 w-4" />
                        <span>Not Spam</span>
                        <Badge variant="secondary">{nonSpamComments.length || results.recentNonSpam.length}</Badge>
                      </TabsTrigger>
                      <TabsTrigger value="youtube-comments" className="flex items-center gap-2">
                        <Youtube className="h-4 w-4" />
                        <span>YouTube Comments</span>
                        <Badge variant="secondary">{youtubeComments.length}</Badge>
                      </TabsTrigger>
                    </TabsList>
                  </div>
                  
                  <TabsContent value="spam" className="focus-visible:outline-none">
                    {analyzingComments ? (
                      <div className="p-8 text-center">
                        <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
                        <p className="text-muted-foreground">Analyzing comments for spam...</p>
                      </div>
                    ) : spamComments.length > 0 ? (
                      <div className="divide-y max-h-[600px] overflow-y-auto">
                        {spamComments.map((comment, index) => renderYouTubeCommentWithSpam(comment, index))}
                      </div>
                    ) : results.recentSpam.length > 0 ? (
                      <div className="divide-y">
                        {results.recentSpam.map((comment, index) => renderComment(comment, index))}
                      </div>
                    ) : (
                      <div className="p-8 text-center text-muted-foreground">
                        <ShieldAlert className="h-8 w-8 mx-auto mb-2 opacity-50" />
                        <p>No spam comments detected</p>
                      </div>
                    )}
                  </TabsContent>
                  
                  <TabsContent value="not-spam" className="focus-visible:outline-none">
                    {analyzingComments ? (
                      <div className="p-8 text-center">
                        <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
                        <p className="text-muted-foreground">Analyzing comments for spam...</p>
                      </div>
                    ) : nonSpamComments.length > 0 ? (
                      <div className="divide-y max-h-[600px] overflow-y-auto">
                        {nonSpamComments.map((comment, index) => renderYouTubeCommentWithSpam(comment, index))}
                      </div>
                    ) : results.recentNonSpam.length > 0 ? (
                      <div className="divide-y">
                        {results.recentNonSpam.map((comment, index) => renderComment(comment, index))}
                      </div>
                    ) : (
                      <div className="p-8 text-center text-muted-foreground">
                        <ThumbsUp className="h-8 w-8 mx-auto mb-2 opacity-50" />
                        <p>No non-spam comments found</p>
                      </div>
                    )}
                  </TabsContent>
                  
                  <TabsContent value="youtube-comments" className="focus-visible:outline-none">
                    {loadingComments ? (
                      <div className="p-8 text-center">
                        <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
                        <p className="text-muted-foreground">Loading YouTube comments...</p>
                        <p className="text-xs text-muted-foreground mt-2">
                          This may take a while for videos with many comments
                        </p>
                        {/* Show comment counter during loading */}
                        {youtubeComments.length > 0 && (
                          <div className="mt-4 mb-6">
                            <div className="flex justify-center items-center gap-2 mb-2">
                              <p className="text-sm font-medium">{youtubeComments.length.toLocaleString()}</p>
                              <p className="text-xs text-muted-foreground">comments loaded so far</p>
                              {results?.totalComments && (
                                <Badge variant="outline" className="ml-2">
                                  {Math.round((youtubeComments.length / results.totalComments) * 100)}%
                                </Badge>
                              )}
                            </div>
                            <Progress 
                              value={youtubeComments.length} 
                              max={results?.totalComments || 100} 
                              className="h-1.5 mt-2 w-64 mx-auto"
                              indicatorClassName="bg-blue-500"
                            />
                            {results?.totalComments && (
                              <p className="text-xs text-muted-foreground mt-2">
                                Target: {results.totalComments.toLocaleString()} total comments
                              </p>
                            )}
                          </div>
                        )}
                        {youtubeComments.length > 0 && (
                          <div className="divide-y max-h-[300px] overflow-y-auto border rounded-md mt-4 bg-background/50 text-left">
                            <p className="p-2 text-xs text-center text-muted-foreground border-b">Preview of comments loaded so far:</p>
                            {youtubeComments.slice(-5).map((comment: YouTubeCommentType, index: number) => {
                              // Convert YouTubeCommentType to YouTubeComment
                              const commentWithSpam: YouTubeComment = {
                                id: comment.id,
                                text: comment.text,
                                author: comment.author,
                                published_at: comment.published_at,
                                spam_probability: 0,
                                risk_level: 'low',
                                method: 'pending',
                                is_spam: false
                              };
                              return renderYouTubeCommentWithSpam(commentWithSpam, index);
                            })}
                          </div>
                        )}
                      </div>
                    ) : youtubeComments.length > 0 ? (
                      <>
                        <div className="p-3 bg-muted/50 border-b">
                          <p className="text-sm text-center">
                            Showing {youtubeComments.length.toLocaleString()} comments
                            {results?.totalComments && youtubeComments.length < results.totalComments && (
                              <>
                                <span className="text-muted-foreground"> (out of {results.totalComments.toLocaleString()} total)</span>
                                
                                {/* Show special message if we've fetched most but not all comments */}
                                {youtubeComments.length >= results.totalComments * 0.65 && youtubeComments.length < results.totalComments * 0.98 && (
                                  <div className="mt-1 text-xs text-amber-500 flex items-center justify-center">
                                    <Info className="h-3 w-3 mr-1" />
                                    <span>YouTube API limits prevent retrieving all comments. We've fetched {Math.round((youtubeComments.length / results.totalComments) * 100)}% of them.</span>
                                  </div>
                                )}
                              </>
                            )}
                          </p>
                        </div>
                        <div className="divide-y max-h-[600px] overflow-y-auto">
                          {youtubeComments.map((comment: YouTubeCommentType, index: number) => {
                            // Convert YouTubeCommentType to YouTubeComment
                            const commentWithSpam: YouTubeComment = {
                              id: comment.id,
                              text: comment.text,
                              author: comment.author,
                              published_at: comment.published_at,
                              spam_probability: 0,
                              risk_level: 'low',
                              method: 'pending',
                              is_spam: false
                            };
                            return renderYouTubeCommentWithSpam(commentWithSpam, index);
                          })}
                        </div>
                      </>
                    ) : (
                      <div className="p-8 text-center text-muted-foreground">
                        <Youtube className="h-8 w-8 mx-auto mb-2 opacity-50" />
                        <p>No comments found for this video</p>
                      </div>
                    )}
                  </TabsContent>
                </Tabs>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default VideoAnalysisPanel; 