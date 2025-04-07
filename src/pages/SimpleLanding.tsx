import React, { useState } from "react";
import { Link } from "react-router-dom";

const SimpleLanding = () => {
  const [apiStatus, setApiStatus] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const testBackendConnection = async () => {
    setIsLoading(true);
    try {
      const response = await fetch("http://localhost:8080/health");
      if (response.ok) {
        const data = await response.json();
        setApiStatus(`✅ Backend is running: ${JSON.stringify(data)}`);
      } else {
        setApiStatus(`❌ Backend error: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      setApiStatus(`❌ Cannot connect to backend: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 p-4">
      <div className="bg-white p-8 rounded-lg shadow-md max-w-lg w-full">
        <h1 className="text-3xl font-bold text-center mb-6">
          SpamShield Application
        </h1>
        
        <p className="mb-6 text-gray-600">
          This is a simple landing page to test that the application is rendering correctly.
        </p>
        
        <div className="flex flex-col space-y-4">
          <Link 
            to="/login" 
            className="bg-blue-600 text-white font-medium py-2 px-4 rounded hover:bg-blue-700 text-center"
          >
            Login
          </Link>
          
          <Link 
            to="/signup" 
            className="bg-gray-200 text-gray-800 font-medium py-2 px-4 rounded hover:bg-gray-300 text-center"
          >
            Sign Up
          </Link>
          
          <Link 
            to="/youtube-analyzer" 
            className="bg-red-600 text-white font-medium py-2 px-4 rounded hover:bg-red-700 text-center"
          >
            YouTube Comment Analyzer
          </Link>
          
          <Link 
            to="/debug" 
            className="bg-green-600 text-white font-medium py-2 px-4 rounded hover:bg-green-700 text-center"
          >
            Debug Page
          </Link>
          
          <button
            onClick={testBackendConnection}
            disabled={isLoading}
            className="bg-purple-600 text-white font-medium py-2 px-4 rounded hover:bg-purple-700 text-center disabled:bg-purple-300"
          >
            {isLoading ? "Testing Connection..." : "Test Backend Connection"}
          </button>
          
          {apiStatus && (
            <div className={`mt-2 p-3 rounded text-sm ${apiStatus.includes("✅") ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
              {apiStatus}
            </div>
          )}
        </div>
        
        <div className="mt-8 text-sm text-gray-500">
          <p>
            Environment: {import.meta.env.MODE}
          </p>
          <p>
            API URL: {import.meta.env.VITE_API_URL || 'Not set'}
          </p>
          <p>
            Supabase Configured: {import.meta.env.VITE_SUPABASE_URL ? 'Yes' : 'No'}
          </p>
        </div>
      </div>
    </div>
  );
};

export default SimpleLanding; 