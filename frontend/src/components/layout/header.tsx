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
      "sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur-sm transition-all duration-300 shadow-sm overflow-visible",
      className
    )}>
      <div className="w-full flex h-16 sm:h-18 lg:h-20 items-center px-2 sm:px-3 md:px-4 lg:px-6">
        {/* Brand - PRIORITY: Never allow compression */}
        <div className="flex items-center gap-1.5 sm:gap-2 lg:gap-6 flex-shrink-0 mr-auto">
          <Logo linkTo="/dashboard" size="md" />
          
          {/* Desktop Navigation */}
          {!isMobile && <div className="ml-2 lg:ml-4"><NavigationMenuDesktop /></div>}
        </div>

        {/* Right side - Allow MINIMUM shrinking */}
        <div className="flex items-center gap-0.5 sm:gap-1 md:gap-2 flex-shrink ml-2">
          {/* Connection Status - Hidden on small screens */}
          <div className="hidden xl:flex items-center gap-2 px-2 py-1 rounded-full bg-muted/30 border border-border/50">
            {wsConnected ? (
              <div className="flex items-center gap-1.5 text-success">
                <Wifi className="h-3 w-3" />
                <span className="text-[10px] font-medium whitespace-nowrap">Connected</span>
              </div>
            ) : (
              <div className="flex items-center gap-1.5 text-destructive">
                <WifiOff className="h-3 w-3" />
                <span className="text-[10px] font-medium whitespace-nowrap">Offline</span>
              </div>
            )}
          </div>

          {/* Theme Toggle */}
          <ThemeToggle />

          {/* Notifications - Hidden on small screens */}
          <Button variant="ghost" size="sm" className="relative hidden sm:flex h-8 w-8 px-0 hover:bg-accent transition-colors rounded-full">
            <Bell className="h-3.5 w-3.5" />
            <Badge className="absolute -top-0.5 -right-0.5 h-4 w-4 rounded-full p-0 text-[9px] gradient-primary text-primary-foreground border border-background">
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