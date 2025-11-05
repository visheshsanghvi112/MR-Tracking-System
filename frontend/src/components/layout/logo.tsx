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
      container: "h-6 w-6 sm:h-8 sm:w-8",
      icon: "h-3 w-3 sm:h-4 sm:w-4",
      text: "text-xs sm:text-sm",
      subtitle: "text-[10px] sm:text-xs"
    },
    md: {
      container: "h-8 w-8 sm:h-10 sm:w-10 lg:h-12 lg:w-12",
      icon: "h-4 w-4 sm:h-5 sm:w-5 lg:h-6 lg:w-6",
      text: "text-sm sm:text-lg lg:text-xl",
      subtitle: "text-xs sm:text-sm"
    },
    lg: {
      container: "h-10 w-10 sm:h-12 sm:w-12 lg:h-16 lg:w-16",
      icon: "h-5 w-5 sm:h-6 sm:w-6 lg:h-8 lg:w-8",
      text: "text-lg sm:text-xl lg:text-2xl",
      subtitle: "text-sm sm:text-base"
    }
  };

  const currentSize = sizeClasses[size];

  return (
    <Link 
      to={linkTo} 
      className={cn(
        "flex items-center gap-2 sm:gap-3 group shrink-0 transition-all duration-300 hover:scale-105",
        className
      )}
    >
      <div className={cn(
        "flex items-center justify-center rounded-2xl gradient-primary shadow-lg group-hover:shadow-primary/40 group-hover:scale-105 transition-all duration-300 ring-2 ring-primary/10",
        currentSize.container
      )}>
        <MapPin className={cn(
          "text-primary-foreground drop-shadow-lg",
          currentSize.icon
        )} />
      </div>
      <div className="flex flex-col leading-tight">
        <span className={cn(
          "font-black bg-gradient-to-r from-primary via-primary-variant to-accent bg-clip-text text-transparent drop-shadow-sm whitespace-nowrap tracking-tight",
          currentSize.text
        )}>
          FieldSync
        </span>
        <span className={cn(
          "font-semibold text-muted-foreground tracking-wider uppercase opacity-80",
          currentSize.subtitle
        )}>
          Pro
        </span>
      </div>
    </Link>
  );
}