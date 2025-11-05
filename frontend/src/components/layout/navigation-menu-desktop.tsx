import { Link, useLocation } from "react-router-dom";
import { 
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
  navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu";
import { MapPin, Users, BarChart3, Settings, MessageSquare } from "lucide-react";
import { cn } from "@/lib/utils";

const navigationItems = [
  { title: "Dashboard", href: "/dashboard", icon: MapPin, description: "Overview and quick actions" },
  { title: "Representatives", href: "/mrs", icon: Users, description: "Manage field representatives" },
  { title: "Analytics", href: "/analytics", icon: BarChart3, description: "View reports and insights" },
  { title: "Contact", href: "/contact", icon: MessageSquare, description: "Get in touch" },
  { title: "Settings", href: "/settings", icon: Settings, description: "App configuration" },
];

export function NavigationMenuDesktop() {
  const location = useLocation();

  const isActiveRoute = (href: string) => {
    if (href === "/dashboard" && (location.pathname === "/" || location.pathname === "/dashboard")) {
      return true;
    }
    return location.pathname.startsWith(href) && href !== "/dashboard";
  };

  return (
    <NavigationMenu className="hidden lg:flex">
      <NavigationMenuList className="gap-1">
        {navigationItems.map((item) => (
          <NavigationMenuItem key={item.href}>
            <NavigationMenuLink asChild>
              <Link
                to={item.href}
                className={cn(
                  navigationMenuTriggerStyle(),
                  "flex items-center gap-2 text-muted-foreground hover:text-foreground transition-all duration-300 hover:scale-105 rounded-lg px-4 py-2 h-10",
                  isActiveRoute(item.href) && "bg-gradient-to-r from-primary/15 to-primary-variant/15 text-primary border border-primary/25 shadow-sm font-medium"
                )}
              >
                <item.icon className="h-4 w-4" />
                <span className="font-medium">{item.title}</span>
              </Link>
            </NavigationMenuLink>
          </NavigationMenuItem>
        ))}
      </NavigationMenuList>
    </NavigationMenu>
  );
}