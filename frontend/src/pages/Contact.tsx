import { useState } from "react";

import { EnhancedCard } from "@/components/ui/enhanced-card";
import { EnhancedButton } from "@/components/ui/enhanced-button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/components/ui/use-toast";
import { 
  Mail, 
  Phone, 
  MapPin, 
  Clock, 
  Send,
  MessageSquare,
  Users,
  Shield,
  Zap
} from "lucide-react";

const Contact = () => {
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    company: "",
    subject: "",
    message: "",
    inquiryType: "general"
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // Simulate form submission
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    toast({
      title: "Message Sent!",
      description: "Thank you for contacting us. We'll get back to you within 24 hours.",
    });
    
    setFormData({
      name: "",
      email: "",
      company: "",
      subject: "",
      message: "",
      inquiryType: "general"
    });
    setIsSubmitting(false);
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const contactInfo = [
    {
      icon: Mail,
      title: "Email Support",
      value: "support@fieldsync.pro",
      description: "24/7 email support"
    },
    {
      icon: Phone,
      title: "Phone Support",
      value: "+1 (555) 123-4567",
      description: "Mon-Fri, 9AM-6PM PST"
    },
    {
      icon: MapPin,
      title: "Head Office",
      value: "San Francisco, CA",
      description: "Visit our headquarters"
    },
    {
      icon: Clock,
      title: "Response Time",
      value: "< 4 hours",
      description: "Average response time"
    }
  ];

  const inquiryTypes = [
    { value: "general", label: "General Inquiry", icon: MessageSquare },
    { value: "sales", label: "Sales & Pricing", icon: Zap },
    { value: "support", label: "Technical Support", icon: Shield },
    { value: "partnership", label: "Partnership", icon: Users }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
      <main className="container mx-auto px-4 py-8 animate-fade-in">
        {/* Hero Section */}
        <div className="text-center mb-12 space-y-4">
          <Badge variant="secondary" className="mb-4 animate-bounce">
            <MessageSquare className="h-3 w-3 mr-1" />
            Get in Touch
          </Badge>
          <h1 className="text-4xl sm:text-5xl font-black bg-gradient-to-r from-primary via-primary-variant to-accent bg-clip-text text-transparent">
            Contact FieldSync Pro
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Have questions about our medical representative tracking platform? 
            We're here to help you optimize your field operations.
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Contact Form */}
          <div className="lg:col-span-2">
            <EnhancedCard variant="glass" className="p-6 sm:p-8">
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-foreground mb-2">Send us a Message</h2>
                <p className="text-muted-foreground">
                  Fill out the form below and we'll get back to you as soon as possible.
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Inquiry Type */}
                <div className="space-y-3">
                  <Label className="text-sm font-medium">Inquiry Type</Label>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                    {inquiryTypes.map((type) => (
                      <button
                        key={type.value}
                        type="button"
                        onClick={() => handleInputChange("inquiryType", type.value)}
                        className={`p-3 rounded-lg border text-sm font-medium transition-all duration-300 hover:scale-105 ${
                          formData.inquiryType === type.value
                            ? "bg-primary text-primary-foreground border-primary shadow-lg"
                            : "bg-background border-border hover:border-primary/50"
                        }`}
                      >
                        <type.icon className="h-4 w-4 mx-auto mb-1" />
                        {type.label}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Personal Information */}
                <div className="grid sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Full Name *</Label>
                    <Input
                      id="name"
                      type="text"
                      placeholder="John Doe"
                      value={formData.name}
                      onChange={(e) => handleInputChange("name", e.target.value)}
                      required
                      className="transition-all duration-300 focus:scale-105"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email Address *</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="john@company.com"
                      value={formData.email}
                      onChange={(e) => handleInputChange("email", e.target.value)}
                      required
                      className="transition-all duration-300 focus:scale-105"
                    />
                  </div>
                </div>

                <div className="grid sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="company">Company</Label>
                    <Input
                      id="company"
                      type="text"
                      placeholder="Your Company"
                      value={formData.company}
                      onChange={(e) => handleInputChange("company", e.target.value)}
                      className="transition-all duration-300 focus:scale-105"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="subject">Subject *</Label>
                    <Input
                      id="subject"
                      type="text"
                      placeholder="How can we help you?"
                      value={formData.subject}
                      onChange={(e) => handleInputChange("subject", e.target.value)}
                      required
                      className="transition-all duration-300 focus:scale-105"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="message">Message *</Label>
                  <Textarea
                    id="message"
                    placeholder="Tell us more about your needs..."
                    value={formData.message}
                    onChange={(e) => handleInputChange("message", e.target.value)}
                    required
                    rows={6}
                    className="transition-all duration-300 focus:scale-105 resize-none"
                  />
                </div>

                <EnhancedButton
                  type="submit"
                  variant="gradient"
                  size="lg"
                  loading={isSubmitting}
                  className="w-full sm:w-auto"
                >
                  <Send className="h-4 w-4 mr-2" />
                  {isSubmitting ? "Sending..." : "Send Message"}
                </EnhancedButton>
              </form>
            </EnhancedCard>
          </div>

          {/* Contact Information */}
          <div className="space-y-6">
            <EnhancedCard variant="glass" className="p-6">
              <h3 className="text-xl font-bold text-foreground mb-4">Contact Information</h3>
              <div className="space-y-4">
                {contactInfo.map((info, index) => (
                  <div key={index} className="flex items-start gap-3 group">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 group-hover:bg-primary/20 transition-colors duration-300">
                      <info.icon className="h-5 w-5 text-primary" />
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold text-foreground">{info.title}</h4>
                      <p className="text-sm font-medium text-primary">{info.value}</p>
                      <p className="text-xs text-muted-foreground">{info.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </EnhancedCard>

            <EnhancedCard variant="gradient" className="p-6 text-center">
              <div className="space-y-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-white/20 mx-auto">
                  <Zap className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-xl font-bold text-white">Need Immediate Help?</h3>
                <p className="text-white/90 text-sm">
                  Our support team is available 24/7 to help you with any urgent issues.
                </p>
                <Separator className="bg-white/20" />
                <div className="text-white/90 text-sm">
                  <p>Emergency Support:</p>
                  <p className="font-bold text-white">+1 (555) 911-HELP</p>
                </div>
              </div>
            </EnhancedCard>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Contact;