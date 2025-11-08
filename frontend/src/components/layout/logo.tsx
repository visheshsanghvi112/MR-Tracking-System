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
      text: "text-[10px] sm:text-xs",
      subtitle: "text-[7px] sm:text-[8px]"
    },
    md: {
      container: "h-8 w-8 sm:h-9 sm:w-9 md:h-10 md:w-10",
      icon: "h-4 w-4 sm:h-4.5 sm:w-4.5 md:h-5 md:w-5",
      text: "text-[11px] sm:text-xs md:text-sm lg:text-base",
      subtitle: "text-[7px] sm:text-[9px] md:text-[10px]"
    },
    lg: {
      container: "h-9 w-9 sm:h-10 sm:w-10 md:h-12 md:w-12",
      icon: "h-4.5 w-4.5 sm:h-5 sm:w-5 md:h-6 md:w-6",
      text: "text-xs sm:text-sm md:text-base lg:text-lg",
      subtitle: "text-[8px] sm:text-[10px] md:text-xs"
    }
  };

  const currentSize = sizeClasses[size];

  return (
    <Link 
      to={linkTo} 
      className={cn(
        "flex items-center gap-1 sm:gap-1.5 group flex-shrink-0 hover:opacity-90 transition-opacity",
        className
      )}
    >
      <div className={cn(
        "flex items-center justify-center rounded-lg gradient-primary shadow-sm flex-shrink-0",
        currentSize.container
      )}>
        <MapPin className={cn(
          "text-primary-foreground flex-shrink-0",
          currentSize.icon
        )} />
      </div>
      <div className="flex flex-col leading-none">
        <span className={cn(
          "font-black bg-gradient-to-r from-primary to-primary-variant bg-clip-text text-transparent whitespace-nowrap",
          currentSize.text
        )}>
          FieldSync
        </span>
        <span className={cn(
          "font-bold text-muted-foreground tracking-widest uppercase opacity-60 whitespace-nowrap hidden xs:block",
          currentSize.subtitle
        )}>
          PRO
        </span>
      </div>
    </Link>
  );
}