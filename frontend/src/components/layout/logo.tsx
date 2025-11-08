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
      container: "h-8 w-8",
      icon: "h-4 w-4",
      text: "text-xs",
      subtitle: "text-[8px]"
    },
    md: {
      container: "h-9 w-9 sm:h-10 sm:w-10",
      icon: "h-4 w-4 sm:h-5 sm:w-5",
      text: "text-xs sm:text-sm md:text-base",
      subtitle: "text-[8px] sm:text-[10px]"
    },
    lg: {
      container: "h-10 w-10 sm:h-12 sm:w-12",
      icon: "h-5 w-5 sm:h-6 sm:w-6",
      text: "text-sm sm:text-base lg:text-lg",
      subtitle: "text-[10px] sm:text-xs"
    }
  };

  const currentSize = sizeClasses[size];

  return (
    <Link 
      to={linkTo} 
      className={cn(
        "flex items-center gap-1 sm:gap-1.5 md:gap-2 group flex-shrink-0 transition-transform duration-200 hover:scale-[1.01] overflow-visible",
        className
      )}
      style={{ minWidth: 'fit-content' }}
    >
      <div className={cn(
        "flex items-center justify-center rounded-lg sm:rounded-xl gradient-primary shadow-md group-hover:shadow-lg transition-all duration-200 flex-shrink-0",
        currentSize.container
      )}>
        <MapPin className={cn(
          "text-primary-foreground flex-shrink-0",
          currentSize.icon
        )} />
      </div>
      <div className="flex flex-col leading-none justify-center overflow-visible" style={{ minWidth: 'fit-content' }}>
        <span className={cn(
          "font-black bg-gradient-to-r from-primary via-primary-variant to-accent bg-clip-text text-transparent whitespace-nowrap tracking-tight",
          currentSize.text
        )}>
          FieldSync
        </span>
        <span className={cn(
          "font-bold text-muted-foreground tracking-widest uppercase opacity-70 whitespace-nowrap mt-0",
          currentSize.subtitle
        )}>
          PRO
        </span>
      </div>
    </Link>
  );
}