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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
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
  User,
  Building,
  Phone,
  Shield,
  Award,
  Clock,
  CheckCircle
} from "lucide-react";

export default function Register() {
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    phone: "",
    company: "",
    companySize: "",
    password: "",
    confirmPassword: ""
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [agreeToTerms, setAgreeToTerms] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const { toast } = useToast();

  // Enhanced SEO with structured data
  useEffect(() => {
    const structuredData = {
      "@context": "https://schema.org",
      "@type": "WebPage",
      "name": "Create Account - FieldSync Pro",
      "description": "Start your free trial with FieldSync Pro. Comprehensive medical representative field management solution for pharmaceutical companies.",
      "url": window.location.href,
      "mainEntity": {
        "@type": "SoftwareApplication",
        "name": "FieldSync Pro",
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "Web Browser",
        "offers": {
          "@type": "Offer",
          "price": "0",
          "priceCurrency": "INR",
          "priceSpecification": {
            "@type": "UnitPriceSpecification",
            "price": "0",
            "priceCurrency": "INR",
            "name": "14-day free trial"
          }
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

  const companySize = [
    { value: "1-10", label: "1-10 employees" },
    { value: "11-50", label: "11-50 employees" },
    { value: "51-200", label: "51-200 employees" },
    { value: "201-500", label: "201-500 employees" },
    { value: "500+", label: "500+ employees" }
  ];

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const validateForm = () => {
    const { firstName, lastName, email, phone, company, password, confirmPassword } = formData;
    
    if (!firstName || !lastName || !email || !phone || !company || !password || !confirmPassword) {
      return "Please fill in all required fields";
    }
    
    if (!email.includes("@")) {
      return "Please enter a valid email address";
    }
    
    if (phone.length < 10) {
      return "Please enter a valid 10-digit phone number";
    }
    
    if (password.length < 8) {
      return "Password must be at least 8 characters long";
    }
    
    if (password !== confirmPassword) {
      return "Passwords do not match";
    }
    
    if (!agreeToTerms) {
      return "Please agree to the Terms of Service and Privacy Policy";
    }
    
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }
    
    setIsLoading(true);

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      toast({
        title: "Account Created Successfully!",
        description: "Welcome to FieldSync Pro. Please check your email for verification.",
      });
      
      // In real app, redirect to dashboard or email verification page
      // navigate('/dashboard');
      
    } catch (error) {
      setError("Registration failed. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleRegister = () => {
    toast({
      title: "Google Registration",
      description: "Google authentication will be implemented with your backend",
    });
  };

  return (
    <>
      <Helmet>
        <title>Create Account - FieldSync Pro | Start Free 14-Day Trial</title>
        <meta name="description" content="Start your free 14-day trial with FieldSync Pro. Comprehensive medical representative field management, route optimization, and sales analytics for pharmaceutical companies." />
        <meta name="keywords" content="FieldSync trial, pharmaceutical CRM, medical representative software, field force management, healthcare sales tracking, pharma route optimization, free trial registration" />
        
        {/* Open Graph tags */}
        <meta property="og:title" content="Create Account - FieldSync Pro | Free Trial" />
        <meta property="og:description" content="Join 5000+ pharmaceutical professionals using FieldSync Pro. Start your free 14-day trial and transform your field operations today." />
        <meta property="og:type" content="website" />
        <meta property="og:url" content={window.location.href} />
        <meta property="og:image" content="/og-register.jpg" />
        <meta property="og:site_name" content="FieldSync Pro" />
        
        {/* Twitter Card tags */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="Create Account - FieldSync Pro" />
        <meta name="twitter:description" content="Start your free trial with the leading medical representative tracking solution. No credit card required." />
        <meta name="twitter:image" content="/twitter-register.jpg" />
        
        {/* Additional SEO tags */}
        <meta name="robots" content="index, follow" />
        <meta name="author" content="FieldSync Pro" />
        <meta name="theme-color" content="#00C851" />
        <link rel="canonical" href={window.location.href} />
        
        {/* Mobile optimization */}
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
        <meta name="format-detection" content="telephone=no" />
      </Helmet>

      <div className="min-h-screen bg-gradient-to-br from-background via-surface to-background flex flex-col">
        {/* Enhanced Main Content */}
        <main className="flex-1 flex items-center justify-center p-6 section-spacing">
          <div className="w-full max-w-2xl space-y-8">
            {/* Value Proposition */}
            <div className="text-center space-y-6">
              <div className="flex items-center justify-center gap-8">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Award className="h-4 w-4 text-success" />
                  <span>14-Day Free Trial</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Clock className="h-4 w-4 text-warning" />
                  <span>2-Min Setup</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="h-4 w-4 text-primary" />
                  <span>No Credit Card</span>
                </div>
              </div>
            </div>

            <Card className="glass-card hover-lift">
              <CardHeader className="text-center space-y-4">
                <div className="flex h-16 w-16 items-center justify-center rounded-2xl gradient-success shadow-xl glow-success mx-auto animate-pulse-glow">
                  <User className="h-8 w-8 text-success-foreground" />
                </div>
                <div className="space-y-2">
                  <CardTitle className="text-3xl font-bold bg-gradient-to-r from-foreground to-muted-foreground bg-clip-text text-transparent">
                    Start Your Free Trial
                  </CardTitle>
                  <CardDescription className="text-base">
                    Join 5000+ pharmaceutical professionals who trust FieldSync Pro for their field operations
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

              <form onSubmit={handleSubmit} className="space-y-4">
                {/* Name Fields */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="firstName">First Name *</Label>
                    <Input
                      id="firstName"
                      type="text"
                      placeholder="Rajesh"
                      value={formData.firstName}
                      onChange={(e) => handleInputChange("firstName", e.target.value)}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="lastName">Last Name *</Label>
                    <Input
                      id="lastName"
                      type="text"
                      placeholder="Kumar"
                      value={formData.lastName}
                      onChange={(e) => handleInputChange("lastName", e.target.value)}
                      required
                    />
                  </div>
                </div>

                {/* Email */}
                <div className="space-y-2">
                  <Label htmlFor="email">Email Address *</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="email"
                      type="email"
                      placeholder="rajesh@yourcompany.com"
                      value={formData.email}
                      onChange={(e) => handleInputChange("email", e.target.value)}
                      className="pl-9"
                      required
                    />
                  </div>
                </div>

                {/* Phone */}
                <div className="space-y-2">
                  <Label htmlFor="phone">Phone Number *</Label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="phone"
                      type="tel"
                      placeholder="9876543210"
                      value={formData.phone}
                      onChange={(e) => handleInputChange("phone", e.target.value.replace(/\D/g, ""))}
                      className="pl-9"
                      maxLength={10}
                      required
                    />
                  </div>
                </div>

                {/* Company */}
                <div className="space-y-2">
                  <Label htmlFor="company">Company Name *</Label>
                  <div className="relative">
                    <Building className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="company"
                      type="text"
                      placeholder="ABC Pharmaceuticals Pvt Ltd"
                      value={formData.company}
                      onChange={(e) => handleInputChange("company", e.target.value)}
                      className="pl-9"
                      required
                    />
                  </div>
                </div>

                {/* Company Size */}
                <div className="space-y-2">
                  <Label htmlFor="companySize">Company Size</Label>
                  <Select value={formData.companySize} onValueChange={(value) => handleInputChange("companySize", value)}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select company size" />
                    </SelectTrigger>
                    <SelectContent>
                      {companySize.map((size) => (
                        <SelectItem key={size.value} value={size.value}>
                          {size.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Password */}
                <div className="space-y-2">
                  <Label htmlFor="password">Password *</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="password"
                      type={showPassword ? "text" : "password"}
                      placeholder="Create a strong password"
                      value={formData.password}
                      onChange={(e) => handleInputChange("password", e.target.value)}
                      className="pl-9 pr-9"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    >
                      {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Must be at least 8 characters long
                  </p>
                </div>

                {/* Confirm Password */}
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">Confirm Password *</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      id="confirmPassword"
                      type={showConfirmPassword ? "text" : "password"}
                      placeholder="Confirm your password"
                      value={formData.confirmPassword}
                      onChange={(e) => handleInputChange("confirmPassword", e.target.value)}
                      className="pl-9 pr-9"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    >
                      {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                    </button>
                  </div>
                </div>

                {/* Terms Checkbox */}
                <div className="flex items-start space-x-2">
                  <Checkbox 
                    id="terms" 
                    checked={agreeToTerms}
                    onCheckedChange={(checked) => setAgreeToTerms(checked === true)}
                    className="mt-1"
                  />
                  <div className="text-sm">
                    <Label 
                      htmlFor="terms" 
                      className="font-normal cursor-pointer leading-relaxed"
                    >
                      I agree to the{" "}
                      <Link to="/terms" className="text-primary hover:underline">
                        Terms of Service
                      </Link>
                      {" "}and{" "}
                      <Link to="/privacy" className="text-primary hover:underline">
                        Privacy Policy
                      </Link>
                    </Label>
                  </div>
                </div>

                <Button 
                  type="submit" 
                  className="w-full h-12 gradient-success text-success-foreground font-semibold shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300 glow-success" 
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <div className="flex items-center gap-2">
                      <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                      <span>Creating Account...</span>
                    </div>
                  ) : (
                    "Start Free 14-Day Trial"
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
                onClick={handleGoogleRegister}
                type="button"
              >
                <Chrome className="h-4 w-4 mr-2" />
                Continue with Google
              </Button>

              <div className="text-center text-sm text-muted-foreground">
                <p>
                  By creating an account, you agree to receive product updates and promotional emails.
                  You can unsubscribe at any time.
                </p>
              </div>
            </CardContent>
          </Card>

            {/* Enhanced Help Section */}
            <div className="text-center space-y-4">
              <p className="text-sm text-muted-foreground">
                Need assistance with setup? Our team is here to help
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link 
                  to="/demo" 
                  className="text-primary hover:text-primary-hover font-medium hover:underline transition-colors"
                >
                  Schedule Onboarding Call
                </Link>
                <Link 
                  to="/contact" 
                  className="text-primary hover:text-primary-hover font-medium hover:underline transition-colors"
                >
                  Contact Sales Team  
                </Link>
                <a 
                  href="tel:+919876543210" 
                  className="text-primary hover:text-primary-hover font-medium hover:underline transition-colors"
                >
                  Call +91-9876543210
                </a>
              </div>
              
              {/* Trust Indicators */}
              <div className="flex items-center justify-center gap-6 pt-6">
                <div className="flex items-center gap-2">
                  <Shield className="h-4 w-4 text-success" />
                  <span className="text-xs text-muted-foreground">Enterprise Security</span>
                </div>
                <div className="flex items-center gap-2">
                  <Award className="h-4 w-4 text-warning" />
                  <span className="text-xs text-muted-foreground">ISO 27001 Certified</span>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </>
  );
}