import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { 
  MapPin, 
  Users, 
  BarChart3, 
  Settings, 
  MessageSquare,
  Menu,
  X,
  Sun,
  Moon,
  Laptop,
  Wifi,
  WifiOff
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useTheme } from "@/providers/theme-provider";
import { Logo } from "./logo";

const navigationItems = [
  { title: "Dashboard", href: "/dashboard", icon: MapPin },
  { title: "Representatives", href: "/mrs", icon: Users },
  { title: "Analytics", href: "/analytics", icon: BarChart3 },
  { title: "Contact", href: "/contact", icon: MessageSquare },
  { title: "Settings", href: "/settings", icon: Settings },
];

interface MobileMenuProps {
  wsConnected?: boolean;
}

export function MobileMenu({ wsConnected = true }: MobileMenuProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { theme, setTheme } = useTheme();
  const location = useLocation();

  const isActiveRoute = (href: string) => {
    if (href === "/dashboard" && (location.pathname === "/" || location.pathname === "/dashboard")) {
      return true;
    }
    return location.pathname.startsWith(href) && href !== "/dashboard";
  };

  return (
    <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenuOpen}>
      <SheetTrigger asChild>
        <Button 
          variant="ghost" 
          size="sm" 
          className="lg:hidden h-9 w-9 p-0 relative hover:bg-accent"
        >
          <Menu className={cn("h-5 w-5 transition-all duration-300", mobileMenuOpen && "rotate-90")} />
          <span className="sr-only">Open menu</span>
        </Button>
      </SheetTrigger>
            <SheetContent 
              side="right" 
              className="w-[320px] bg-background p-0 border-l"
            >
        <div className="flex flex-col h-full">
          {/* Mobile Header */}
          <div className="flex items-center justify-between p-4 border-b border-border/50">
            <Logo size="sm" linkTo="/dashboard" />
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setMobileMenuOpen(false)}
              className="h-8 w-8 p-0 hover:bg-accent"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          
          {/* Mobile Navigation */}
          <nav className="flex-1 p-4">
            <div className="space-y-2">
              {navigationItems.map((item) => (
                <Link
                  key={item.href}
                  to={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={cn(
                    "flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition-all hover:bg-accent hover:text-accent-foreground border border-transparent hover:border-accent-foreground/10",
                    isActiveRoute(item.href) && "bg-gradient-to-r from-primary/15 to-primary-variant/15 text-primary border-primary/25 shadow-sm"
                  )}
                >
                  <item.icon className="h-5 w-5" />
                  {item.title}
                </Link>
              ))}
            </div>
          </nav>

          {/* Mobile Footer */}
          <div className="p-4 border-t border-border/50 space-y-4">
            {/* Mobile Connection Status */}
            <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-muted/30">
              {wsConnected ? (
                <div className="flex items-center gap-2 text-success">
                  <Wifi className="h-4 w-4" />
                  <span className="text-sm font-medium">Connected</span>
                </div>
              ) : (
                <div className="flex items-center gap-2 text-destructive">
                  <WifiOff className="h-4 w-4" />
                  <span className="text-sm font-medium">Disconnected</span>
                </div>
              )}
            </div>

            {/* Mobile Theme Toggle */}
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-foreground">Theme</span>
              <div className="flex items-center gap-1 p-1 rounded-lg bg-muted/50">
                <Button
                  variant={theme === "light" ? "default" : "ghost"}
                  size="sm"
                  onClick={() => setTheme("light")}
                  className="h-8 w-8 p-0"
                >
                  <Sun className="h-3 w-3" />
                </Button>
                <Button
                  variant={theme === "dark" ? "default" : "ghost"}
                  size="sm"
                  onClick={() => setTheme("dark")}
                  className="h-8 w-8 p-0"
                >
                  <Moon className="h-3 w-3" />
                </Button>
                <Button
                  variant={theme === "system" ? "default" : "ghost"}
                  size="sm"
                  onClick={() => setTheme("system")}
                  className="h-8 w-8 p-0"
                >
                  <Laptop className="h-3 w-3" />
                </Button>
              </div>
            </div>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}