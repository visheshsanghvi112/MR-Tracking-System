import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { 
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { User, LogOut, Settings } from "lucide-react";

export function UserMenu() {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="relative h-9 w-9 rounded-full hover:ring-2 hover:ring-primary/20 transition-all duration-300">
          <Avatar className="h-9 w-9 ring-2 ring-background shadow-md">
            <AvatarFallback className="bg-gradient-to-r from-primary to-primary-variant text-primary-foreground font-semibold">
              AD
            </AvatarFallback>
          </Avatar>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent 
        className="w-64 bg-popover z-50 border shadow-xl rounded-xl" 
        align="end" 
        forceMount
        sideOffset={8}
      >
        <DropdownMenuLabel className="font-normal p-4">
          <div className="flex flex-col space-y-2">
            <p className="text-sm font-semibold leading-none text-popover-foreground">Admin User</p>
            <p className="text-xs leading-none text-muted-foreground">
              admin@company.com
            </p>
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator className="bg-border/50" />
        <div className="p-1">
          <DropdownMenuItem className="text-popover-foreground hover:bg-accent hover:text-accent-foreground rounded-lg p-3 cursor-pointer" asChild>
            <Link to="/profile" className="flex items-center">
              <User className="mr-3 h-4 w-4" />
              <span>Profile</span>
            </Link>
          </DropdownMenuItem>
          <DropdownMenuItem className="text-popover-foreground hover:bg-accent hover:text-accent-foreground rounded-lg p-3 cursor-pointer" asChild>
            <Link to="/settings" className="flex items-center">
              <Settings className="mr-3 h-4 w-4" />
              <span>Settings</span>
            </Link>
          </DropdownMenuItem>
        </div>
        <DropdownMenuSeparator className="bg-border/50" />
        <div className="p-1">
          <DropdownMenuItem className="text-popover-foreground hover:bg-accent hover:text-accent-foreground rounded-lg p-3 cursor-pointer">
            <LogOut className="mr-3 h-4 w-4" />
            <span>Log out</span>
          </DropdownMenuItem>
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}