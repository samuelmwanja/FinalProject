import React, { useState, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/lib/auth";
import { supabase } from "@/lib/supabase";

const LoginPage = () => {
  const { login, error, loading } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const location = useLocation();
  const message = location.state?.message;
  
  // Add debug logging on component mount
  useEffect(() => {
    console.log("LoginPage mounted");
    console.log("Auth state:", { loading, error });
    
    // Check Supabase connection
    const checkSupabase = async () => {
      try {
        console.log("Checking Supabase connection...");
        // Test if we can get the Supabase URL and key
        const { data, error } = await supabase.from('users').select('count');
        console.log("Supabase test query result:", { data, error });
      } catch (e) {
        console.error("Supabase connection error:", e);
      }
    };
    
    checkSupabase();
  }, [loading, error]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;
    
    console.log("Attempting login with:", { email });
    await login(email, password);
    console.log("Login attempt completed, auth state:", { loading, error });
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-background px-4">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold tracking-tight">
            Sign in to your account
          </h2>
          <p className="mt-2 text-sm text-muted-foreground">
            Enter your credentials to access your account
          </p>
        </div>

        {message && (
          <div className="p-4 bg-green-100 text-green-800 rounded-md">
            {message}
          </div>
        )}
        
        {/* Error messages are now hidden since we use toast notifications */}
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <Label htmlFor="email" className="block text-sm font-medium">
                Email address
              </Label>
              <div className="mt-1">
                <Input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="block w-full"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between">
                <Label htmlFor="password" className="block text-sm font-medium">
                  Password
                </Label>
                <div className="text-sm">
                  <Link
                    to="/forgot-password"
                    className="font-medium text-primary hover:text-primary/80"
                  >
                    Forgot password?
                  </Link>
                </div>
              </div>
              <div className="mt-1">
                <Input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full"
                />
              </div>
            </div>
          </div>

          <div>
            <Button 
              type="submit" 
              className="w-full py-6" 
              disabled={loading}
              size="lg"
            >
              {loading ? "Signing in..." : "Sign in"}
            </Button>
          </div>
          
          <div className="text-center mt-6">
            <p className="text-sm text-muted-foreground">
              Not a member?{" "}
              <Link
                to="/signup"
                className="font-medium text-primary hover:text-primary/80"
              >
                Sign up now
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default LoginPage; 