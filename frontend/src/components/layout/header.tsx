import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { 
  Bell,
  Sun,
  Moon,
  Laptop,
  Wifi,
  WifiOff
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useTheme } from "@/providers/theme-provider";
import { useIsMobile } from "@/hooks/use-mobile";
import { Logo } from "./logo";
import { NavigationMenuDesktop } from "./navigation-menu-desktop";
import { MobileMenu } from "./mobile-menu";
import { UserMenu } from "./user-menu";

interface HeaderProps {
  className?: string;
}

export function Header({ className }: HeaderProps) {
  const { theme, setTheme } = useTheme();
  const isMobile = useIsMobile();
  const [wsConnected, setWsConnected] = useState(true);

  const ThemeToggle = () => (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="sm" className="h-8 w-8 px-0 hover:bg-accent transition-all duration-300">
          <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="bg-popover z-50 border shadow-xl rounded-xl" sideOffset={8}>
        <div className="p-1">
          <DropdownMenuItem onClick={() => setTheme("light")} className="rounded-lg cursor-pointer">
            <Sun className="mr-2 h-4 w-4" />
            <span>Light</span>
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => setTheme("dark")} className="rounded-lg cursor-pointer">
            <Moon className="mr-2 h-4 w-4" />
            <span>Dark</span>
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => setTheme("system")} className="rounded-lg cursor-pointer">
            <Laptop className="mr-2 h-4 w-4" />
            <span>System</span>
          </DropdownMenuItem>
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );

  return (
    <header className={cn(
      "sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur-sm transition-all duration-300 shadow-sm",
      className
    )}>
      <div className="container flex h-16 lg:h-20 items-center justify-between px-3 sm:px-4 lg:px-6 gap-2 sm:gap-4 transition-all duration-300">
        {/* Brand */}
        <div className="flex items-center gap-2 sm:gap-3 lg:gap-8 flex-shrink-0 min-w-0">
          <Logo linkTo="/dashboard" size="md" />
          
          {/* Desktop Navigation */}
          {!isMobile && <NavigationMenuDesktop />}
        </div>

        {/* Right side */}
        <div className="flex items-center gap-1 sm:gap-2 md:gap-3 flex-shrink-0">
          {/* Connection Status - Hidden on small screens */}
          <div className="hidden xl:flex items-center gap-2 px-3 py-1.5 rounded-full bg-muted/30 border border-border/50 flex-shrink-0">
            {wsConnected ? (
              <div className="flex items-center gap-2 text-success">
                <Wifi className="h-3.5 w-3.5" />
                <span className="text-xs font-medium whitespace-nowrap">Connected</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-destructive">
                <WifiOff className="h-3.5 w-3.5" />
                <span className="text-xs font-medium whitespace-nowrap">Disconnected</span>
              </div>
            )}
          </div>

          {/* Theme Toggle */}
          <ThemeToggle />

          {/* Notifications - Hidden on small screens */}
          <Button variant="ghost" size="sm" className="relative hidden sm:flex h-9 w-9 px-0 hover:scale-105 hover:bg-accent transition-all duration-300 rounded-full">
            <Bell className="h-4 w-4" />
            <Badge className="absolute -top-1 -right-1 h-5 w-5 rounded-full p-0 text-[10px] gradient-primary text-primary-foreground border-2 border-background shadow-lg">
              3
            </Badge>
          </Button>

          {/* Mobile Menu */}
          <MobileMenu wsConnected={wsConnected} />

          {/* User Menu */}
          <UserMenu />
        </div>
      </div>
    </header>
  );
}