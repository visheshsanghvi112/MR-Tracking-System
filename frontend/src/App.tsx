import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { HelmetProvider } from "react-helmet-async";
import { ThemeProvider } from "@/providers/theme-provider";
import Dashboard from "./pages/Dashboard";
import MRDetail from "./pages/MRDetail";
import MRs from "./pages/MRs";
import Analytics from "./pages/Analytics";
import Settings from "./pages/Settings";
import Profile from "./pages/Profile";
import Contact from "./pages/Contact";
import NotFound from "./pages/NotFound";
import Welcome from "./pages/Welcome";
import Login from "./pages/Login";
import Register from "./pages/Register";
import { Footer } from "./components/layout/footer";
import { Header } from "./components/layout/header";
import { LandingHeader } from "./components/layout/landing-header";

const queryClient = new QueryClient();

function AppLayout() {
  const location = useLocation();
  const isLandingPage = ['/', '/login', '/register'].includes(location.pathname);
  
  return (
    <div className="flex min-h-screen flex-col">
      {isLandingPage ? <LandingHeader /> : <Header />}
      <div className="flex-1">
        <Routes>
          <Route path="/" element={<Welcome />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/mrs" element={<MRs />} />
          <Route path="/mr/:id" element={<MRDetail />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/profile" element={<Profile />} />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
      <Footer />
    </div>
  );
}

const App = () => (
  <HelmetProvider>
    <ThemeProvider defaultTheme="system" storageKey="mr-tracking-theme">
      <QueryClientProvider client={queryClient}>
        <TooltipProvider>
          <Toaster />
          <Sonner />
          <BrowserRouter>
            <AppLayout />
          </BrowserRouter>
        </TooltipProvider>
      </QueryClientProvider>
    </ThemeProvider>
  </HelmetProvider>
);

export default App;
