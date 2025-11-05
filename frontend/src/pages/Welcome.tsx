import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  MapPin,
  Users,
  BarChart3,
  Shield,
  Smartphone,
  Clock,
  CheckCircle,
  ArrowRight,
  Globe,
  TrendingUp
} from "lucide-react";
import { apiClient } from "@/lib/apiClient";

export default function Welcome() {
  const [activeFeature, setActiveFeature] = useState(0);
  const [loadingStats, setLoadingStats] = useState(true);
  const [statsError, setStatsError] = useState<string | null>(null);
  const [liveStats, setLiveStats] = useState<{
    total_mrs: number;
    active_mrs: number;
    total_visits: number;
    total_distance: number;
    avg_visits_per_mr: number;
  } | null>(null);

  useEffect(() => {
    let ignore = false;
    (async () => {
      try {
        const res = await apiClient.getDashboardStats();
        if (!ignore && res.success) {
          setLiveStats(res.data);
        } else if (!ignore) {
          setStatsError(res.message || "Failed to load stats");
        }
      } catch (e: any) {
        if (!ignore) setStatsError(e?.message || "Failed to load stats");
      } finally {
        if (!ignore) setLoadingStats(false);
      }
    })();
    return () => {
      ignore = true;
    };
  }, []);

  const features = [
    {
      icon: <MapPin className="h-6 w-6" />,
      title: "Real-time Location Tracking",
      description: "Track your medical representatives across India with precise GPS monitoring and route optimization."
    },
    {
      icon: <BarChart3 className="h-6 w-6" />,
      title: "Advanced Analytics",
      description: "Get detailed insights into performance metrics, visit patterns, and ROI analysis."
    },
    {
      icon: <Users className="h-6 w-6" />,
      title: "Team Management",
      description: "Efficiently manage your medical representative teams across multiple territories and regions."
    },
    {
      icon: <Shield className="h-6 w-6" />,
      title: "Secure & Compliant",
      description: "Enterprise-grade security with compliance to Indian data protection regulations."
    }
  ];

  // Remove marketing testimonials and fake counters. Show only live stats when available.

  return (
    <div className="min-h-screen bg-background">
      <main className="flex-1">
        {/* Hero Section */}
        <section className="relative py-12 sm:py-16 md:py-20 lg:py-32 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-primary-light via-background to-accent opacity-50"></div>
          <div className="container relative px-4 sm:px-6">
            <div className="mx-auto max-w-4xl text-center">
              <Badge className="mb-4 sm:mb-6" variant="secondary">
                <Globe className="h-3 w-3 mr-1" />
                Trusted by 500+ Indian Pharma Companies
              </Badge>
              
              <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold tracking-tight text-foreground">
                Track Your Medical Representatives
                <span className="text-primary block mt-2">Everywhere</span>
              </h1>
              
              <p className="mx-auto mt-4 sm:mt-6 max-w-2xl text-base sm:text-lg leading-7 sm:leading-8 text-muted-foreground px-4">
                Complete field force management solution designed for Indian pharmaceutical companies. 
                Track, analyze, and optimize your MR operations with real-time insights and ₹ROI tracking.
              </p>
              
              <div className="mt-8 sm:mt-10 flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4 px-4">
                <Button size="lg" className="w-full sm:w-auto text-sm sm:text-base" asChild>
                  <Link to="/register">
                    Start Free Trial
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
                <Button variant="outline" size="lg" className="w-full sm:w-auto text-sm sm:text-base" asChild>
                  <Link to="/demo">
                    Schedule Demo
                  </Link>
                </Button>
              </div>
              
              <p className="mt-3 sm:mt-4 text-xs sm:text-sm text-muted-foreground px-4">
                14-day free trial • No credit card required • Setup in 5 minutes
              </p>
            </div>
          </div>
        </section>

        {/* Live Stats Section (real data only) */}
        <section className="py-12 sm:py-16 bg-surface">
          <div className="container px-4 sm:px-6">
            <div className="mx-auto max-w-3xl">
              {loadingStats && (
                <div className="text-center text-sm text-muted-foreground">Loading live stats…</div>
              )}
              {!loadingStats && statsError && (
                <div className="text-center text-sm text-muted-foreground">No live stats available</div>
              )}
              {!loadingStats && liveStats && (
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 lg:gap-8">
                  <div className="text-center">
                    <div className="text-2xl sm:text-3xl lg:text-4xl font-bold text-primary">{liveStats.total_mrs}</div>
                    <div className="text-xs sm:text-sm text-muted-foreground mt-1">Total MRs</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl sm:text-3xl lg:text-4xl font-bold text-primary">{liveStats.active_mrs}</div>
                    <div className="text-xs sm:text-sm text-muted-foreground mt-1">Active Today</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl sm:text-3xl lg:text-4xl font-bold text-primary">{liveStats.total_visits}</div>
                    <div className="text-xs sm:text-sm text-muted-foreground mt-1">Total Visits</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl sm:text-3xl lg:text-4xl font-bold text-primary">{Math.round((liveStats.total_distance || 0) as number)}</div>
                    <div className="text-xs sm:text-sm text-muted-foreground mt-1">Distance (km)</div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-12 sm:py-16 md:py-20">
          <div className="container px-4 sm:px-6">
            <div className="mx-auto max-w-2xl text-center mb-12 sm:mb-16">
              <h2 className="text-2xl sm:text-3xl font-bold tracking-tight">
                Everything you need to manage your field force
              </h2>
              <p className="mt-3 sm:mt-4 text-base sm:text-lg text-muted-foreground px-4">
                Comprehensive tools designed specifically for Indian pharmaceutical field operations
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 sm:gap-12 items-center">
              <div className="space-y-4 sm:space-y-6">
                {features.map((feature, index) => (
                  <Card 
                    key={index}
                    className={`cursor-pointer transition-all duration-300 ${
                      activeFeature === index ? 'ring-2 ring-primary bg-primary-light' : 'hover:bg-accent'
                    }`}
                    onClick={() => setActiveFeature(index)}
                  >
                    <CardHeader className="pb-3">
                      <div className="flex items-center gap-3">
                        <div className="flex h-8 w-8 sm:h-10 sm:w-10 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                          {feature.icon}
                        </div>
                        <CardTitle className="text-base sm:text-lg">{feature.title}</CardTitle>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <CardDescription className="text-sm sm:text-base">
                        {feature.description}
                      </CardDescription>
                    </CardContent>
                  </Card>
                ))}
              </div>

              <div className="relative order-first lg:order-last">
                <div className="aspect-video rounded-lg bg-gradient-to-br from-primary-light to-accent border-2 border-border shadow-lg flex items-center justify-center p-4">
                  <div className="text-center">
                    <MapPin className="h-12 w-12 sm:h-16 sm:w-16 text-primary mx-auto mb-3 sm:mb-4" />
                    <h3 className="text-lg sm:text-xl font-semibold mb-2">Interactive Dashboard</h3>
                    <p className="text-muted-foreground text-sm sm:text-base max-w-xs mx-auto">
                      Real-time view of your medical representatives across India with detailed analytics
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Benefits Section */}
        <section className="py-12 sm:py-16 md:py-20 bg-surface">
          <div className="container px-4 sm:px-6">
            <div className="mx-auto max-w-2xl text-center mb-12 sm:mb-16">
              <h2 className="text-2xl sm:text-3xl font-bold tracking-tight">
                Why Choose FieldSync Pro?
              </h2>
              <p className="mt-3 sm:mt-4 text-base sm:text-lg text-muted-foreground px-4">
                Built specifically for the Indian pharmaceutical industry
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 lg:gap-8">
              {[
                {
                  icon: <Smartphone className="h-6 w-6" />,
                  title: "Mobile-First Design",
                  description: "Works perfectly on all devices with offline capabilities for remote areas"
                },
                {
                  icon: <Clock className="h-6 w-6" />,
                  title: "Real-time Updates",
                  description: "Get instant notifications and live tracking updates throughout the day"
                },
                {
                  icon: <TrendingUp className="h-6 w-6" />,
                  title: "ROI Optimization",
                  description: "Track costs in ₹ and optimize routes to maximize return on investment"
                }
              ].map((benefit, index) => (
                <Card key={index} className="text-center">
                  <CardHeader className="pb-4">
                    <div className="flex h-10 w-10 sm:h-12 sm:w-12 items-center justify-center rounded-lg bg-primary text-primary-foreground mx-auto">
                      {benefit.icon}
                    </div>
                    <CardTitle className="text-base sm:text-lg">{benefit.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-sm sm:text-base">
                      {benefit.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        {/* Remove testimonials/fake social proof */}

        {/* CTA Section */}
        <section className="py-12 sm:py-16 md:py-20 bg-primary text-primary-foreground">
          <div className="container px-4 sm:px-6 text-center">
            <h2 className="text-2xl sm:text-3xl font-bold tracking-tight mb-3 sm:mb-4">
              Ready to Transform Your Field Operations?
            </h2>
            <p className="text-lg sm:text-xl opacity-90 mb-6 sm:mb-8 max-w-2xl mx-auto px-4">
              Join hundreds of Indian pharmaceutical companies already using our platform
            </p>
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center px-4">
              <Button size="lg" variant="secondary" className="w-full sm:w-auto" asChild>
                <Link to="/register">
                  Start Free Trial
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" className="w-full sm:w-auto border-primary-foreground text-primary-foreground hover:bg-primary-foreground hover:text-primary" asChild>
                <Link to="/contact">
                  Contact Sales
                </Link>
              </Button>
            </div>
            <p className="mt-3 sm:mt-4 text-xs sm:text-sm opacity-75 px-4">
              Questions? Call us at +91-9876543210 or email sales@mrtracking.in
            </p>
          </div>
        </section>
      </main>

    </div>
  );
}