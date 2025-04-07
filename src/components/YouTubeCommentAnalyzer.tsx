import React, { useState } from 'react';
import { analyzeYouTubeVideo, YouTubeAnalysisResponse, YouTubeComment } from '@/lib/api';

interface AnalysisResult {
  video_id: string;
  title: string;
  total_comments: number;
  retrieved_comments: number;
  spam_comments: number;
  recent_spam: YouTubeComment[];
  recent_non_spam: YouTubeComment[];
  data_source: string;
  classifier_method: string;
  warning?: string;
  error?: string;
}

const YouTubeCommentAnalyzer: React.FC = () => {
  const [videoUrl, setVideoUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);

  console.log('YouTubeCommentAnalyzer component rendered');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!videoUrl) {
      setError('Please enter a YouTube URL');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    console.log('Submitting request to analyze YouTube URL:', videoUrl);
    
    try {
      // Use the improved API client to fetch all comments (no max limit)
      console.log('Calling analyzeYouTubeVideo with URL:', videoUrl);
      const response = await analyzeYouTubeVideo(videoUrl); // No max_comments means fetch all
      console.log('Received API response:', response);
      
      if (response.error) {
        console.error('Error in API response:', response.error);
        throw new Error(response.error);
      }
      
      if (!response.video_id) {
        console.error('API response missing video_id:', response);
        throw new Error('Invalid API response: missing video ID');
      }
      
      // Format the response to match our component's expected format
      console.log('Formatting response for UI');
      const formattedResult: AnalysisResult = {
        video_id: response.video_id,
        title: response.title || 'YouTube Video',
        total_comments: response.total_comments || 0,
        retrieved_comments: response.analyzed_comments || 0,
        spam_comments: response.spam_comments || 0,
        recent_spam: response.recent_spam?.map(comment => ({
          id: comment.text.substring(0, 8), // Generate an ID since our mock data doesn't have one
          text: comment.text,
          author: comment.author || "YouTube User",
          published_at: comment.published_at || new Date().toISOString(),
          spam_probability: comment.spam_probability || 0,
          risk_level: comment.risk_level || "low",
          method: comment.method || "ml-model",
          is_spam: comment.is_spam || false
        })) || [],
        recent_non_spam: response.recent_non_spam?.map(comment => ({
          id: comment.text.substring(0, 8), // Generate an ID 
          text: comment.text,
          author: comment.author || "YouTube User",
          published_at: comment.published_at || new Date().toISOString(),
          spam_probability: comment.spam_probability || 0,
          risk_level: comment.risk_level || "low",
          method: comment.method || "ml-model",
          is_spam: comment.is_spam || false
        })) || [],
        data_source: response.data_source || 'mock_data',
        classifier_method: response.classifier_method || 'ml-model',
        warning: response.warning || (response.data_source === 'mock_data' ? 'Using mock data for this demo' : undefined)
      };
      
      console.log('Comments received:', response.analyzed_comments || 0);
      console.log('Spam comments:', formattedResult.recent_spam.length);
      console.log('Non-spam comments:', formattedResult.recent_non_spam.length);
      
      setResult(formattedResult);
      console.log('Analysis results set to state:', formattedResult);
    } catch (err) {
      console.error('Error during analysis:', err);
      setError(`Error analyzing comments: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  };
  
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    } catch (e) {
      return dateString || 'Unknown date';
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-4">
      <div className="bg-white p-6 rounded-lg shadow-md mb-8">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="videoUrl" className="block text-sm font-medium text-gray-700 mb-1">
              YouTube Video URL:
            </label>
            <div className="mt-1 flex rounded-md shadow-sm">
              <input
                type="text"
                id="videoUrl"
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
                placeholder="Enter YouTube URL (e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ)"
                className="flex-1 block w-full rounded-md border-gray-300 border p-2 focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              />
            </div>
          </div>
          
          <div>
            <button
              type="submit"
              disabled={loading}
              className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-blue-300 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Analyzing...
                </>
              ) : 'Analyze Comments'}
            </button>
          </div>
        </form>
      </div>
      
      {loading && (
        <div className="text-center my-8 p-6 bg-white rounded-lg shadow-md">
          <p className="text-lg font-medium text-gray-700 mb-4">Analyzing YouTube comments</p>
          <p className="text-sm text-gray-500 mb-6">This may take a moment as we retrieve and classify all comments.</p>
          <div className="flex justify-center">
            <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
          </div>
        </div>
      )}
      
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded shadow-md mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}
      
      {result && (
        <div>
          <div className="bg-white p-6 rounded-lg shadow-md mb-8">
            <h2 className="text-xl font-semibold mb-4 flex items-center">
              <svg className="w-5 h-5 mr-2 text-red-600" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm0-2a6 6 0 100-12 6 6 0 000 12z" clipRule="evenodd" />
              </svg>
              {result.title}
            </h2>
            
            {result.warning && (
              <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 my-4 rounded">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-yellow-700">{result.warning}</p>
                  </div>
                </div>
              </div>
            )}
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
              <div className="bg-gray-50 p-4 rounded shadow-sm border border-gray-200">
                <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider">Total Comments</h3>
                <p className="mt-1 text-2xl font-semibold text-blue-600">{result.total_comments.toLocaleString()}</p>
              </div>
              
              <div className="bg-gray-50 p-4 rounded shadow-sm border border-gray-200">
                <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider">Retrieved</h3>
                <p className="mt-1 text-2xl font-semibold text-blue-600">{result.retrieved_comments.toLocaleString()}</p>
              </div>
              
              <div className="bg-gray-50 p-4 rounded shadow-sm border border-gray-200">
                <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider">Spam Comments</h3>
                <p className="mt-1 text-2xl font-semibold text-red-600">{result.spam_comments.toLocaleString()}</p>
              </div>
              
              <div className="bg-gray-50 p-4 rounded shadow-sm border border-gray-200">
                <h3 className="text-sm font-medium text-gray-500 uppercase tracking-wider">Spam Percentage</h3>
                <p className="mt-1 text-2xl font-semibold text-red-600">
                  {((result.spam_comments / result.retrieved_comments) * 100).toFixed(1)}%
                </p>
              </div>
            </div>
            
            <div className="mt-4 text-sm text-gray-500">
              <p className="flex items-center">
                <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2h-1v-3a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                Classification method: {result.classifier_method || 'ML model'}
              </p>
            </div>
          </div>
          
          <div className="mb-8">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-lg font-semibold border-b pb-2 mb-4 flex items-center">
                <svg className="w-5 h-5 mr-2 text-red-500" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                Recent Spam Comments
              </h2>
              {result.recent_spam && result.recent_spam.length > 0 ? (
                <div className="space-y-4">
                  {result.recent_spam.map((comment) => (
                    <div 
                      key={comment.id} 
                      className="p-4 bg-gray-50 border border-gray-200 rounded border-l-4 border-l-red-500"
                    >
                      <div className="font-medium text-gray-800 mb-1">@{comment.author}</div>
                      <div className="mb-2 text-gray-700" dangerouslySetInnerHTML={{ __html: comment.text }}></div>
                      <div className="text-xs text-gray-500 flex justify-between">
                        <span>Published: {formatDate(comment.published_at)}</span>
                        <span className="flex items-center">
                          <svg className="w-3 h-3 mr-1 text-red-500" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                          </svg>
                          Spam Probability: {(comment.spam_probability * 100).toFixed(1)}% 
                          ({comment.risk_level} risk)
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 italic">No spam comments found</p>
              )}
            </div>
          </div>
          
          <div>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-lg font-semibold border-b pb-2 mb-4 flex items-center">
                <svg className="w-5 h-5 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                  <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                Recent Non-Spam Comments
              </h2>
              {result.recent_non_spam && result.recent_non_spam.length > 0 ? (
                <div className="space-y-4">
                  {result.recent_non_spam.map((comment) => (
                    <div 
                      key={comment.id} 
                      className="p-4 bg-gray-50 border border-gray-200 rounded border-l-4 border-l-green-500"
                    >
                      <div className="font-medium text-gray-800 mb-1">@{comment.author}</div>
                      <div className="mb-2 text-gray-700" dangerouslySetInnerHTML={{ __html: comment.text }}></div>
                      <div className="text-xs text-gray-500 flex justify-between">
                        <span>Published: {formatDate(comment.published_at)}</span>
                        <span className="flex items-center">
                          <svg className="w-3 h-3 mr-1 text-green-500" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                            <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                          </svg>
                          Spam Probability: {(comment.spam_probability * 100).toFixed(1)}% 
                          ({comment.risk_level} risk)
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 italic">No non-spam comments found</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default YouTubeCommentAnalyzer; 