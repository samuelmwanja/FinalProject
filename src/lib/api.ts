// API service for interacting with the backend

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:7777/api/v1';
const FLASK_API_URL = import.meta.env.VITE_FLASK_API_URL || 'http://localhost:5000/api';

// Helper function to get the auth token
const getAuthToken = () => localStorage.getItem('authToken');

// Helper for making authenticated API requests
async function authFetch(endpoint: string, options: RequestInit = {}) {
  const token = getAuthToken();
  
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    ...options.headers
  };
  
  try {
    console.log(`Making API request to: ${API_URL}${endpoint}`);
    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
      credentials: 'same-origin', // Changed from include to same-origin to avoid CORS preflight
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        message: `HTTP error! status: ${response.status}`
      }));
      console.error(`API error: ${response.statusText}`, errorData);
      throw new Error(errorData.message || errorData.detail || `API error: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error in API request to ${endpoint}:`, error);
    throw error;
  }
}

// Authentication
export async function login(email: string, password: string) {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);
  
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: `HTTP error! status: ${response.status}`
    }));
    throw new Error(error.detail || `Login failed: ${response.statusText}`);
  }
  
  const data = await response.json();
  return data;
}

export async function register(email: string, password: string, fullName: string) {
  const response = await fetch(`${API_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      email,
      password,
      full_name: fullName
    })
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({
      detail: `HTTP error! status: ${response.status}`
    }));
    throw new Error(error.detail || `Registration failed: ${response.statusText}`);
  }
  
  const data = await response.json();
  return data;
}

export async function getCurrentUser() {
  return authFetch('/auth/me');
}

// Dashboard Metrics
export async function fetchDashboardMetrics() {
  try {
    return await authFetch('/metrics/dashboard');
  } catch (error) {
    console.error('Error fetching dashboard metrics:', error);
    // Return default data when API fails
    return {
      total_comments: 0,
      flagged_spam: 0,
      spam_rate: 0,
      total_comments_change: 0,
      flagged_spam_change: 0,
      industry_average: 12,
      most_active_video: null,
      recent_detections: []
    };
  }
}

// Define the comment type
export interface YouTubeComment {
  id: string;
  text: string;
  author: string;
  published_at: string;
  spam_probability: number;
  risk_level: string;
  method: string;
  is_spam: boolean;
}

// Define the YouTube analysis response interface
export interface YouTubeAnalysisResponse {
  video_id: string;
  title: string;
  total_count: number;
  spam_count: number;
  spam_rate: number;
  comments: YouTubeComment[];
  is_mock_data?: boolean;
  error?: string;
  
  // Fields from our new server format
  analyzed_comments?: number;
  ml_classified_count?: number;
  rule_classified_count?: number;
  
  // Legacy fields for backward compatibility
  total_comments?: number;
  spam_comments?: number;
  recent_spam?: Array<{
    text: string;
    author?: string;
    published_at?: string;
    spam_probability: number;
    risk_level: string;
    is_spam: boolean;
    method: string;
  }>;
  recent_non_spam?: Array<{
    text: string;
    author?: string;
    published_at?: string;
    spam_probability: number;
    risk_level: string;
    is_spam: boolean;
    method: string;
  }>;
  classifier_method?: string;
  data_source?: string;
  warning?: string;
}

// Define the comment type from the Flask endpoint
interface FlaskYouTubeComment {
  id: string;
  text: string;
  author: string;
  published_at: string;
  is_spam: boolean;
  confidence: number;
  ml_is_spam: boolean;
  rule_is_spam: boolean;
  ml_confidence: number;
  rule_confidence: number;
}

// YouTube Video Analysis
export async function analyzeYouTubeVideo(videoUrl: string, maxComments?: number): Promise<YouTubeAnalysisResponse> {
  try {
    console.log(`Sending analysis request for URL: ${videoUrl} with max_comments: ${maxComments === undefined ? 'all' : maxComments}`);
    
    // Use our FastAPI endpoint on port 7777
    const apiUrl = `http://localhost:7777/api/v1/youtube/analyze`;
    
    console.log(`Sending request to: ${apiUrl}`);
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        video_url: videoUrl, 
        max_comments: maxComments 
      }),
      credentials: 'omit', // Don't send cookies for cross-origin requests
      mode: 'cors',       // Explicitly request CORS mode
    });
    
    // Debug the response
    if (!response.ok) {
      console.error(`API request failed with status: ${response.status} ${response.statusText}`);
      const errorContent = await response.text();
      console.error(`Error content: ${errorContent}`);
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }
    
    const result = await response.json();
    console.log("Received API response:", result);
    
    // Format and return the response
    return {
      ...result,
      video_id: result.video_id || '',
      title: result.title || 'YouTube Video',
      total_count: result.total_comments || 0,
      spam_count: result.spam_comments || 0,
      comments: result.comments || [],
      spam_rate: result.spam_rate || 0,
    };
  } catch (error) {
    console.error('Error analyzing YouTube video:', error);
    // Return a formatted error response
    return {
      video_id: '',
      title: 'Error analyzing video',
      total_count: 0,
      spam_count: 0,
      spam_rate: 0,
      comments: [],
      is_mock_data: false,
      error: error instanceof Error ? error.message : String(error)
    };
  }
}

// Videos
export async function fetchVideos(page: number = 1, limit: number = 10) {
  return authFetch(`/youtube/videos`);
}

export async function fetchVideoDetails(videoId: string) {
  return authFetch(`/youtube/videos/${videoId}`);
}

// YouTube Comments
export async function fetchYouTubeComments(videoId: string) {
  return authFetch(`/youtube/videos/${videoId}/comments`);
}

// Modified to use our new endpoint that properly classifies comments
export async function fetchClassifiedComments(videoId: string) {
  return fetch(`/api/v1/youtube/videos/${videoId}/comments`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    }
  }).then(res => {
    if (!res.ok) throw new Error('Failed to fetch classified comments');
    return res.json();
  });
}

// Comments
export async function fetchComments(videoId: string = '', riskLevel: string = '', page: number = 1, limit: number = 20) {
  // Use the new endpoint for fetching classified comments if videoId is provided
  if (videoId) {
    try {
      const response = await fetchClassifiedComments(videoId);
      return response.comments || [];
    } catch (error) {
      console.error("Error fetching classified comments:", error);
      // Fall back to the original endpoint if the new one fails
    }
  }
  
  // Original code as fallback
  let endpoint = '/comments?';
  if (videoId) endpoint += `video_id=${videoId}&`;
  if (riskLevel) endpoint += `risk_level=${riskLevel}&`;
  endpoint += `skip=${(page - 1) * limit}&limit=${limit}`;
  
  return authFetch(endpoint);
}

export async function deleteComment(commentId: string) {
  return authFetch(`/comments/${commentId}`, {
    method: 'DELETE'
  });
}

export async function whitelistComment(commentId: string) {
  return authFetch(`/comments/${commentId}/whitelist`, {
    method: 'POST'
  });
}

export async function batchDeleteComments(commentIds: string[]) {
  return authFetch('/comments/batch/delete', {
    method: 'POST',
    body: JSON.stringify(commentIds)
  });
}

export async function batchWhitelistComments(commentIds: string[]) {
  return authFetch('/comments/batch/whitelist', {
    method: 'POST',
    body: JSON.stringify(commentIds)
  });
}

// ML Settings
export async function fetchMLSettings() {
  return authFetch('/settings/ml');
}

export async function updateMLSettings(settings: any) {
  return authFetch('/settings/ml', {
    method: 'PUT',
    body: JSON.stringify(settings)
  });
}

// More detailed metrics
export async function fetchOverallMetrics() {
  return authFetch('/metrics/overall');
}

export async function fetchVideoMetrics(videoId: string) {
  return authFetch(`/metrics/videos/${videoId}`);
}

export async function fetchTimeSeriesMetrics(period: string = 'day', limit: number = 30) {
  return authFetch(`/metrics/timeseries?period=${period}&limit=${limit}`);
}

export async function fetchMostTargetedVideos(limit: number = 5) {
  return authFetch(`/metrics/videos/most-targeted?limit=${limit}`);
}

// Other API functions can be added as needed 