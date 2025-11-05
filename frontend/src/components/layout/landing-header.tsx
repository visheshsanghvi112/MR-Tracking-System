import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Logo } from "./logo";

interface LandingHeaderProps {
  className?: string;
}

export function LandingHeader({ className }: LandingHeaderProps) {
  return (
    <header className={cn(
      "sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur-sm transition-all duration-300 shadow-sm",
      className
    )}>
      <div className="container flex h-16 lg:h-18 items-center justify-between px-4 lg:px-6">
        <Logo linkTo="/" size="md" />
        
        <div className="flex items-center gap-3 sm:gap-4">
          <Button variant="ghost" size="sm" asChild className="hidden sm:flex hover:bg-accent transition-all duration-300">
            <Link to="/login">Sign In</Link>
          </Button>
          <Button size="sm" asChild className="shadow-lg hover:shadow-xl hover:scale-105 transition-all duration-300">
            <Link to="/register">Get Started</Link>
          </Button>
        </div>
      </div>
    </header>
  );
}