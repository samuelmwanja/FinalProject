import React from 'react';
import { Link } from 'react-router-dom';
import YouTubeCommentAnalyzer from '@/components/YouTubeCommentAnalyzer';
import { Shield, Home } from 'lucide-react';

export default function YouTubeAnalyzerPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="sticky top-0 z-10 border-b bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex h-16 items-center justify-between py-4">
          <div className="flex items-center gap-2">
            <Shield className="h-6 w-6 text-red-600" />
            <span className="text-xl font-bold">SpamShield</span>
          </div>
          
          <nav className="flex space-x-4">
            <Link 
              to="/" 
              className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100"
            >
              <Home className="h-4 w-4 mr-1" />
              Home
            </Link>
          </nav>
        </div>
      </header>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight">YouTube Analyzer</h1>
          <p className="text-muted-foreground text-gray-500">
            Analyze comments on any YouTube video for spam and suspicious content.
          </p>
        </div>
      </div>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <YouTubeCommentAnalyzer />
      </main>
      
      <footer className="border-t mt-12 py-4 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between text-xs text-gray-500">
          <div>© 2023 SpamShield. All rights reserved.</div>
          <div>Privacy Policy · Terms of Service</div>
        </div>
      </footer>
    </div>
  );
} 