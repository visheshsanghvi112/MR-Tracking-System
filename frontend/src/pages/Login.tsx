import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Checkbox } from "@/components/ui/checkbox";
import { useToast } from "@/hooks/use-toast";
import { 
  MapPin, 
  Eye, 
  EyeOff, 
  Mail, 
  Lock, 
  ArrowLeft,
  AlertCircle,
  Chrome,
  Shield,
  Zap,
  Users
} from "lucide-react";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const { toast } = useToast();

  // Enhanced SEO with structured data
  useEffect(() => {
    const structuredData = {
      "@context": "https://schema.org",
      "@type": "WebPage",
        "name": "Login - FieldSync Pro",
        "description": "Secure login to your FieldSync Pro account. Access your dashboard, manage field operations, and track medical representative activities.",
      "url": window.location.href,
      "mainEntity": {
        "@type": "SoftwareApplication",
        "name": "FieldSync Pro",
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "Web Browser",
        "offers": {
          "@type": "Offer",
          "price": "0",
          "priceCurrency": "INR"
        }
      }
    };

    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.innerHTML = JSON.stringify(structuredData);
    document.head.appendChild(script);

    return () => {
      document.head.removeChild(script);
    };
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    // Basic validation
    if (!email || !password) {
      setError("Please fill in all fields");
      setIsLoading(false);
      return;
    }

    if (!email.includes("@")) {
      setError("Please enter a valid email address");
      setIsLoading(false);
      return;
    }

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // For demo purposes, accept any email/password combination
      toast({
        title: "Login Successful!",
        description: "Welcome back to FieldSync Pro",
      });
      
      // In real app, redirect to dashboard after successful login
      // navigate('/dashboard');
      
    } catch (error) {
      setError("Login failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleLogin = () => {
    toast({
      title: "Google Login",
      description: "Google authentication will be implemented with your backend",
    });
  };

  return (
    <>
      <Helmet>
        <title>Secure Login - FieldSync Pro | Medical Representative Field Management</title>
        <meta name="description" content="Secure login to your FieldSync Pro account. Access comprehensive medical representative tracking, route optimization, and sales analytics. Start managing your field operations today." />
        <meta name="keywords" content="FieldSync login, medical representative management, pharma field operations, sales tracking, healthcare CRM login, pharmaceutical tracking system" />
        
        {/* Open Graph tags */}
        <meta property="og:title" content="Secure Login - FieldSync Pro" />
        <meta property="og:description" content="Access your comprehensive medical representative tracking dashboard. Manage field operations, optimize routes, and track sales performance." />
        <meta property="og:type" content="website" />
        <meta property="og:url" content={window.location.href} />
        <meta property="og:image" content="/og-login.jpg" />
        <meta property="og:site_name" content="FieldSync Pro" />
        
        {/* Twitter Card tags */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="Secure Login - FieldSync Pro" />
        <meta name="twitter:description" content="Access your medical representative tracking dashboard. Comprehensive field management for pharmaceutical companies." />
        <meta name="twitter:image" content="/twitter-login.jpg" />
        
        {/* Additional SEO tags */}
        <meta name="robots" content="index, follow" />
        <meta name="author" content="FieldSync Pro" />
        <meta name="theme-color" content="#0066FF" />
        <link rel="canonical" href={window.location.href} />
        
        {/* Mobile optimization */}
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
        <meta name="format-detection" content="telephone=no" />
        
        {/* Security headers */}
        <meta http-equiv="X-Content-Type-Options" content="nosniff" />
        <meta http-equiv="X-Frame-Options" content="DENY" />
      </Helmet>

      <div className="min-h-screen bg-gradient-to-br from-background via-surface to-background flex flex-col">
        {/* Enhanced Main Content */}
        <main className="flex-1 flex items-center justify-center p-6 section-spacing">
          <div className="w-full max-w-md space-y-8">
            {/* Trust Indicators */}
            <div className="text-center space-y-4">
              <div className="flex items-center justify-center gap-6 text-sm text-muted-foreground">
                <div className="flex items-center gap-2">
                  <Shield className="h-4 w-4 text-success" />
                  <span>Secure Login</span>
                </div>
                <div className="flex items-center gap-2">
                  <Zap className="h-4 w-4 text-warning" />
                  <span>Fast Access</span>
                </div>
                <div className="flex items-center gap-2">
                  <Users className="h-4 w-4 text-primary" />
                  <span>5000+ Users</span>
                </div>
              </div>
            </div>

            <Card className="glass-card hover-lift">
              <CardHeader className="text-center space-y-4">
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl gradient-primary shadow-xl glow-primary mx-auto animate-pulse-glow">
                  <Lock className="h-8 w-8 text-primary-foreground" />
                </div>
                <div className="space-y-2">
                  <CardTitle className="text-3xl font-bold bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text text-transparent">
                    Welcome Back
                  </CardTitle>
                  <CardDescription className="text-base">
                    Sign in to your FieldSync Pro account and continue optimizing your field operations
                  </CardDescription>
                </div>
              </CardHeader>
            
            <CardContent className="space-y-6">
              {error && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="email" className="text-sm font-medium">Email Address</Label>
                  <div className="relative group">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
                    <Input
                      id="email"
                      type="email"
                      placeholder="rajesh@yourcompany.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="pl-9 h-12 bg-surface/50 border-0 ring-1 ring-border focus:ring-2 focus:ring-primary transition-all"
                      required
                      autoComplete="email"
                      aria-describedby="email-hint"
                    />
                  </div>
                  <p id="email-hint" className="text-xs text-muted-foreground">
                    Use your registered business email address
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password" className="text-sm font-medium">Password</Label>
                  <div className="relative group">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="Enter your secure password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="pl-9 pr-12 h-12 bg-surface/50 border-0 ring-1 ring-border focus:ring-2 focus:ring-primary transition-all"
                      required
                      autoComplete="current-password"
                      aria-describedby="password-hint"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground p-1 rounded-md hover:bg-surface transition-all"
                      aria-label={showPassword ? "Hide password" : "Show password"}
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                  <p id="password-hint" className="text-xs text-muted-foreground">
                    Your password is encrypted and secure
                  </p>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Checkbox 
                      id="remember" 
                      checked={rememberMe}
                      onCheckedChange={(checked) => setRememberMe(checked === true)}
                    />
                    <Label 
                      htmlFor="remember" 
                      className="text-sm font-normal cursor-pointer"
                    >
                      Remember me
                    </Label>
                  </div>
                  
                  <Link 
                    to="/forgot-password" 
                    className="text-sm text-primary hover:underline"
                  >
                    Forgot password?
                  </Link>
                </div>

                <Button 
                  type="submit" 
                  className="w-full h-12 gradient-primary text-primary-foreground font-semibold shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300 glow-primary" 
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <div className="flex items-center gap-2">
                      <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                      <span>Signing in...</span>
                    </div>
                  ) : (
                    "Sign In to Dashboard"
                  )}
                </Button>
              </form>

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <Separator />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-background px-2 text-muted-foreground">
                    Or continue with
                  </span>
                </div>
              </div>

              <Button 
                variant="outline" 
                className="w-full h-12 glass-surface border-glass-border hover:bg-glass hover:scale-105 transition-all duration-300 font-medium" 
                onClick={handleGoogleLogin}
                type="button"
              >
                <Chrome className="h-4 w-4 mr-2" />
                Continue with Google
              </Button>

              <div className="text-center text-sm text-muted-foreground">
                <p>
                  By signing in, you agree to our{" "}
                  <Link to="/terms" className="text-primary hover:underline">
                    Terms of Service
                  </Link>
                  {" "}and{" "}
                  <Link to="/privacy" className="text-primary hover:underline">
                    Privacy Policy
                  </Link>
                </p>
              </div>
            </CardContent>
          </Card>

            {/* Enhanced Help Section */}
            <div className="text-center space-y-4">
              <p className="text-sm text-muted-foreground">
                Need assistance with your account?
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link 
                  to="/demo" 
                  className="text-primary hover:text-primary-hover font-medium hover:underline transition-colors"
                >
                  Schedule a Demo
                </Link>
                <Link 
                  to="/contact" 
                  className="text-primary hover:text-primary-hover font-medium hover:underline transition-colors"
                >
                  Contact Support
                </Link>
                <Link 
                  to="/help" 
                  className="text-primary hover:text-primary-hover font-medium hover:underline transition-colors"
                >
                  Help Center
                </Link>
              </div>
              
              {/* Security Badge */}
              <div className="flex items-center justify-center gap-2 pt-4">
                <Shield className="h-4 w-4 text-success" />
                <span className="text-xs text-muted-foreground">
                  256-bit SSL encryption • SOC 2 compliant
                </span>
              </div>
            </div>
          </div>
        </main>
      </div>
    </>
  );
}