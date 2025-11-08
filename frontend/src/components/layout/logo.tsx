import { Link } from "react-router-dom";
import { MapPin } from "lucide-react";
import { cn } from "@/lib/utils";

interface LogoProps {
  className?: string;
  linkTo?: string;
  size?: "sm" | "md" | "lg";
}

export function Logo({ className, linkTo = "/", size = "md" }: LogoProps) {
  const sizeClasses = {
    sm: {
      container: "h-7 w-7 sm:h-8 sm:w-8",
      icon: "h-3.5 w-3.5 sm:h-4 sm:w-4",
      text: "text-xs sm:text-sm",
      subtitle: "text-[9px] sm:text-[10px]"
    },
    md: {
      container: "h-9 w-9 sm:h-10 sm:w-10",
      icon: "h-4.5 w-4.5 sm:h-5 sm:w-5",
      text: "text-sm sm:text-base lg:text-lg",
      subtitle: "text-[10px] sm:text-xs"
    },
    lg: {
      container: "h-11 w-11 sm:h-12 sm:w-12 lg:h-14 lg:w-14",
      icon: "h-5.5 w-5.5 sm:h-6 sm:w-6 lg:h-7 lg:w-7",
      text: "text-base sm:text-lg lg:text-xl",
      subtitle: "text-xs sm:text-sm"
    }
  };

  const currentSize = sizeClasses[size];

  return (
    <Link 
      to={linkTo} 
      className={cn(
        "flex items-center gap-1.5 sm:gap-2 group flex-shrink-0 transition-all duration-300 hover:scale-[1.02]",
        className
      )}
    >
      <div className={cn(
        "flex items-center justify-center rounded-xl sm:rounded-2xl gradient-primary shadow-lg group-hover:shadow-primary/40 group-hover:scale-105 transition-all duration-300 ring-2 ring-primary/10 flex-shrink-0",
        currentSize.container
      )}>
        <MapPin className={cn(
          "text-primary-foreground drop-shadow-lg flex-shrink-0",
          currentSize.icon
        )} />
      </div>
      <div className="flex flex-col leading-tight justify-center min-w-0">
        <span className={cn(
          "font-black bg-gradient-to-r from-primary via-primary-variant to-accent bg-clip-text text-transparent drop-shadow-sm whitespace-nowrap tracking-tight",
          currentSize.text
        )}>
          FieldSync
        </span>
        <span className={cn(
          "font-semibold text-muted-foreground tracking-wider uppercase opacity-80 whitespace-nowrap -mt-0.5",
          currentSize.subtitle
        )}>
          Pro
        </span>
      </div>
    </Link>
  );
}