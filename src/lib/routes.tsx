import { ReactNode } from "react";
import { Navigate, RouteObject } from "react-router-dom";
import LandingPage from "@/pages/LandingPage";
import LoginPage from "@/pages/LoginPage";
import SignupPage from "@/pages/SignupPage";
import Dashboard from "@/pages/Dashboard";
import SimpleLanding from "@/pages/SimpleLanding";
import YouTubeAnalyzerPage from "@/pages/YouTubeAnalyzerPage";
import { useAuth } from "./auth";

// Simple debug component to verify routing works
const DebugPage = () => {
  return (
    <div className="p-8 max-w-lg mx-auto my-8 bg-white rounded-lg shadow">
      <h1 className="text-2xl font-bold mb-4">Debug Page</h1>
      <p className="mb-4">If you can see this page, routing is working correctly.</p>
      <pre className="bg-gray-100 p-4 rounded">
        {JSON.stringify({
          environment: import.meta.env.MODE,
          apiUrl: import.meta.env.VITE_API_URL,
          supabaseConfigured: !!import.meta.env.VITE_SUPABASE_URL
        }, null, 2)}
      </pre>
    </div>
  );
};

interface ProtectedRouteProps {
  children: ReactNode;
}

export const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex h-screen w-full items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

interface PublicRouteProps {
  children: ReactNode;
}

export const PublicRoute = ({ children }: PublicRouteProps) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex h-screen w-full items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};

export const routes: RouteObject[] = [
  {
    path: "/",
    element: <SimpleLanding />,
  },
  {
    path: "/landing",
    element: <LandingPage />,
  },
  {
    path: "/login",
    element: (
      <PublicRoute>
        <LoginPage />
      </PublicRoute>
    ),
  },
  {
    path: "/signup",
    element: (
      <PublicRoute>
        <SignupPage />
      </PublicRoute>
    ),
  },
  {
    path: "/dashboard",
    element: (
      <ProtectedRoute>
        <Dashboard />
      </ProtectedRoute>
    ),
  },
  {
    path: "/youtube-analyzer",
    element: <YouTubeAnalyzerPage />,
  },
  {
    path: "/debug",
    element: <DebugPage />,
  },
  {
    path: "*",
    element: <Navigate to="/" replace />,
  },
];

export default routes; 