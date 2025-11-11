import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Logo } from "@/components/layout/logo";
import { 
  MapPin, 
  Mail, 
  Phone, 
  Github, 
  Twitter, 
  Linkedin,
  Shield,
  FileText,
  HelpCircle,
  ExternalLink
} from "lucide-react";

export function Footer() {
  const currentYear = new Date().getFullYear();

  const quickLinks = [
    { name: "Dashboard", href: "/dashboard" },
    { name: "MRs", href: "/mrs" },
    { name: "Analytics", href: "/analytics" },
    { name: "Settings", href: "/settings" },
  ];

  const legalLinks = [
    { name: "Privacy Policy", href: "/privacy" },
    { name: "Terms of Service", href: "/terms" },
    { name: "Cookie Policy", href: "/cookies" },
    { name: "Data Protection", href: "/data-protection" },
  ];

  const supportLinks = [
    { name: "Help Center", href: "/help", icon: HelpCircle },
    { name: "Contact Support", href: "/support", icon: Mail },
    { name: "API Documentation", href: "/api-docs", icon: FileText },
    { name: "Security", href: "/security", icon: Shield },
  ];

  const socialLinks = [
    { name: "GitHub", href: "https://github.com/visheshsanghvi112/MR-Tracking-System", icon: Github },
    { name: "Twitter", href: "https://twitter.com/johnleesolutions", icon: Twitter },
    { name: "LinkedIn", href: "https://linkedin.com/company/johnlee-solutions", icon: Linkedin },
  ];

  return (
    <footer className="glass-surface border-t border-glass-border backdrop-blur-lg">
      <div className="container mx-auto px-4 py-12">
        {/* Main Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Brand Section */}
          <div className="space-y-4">
            <Link to="/dashboard">
              <Logo />
            </Link>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Premium pharmaceutical field force management platform. 
              Real-time tracking, intelligent analytics, and performance optimization for medical representatives.
            </p>
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors">
                <Mail className="h-4 w-4" />
                <a href="mailto:visheshsanghvi112@gmail.com">visheshsanghvi112@gmail.com</a>
              </div>
              <div className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors">
                <Phone className="h-4 w-4" />
                <a href="tel:+917977282697">+91 79772 82697</a>
              </div>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <MapPin className="h-4 w-4" />
                <span>Mumbai, Maharashtra, India</span>
              </div>
            </div>
          </div>

          {/* Quick Links */}
          <div className="space-y-4">
            <h3 className="font-semibold text-foreground">Quick Links</h3>
            <nav className="space-y-2">
              {quickLinks.map((link) => (
                <Link
                  key={link.href}
                  to={link.href}
                  className="block text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  {link.name}
                </Link>
              ))}
            </nav>
          </div>

          {/* Support */}
          <div className="space-y-4">
            <h3 className="font-semibold text-foreground">Support</h3>
            <nav className="space-y-2">
              {supportLinks.map((link) => (
                <Link
                  key={link.href}
                  to={link.href}
                  className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors group"
                >
                  <link.icon className="h-4 w-4" />
                  <span>{link.name}</span>
                  <ExternalLink className="h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                </Link>
              ))}
            </nav>
          </div>

          {/* Legal & Social */}
          <div className="space-y-4">
            <h3 className="font-semibold text-foreground">Legal</h3>
            <nav className="space-y-2">
              {legalLinks.map((link) => (
                <Link
                  key={link.href}
                  to={link.href}
                  className="block text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  {link.name}
                </Link>
              ))}
            </nav>
            
            {/* Social Links */}
            <div className="pt-4">
              <h4 className="font-medium text-foreground mb-3">Follow Us</h4>
              <div className="flex items-center gap-2">
                {socialLinks.map((social) => (
                  <Button
                    key={social.name}
                    variant="ghost"
                    size="sm"
                    className="h-8 w-8 p-0"
                    asChild
                  >
                    <a
                      href={social.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-muted-foreground hover:text-foreground"
                    >
                      <social.icon className="h-4 w-4" />
                      <span className="sr-only">{social.name}</span>
                    </a>
                  </Button>
                ))}
              </div>
            </div>
          </div>
        </div>

        <Separator className="my-8" />

        {/* Footer Bottom */}
        <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
          <div className="flex flex-col sm:flex-row items-center gap-2 sm:gap-4 text-sm text-muted-foreground">
            <span>© {currentYear} FieldSync PRO. All rights reserved.</span>
            <Separator orientation="vertical" className="h-4 hidden sm:block" />
            <span className="text-xs font-medium">
              Made by <a href="https://visheshsanghvi.me" target="_blank" rel="noopener noreferrer" className="font-semibold bg-gradient-to-r from-primary to-primary-variant bg-clip-text text-transparent hover:underline">Vishesh Sanghvi</a> for Johnlee
            </span>
          </div>
          
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span>Version 1.0.0</span>
            <Separator orientation="vertical" className="h-4" />
            <div className="flex items-center gap-1">
              <div className="h-2 w-2 rounded-full bg-success animate-pulse" />
              <span>All systems operational</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}