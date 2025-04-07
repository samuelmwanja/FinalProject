import { useEffect, useState } from "react";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { AuthProvider } from "@/lib/auth";
import { routes } from "@/lib/routes";
import { Toaster } from "@/components/ui/toaster";

// Create router once, outside of component
console.log("Creating router with routes:", routes.map(r => r.path));
const router = createBrowserRouter(routes);

function App() {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [appError, setAppError] = useState<Error | null>(null);

  useEffect(() => {
    console.log("App component mounted");
    try {
      // Check if environment variables are loaded
      console.log("Environment variables check:", {
        apiUrl: import.meta.env.VITE_API_URL || 'not set',
        supabaseUrl: import.meta.env.VITE_SUPABASE_URL ? 'set' : 'not set',
        supabaseKey: import.meta.env.VITE_SUPABASE_ANON_KEY ? 'set' : 'not set'
      });
      
      // Check if user prefers dark mode or has set it previously
      const isDark = localStorage.getItem("darkMode") === "true" || 
        window.matchMedia("(prefers-color-scheme: dark)").matches;
      
      setIsDarkMode(isDark);
      document.documentElement.classList.toggle("dark", isDark);
    } catch (error) {
      console.error("Error in App useEffect:", error);
      setAppError(error instanceof Error ? error : new Error(String(error)));
    }
  }, []);

  const toggleDarkMode = () => {
    const newMode = !isDarkMode;
    setIsDarkMode(newMode);
    localStorage.setItem("darkMode", String(newMode));
    document.documentElement.classList.toggle("dark", newMode);
  };

  // If there's an app-level error, show it
  if (appError) {
    return (
      <div className="p-8 max-w-lg mx-auto my-8 bg-white rounded-lg shadow text-red-600">
        <h1 className="text-2xl font-bold mb-4">Application Error</h1>
        <p className="mb-4">There was an error initializing the application:</p>
        <pre className="bg-gray-100 p-4 rounded">{appError.message}</pre>
      </div>
    );
  }

  return (
    <AuthProvider>
      <div className={isDarkMode ? "dark" : ""}>
        <RouterProvider router={router} />
        <Toaster />
      </div>
    </AuthProvider>
  );
}

export default App;
