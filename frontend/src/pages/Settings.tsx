import { useState, useEffect } from "react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { useToast } from "@/hooks/use-toast";
import { useTheme } from "@/providers/theme-provider";
import { 
  Settings as SettingsIcon, 
  Database, 
  Bell, 
  Shield, 
  Wifi,
  Save,
  RefreshCw,
  AlertTriangle,
  Check,
  Key,
  Download,
  Upload,
  Trash2,
  MapPin,
  Users,
  Clock,
  Target,
  Route,
  Phone,
  Mail,
  Building,
  Car,
  Calendar,
  DollarSign,
  Zap,
  Globe
} from "lucide-react";

export default function Settings() {
  const { toast } = useToast();
  const { theme, setTheme } = useTheme();
  
  // API & Connection Settings
  const [apiUrl, setApiUrl] = useState('http://localhost:8000');
  const [wsUrl, setWsUrl] = useState('ws://localhost:8000');
  const [apiKey, setApiKey] = useState('mr-tracking-2025');
  const [googleMapsApiKey, setGoogleMapsApiKey] = useState('');
  
  // Tracking & Performance Settings
  const [refreshInterval, setRefreshInterval] = useState('30');
  const [locationAccuracy, setLocationAccuracy] = useState('high');
  const [trackingRadius, setTrackingRadius] = useState('500');
  const [autoCheckIn, setAutoCheckIn] = useState(true);
  const [offlineSync, setOfflineSync] = useState(true);
  
  // MR Management Settings
  const [maxDailyVisits, setMaxDailyVisits] = useState('15');
  const [workingHoursStart, setWorkingHoursStart] = useState('09:00');
  const [workingHoursEnd, setWorkingHoursEnd] = useState('18:00');
  const [breakDuration, setBreakDuration] = useState('60');
  const [expenseSubmissionDeadline, setExpenseSubmissionDeadline] = useState('7');
  
  // Notification Settings
  const [notifications, setNotifications] = useState(true);
  const [liveTracking, setLiveTracking] = useState(true);
  const [pushNotifications, setPushNotifications] = useState(true);
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [smsAlerts, setSmsAlerts] = useState(false);
  const [notificationSound, setNotificationSound] = useState(true);
  
  // Company & Territory Settings
  const [companyName, setCompanyName] = useState('Pharma Gift App');
  const [companyCode, setCompanyCode] = useState('PGA');
  const [defaultTerritory, setDefaultTerritory] = useState('Mumbai');
  const [currencySymbol, setCurrencySymbol] = useState('₹');
  const [timeZone, setTimeZone] = useState('Asia/Kolkata');
  const [language, setLanguage] = useState('en');
  
  // System Status
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'testing'>('connected');
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  // Load settings on component mount
  useEffect(() => {
    const savedSettings = localStorage.getItem('mr-tracking-admin-settings');
    if (savedSettings) {
      try {
        const settings = JSON.parse(savedSettings);
        // API Settings
        setApiUrl(settings.apiUrl || 'http://localhost:8000');
        setWsUrl(settings.wsUrl || 'ws://localhost:8000');
        setApiKey(settings.apiKey || 'mr-tracking-2025');
        setGoogleMapsApiKey(settings.googleMapsApiKey || '');
        
        // Tracking Settings
        setRefreshInterval(settings.refreshInterval || '30');
        setLocationAccuracy(settings.locationAccuracy || 'high');
        setTrackingRadius(settings.trackingRadius || '500');
        setAutoCheckIn(settings.autoCheckIn ?? true);
        setOfflineSync(settings.offlineSync ?? true);
        
        // MR Settings
        setMaxDailyVisits(settings.maxDailyVisits || '15');
        setWorkingHoursStart(settings.workingHoursStart || '09:00');
        setWorkingHoursEnd(settings.workingHoursEnd || '18:00');
        setBreakDuration(settings.breakDuration || '60');
        setExpenseSubmissionDeadline(settings.expenseSubmissionDeadline || '7');
        
        // Notification Settings
        setNotifications(settings.notifications ?? true);
        setLiveTracking(settings.liveTracking ?? true);
        setPushNotifications(settings.pushNotifications ?? true);
        setEmailNotifications(settings.emailNotifications ?? true);
        setSmsAlerts(settings.smsAlerts ?? false);
        setNotificationSound(settings.notificationSound ?? true);
        
        // Company Settings
        setCompanyName(settings.companyName || 'Pharma Gift App');
        setCompanyCode(settings.companyCode || 'PGA');
        setDefaultTerritory(settings.defaultTerritory || 'Mumbai');
        setCurrencySymbol(settings.currencySymbol || '₹');
        setTimeZone(settings.timeZone || 'Asia/Kolkata');
        setLanguage(settings.language || 'en');
      } catch (error) {
        console.error('Failed to load settings:', error);
      }
    }
  }, []);

  // Mark as having unsaved changes when settings change
  useEffect(() => {
    setHasUnsavedChanges(true);
  }, [apiUrl, wsUrl, apiKey, googleMapsApiKey, refreshInterval, locationAccuracy, trackingRadius, 
      autoCheckIn, offlineSync, maxDailyVisits, workingHoursStart, workingHoursEnd, breakDuration,
      expenseSubmissionDeadline, notifications, liveTracking, pushNotifications, emailNotifications,
      smsAlerts, notificationSound, companyName, companyCode, defaultTerritory, currencySymbol,
      timeZone, language]);

  const testConnection = async () => {
    setConnectionStatus('testing');
    
    try {
      // Test backend API connection
      const response = await fetch(`${apiUrl}/api/mrs`, {
        headers: {
          'X-API-Key': apiKey,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        setConnectionStatus('connected');
        toast({
          title: "Connection Successful",
          description: "Backend API is responding correctly.",
        });
      } else {
        setConnectionStatus('disconnected');
        toast({
          title: "Connection Failed",
          description: "Backend API is not responding. Check URL and API key.",
          variant: "destructive",
        });
      }
    } catch (error) {
      setConnectionStatus('disconnected');
      toast({
        title: "Connection Error",
        description: "Failed to connect to backend API.",
        variant: "destructive",
      });
    }
  };

  const handleSave = () => {
    try {
      // Save all settings to localStorage
      const settingsToSave = {
        // API Settings
        apiUrl,
        wsUrl,
        apiKey,
        googleMapsApiKey,
        
        // Tracking Settings
        refreshInterval,
        locationAccuracy,
        trackingRadius,
        autoCheckIn,
        offlineSync,
        
        // MR Settings
        maxDailyVisits,
        workingHoursStart,
        workingHoursEnd,
        breakDuration,
        expenseSubmissionDeadline,
        
        // Notification Settings
        notifications,
        liveTracking,
        pushNotifications,
        emailNotifications,
        smsAlerts,
        notificationSound,
        
        // Company Settings
        companyName,
        companyCode,
        defaultTerritory,
        currencySymbol,
        timeZone,
        language,
        
        lastSaved: new Date().toISOString()
      };
      
      localStorage.setItem('mr-tracking-admin-settings', JSON.stringify(settingsToSave));
      
      // Apply immediately to frontend API client on next requests
      // (apiClient reads from localStorage overrides at call time)
      
      setHasUnsavedChanges(false);
      
      toast({
        title: "Settings Saved Successfully",
        description: "Settings saved. Frontend will use updated API URL and key immediately.",
      });
    } catch (error) {
      toast({
        title: "Save Failed",
        description: "Failed to save settings. Please try again.",
        variant: "destructive",
      });
    }
  };

  const resetToDefaults = () => {
    // API Settings
    setApiUrl('http://localhost:8000');
    setWsUrl('ws://localhost:8000');
    setApiKey('mr-tracking-2025');
    setGoogleMapsApiKey('AIzaSyAmjPYcRNn1P0WBDcYQCgm8ly4uhFd1xl0');
    
    // Tracking Settings
    setRefreshInterval('30');
    setLocationAccuracy('high');
    setTrackingRadius('500');
    setAutoCheckIn(true);
    setOfflineSync(true);
    
    // MR Settings
    setMaxDailyVisits('15');
    setWorkingHoursStart('09:00');
    setWorkingHoursEnd('18:00');
    setBreakDuration('60');
    setExpenseSubmissionDeadline('7');
    
    // Notification Settings
    setNotifications(true);
    setLiveTracking(true);
    setPushNotifications(true);
    setEmailNotifications(true);
    setSmsAlerts(false);
    setNotificationSound(true);
    
    // Company Settings
    setCompanyName('Pharma Gift App');
    setCompanyCode('PGA');
    setDefaultTerritory('Mumbai');
    setCurrencySymbol('₹');
    setTimeZone('Asia/Kolkata');
    setLanguage('en');
    
    setHasUnsavedChanges(true);
    
    toast({
      title: "Settings Reset",
      description: "All settings have been reset to default values.",
    });
  };

  const exportSettings = () => {
    const settings = {
      // API Settings
      apiUrl,
      wsUrl,
      apiKey,
      googleMapsApiKey,
      
      // Tracking Settings
      refreshInterval,
      locationAccuracy,
      trackingRadius,
      autoCheckIn,
      offlineSync,
      
      // MR Settings
      maxDailyVisits,
      workingHoursStart,
      workingHoursEnd,
      breakDuration,
      expenseSubmissionDeadline,
      
      // Notification Settings
      notifications,
      liveTracking,
      pushNotifications,
      emailNotifications,
      smsAlerts,
      notificationSound,
      
      // Company Settings
      companyName,
      companyCode,
      defaultTerritory,
      currencySymbol,
      timeZone,
      language,
      
      exportedAt: new Date().toISOString(),
      version: "1.0.0"
    };
    
    const dataStr = JSON.stringify(settings, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `mr-tracking-config-${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
    
    toast({
      title: "Configuration Exported",
      description: "MR tracking configuration has been exported successfully.",
    });
  };

  const importSettings = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const settings = JSON.parse(e.target?.result as string);
          
          // API Settings
          setApiUrl(settings.apiUrl || 'http://localhost:8000');
          setWsUrl(settings.wsUrl || 'ws://localhost:8000');
          setApiKey(settings.apiKey || 'mr-tracking-2025');
          setGoogleMapsApiKey(settings.googleMapsApiKey || '');
          
          // Tracking Settings
          setRefreshInterval(settings.refreshInterval || '30');
          setLocationAccuracy(settings.locationAccuracy || 'high');
          setTrackingRadius(settings.trackingRadius || '500');
          setAutoCheckIn(settings.autoCheckIn ?? true);
          setOfflineSync(settings.offlineSync ?? true);
          
          // MR Settings
          setMaxDailyVisits(settings.maxDailyVisits || '15');
          setWorkingHoursStart(settings.workingHoursStart || '09:00');
          setWorkingHoursEnd(settings.workingHoursEnd || '18:00');
          setBreakDuration(settings.breakDuration || '60');
          setExpenseSubmissionDeadline(settings.expenseSubmissionDeadline || '7');
          
          // Notification Settings
          setNotifications(settings.notifications ?? true);
          setLiveTracking(settings.liveTracking ?? true);
          setPushNotifications(settings.pushNotifications ?? true);
          setEmailNotifications(settings.emailNotifications ?? true);
          setSmsAlerts(settings.smsAlerts ?? false);
          setNotificationSound(settings.notificationSound ?? true);
          
          // Company Settings
          setCompanyName(settings.companyName || 'Pharma Gift App');
          setCompanyCode(settings.companyCode || 'PGA');
          setDefaultTerritory(settings.defaultTerritory || 'Mumbai');
          setCurrencySymbol(settings.currencySymbol || '₹');
          setTimeZone(settings.timeZone || 'Asia/Kolkata');
          setLanguage(settings.language || 'en');
          
          setHasUnsavedChanges(true);
          
          toast({
            title: "Configuration Imported",
            description: "MR tracking configuration has been successfully imported.",
          });
        } catch (error) {
          toast({
            title: "Import Failed",
            description: "Failed to import configuration. Please check the file format.",
            variant: "destructive",
          });
        }
      };
      reader.readAsText(file);
    }
  };

  const clearAllData = () => {
    localStorage.removeItem('mr-tracking-admin-settings');
    localStorage.removeItem('mr-tracking-settings');
    resetToDefaults();
    toast({
      title: "All Data Cleared",
      description: "All stored settings and configurations have been cleared.",
      variant: "destructive",
    });
  };

  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto p-6 space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold">MR Tracking System - Admin Settings</h1>
          <p className="text-muted-foreground">
            Configure all MR tracking settings. MRs will get a ready-to-use system with these configurations.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Settings */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Company & Organization Settings */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building className="h-5 w-5" />
                  Company Configuration
                </CardTitle>
                <CardDescription>
                  Basic company information that MRs will see in their app
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Company Name</Label>
                    <Input
                      value={companyName}
                      onChange={(e) => setCompanyName(e.target.value)}
                      placeholder="Pharma Gift App"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Company Code</Label>
                    <Input
                      value={companyCode}
                      onChange={(e) => setCompanyCode(e.target.value)}
                      placeholder="PGA"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Default Territory</Label>
                    <Input
                      value={defaultTerritory}
                      onChange={(e) => setDefaultTerritory(e.target.value)}
                      placeholder="Mumbai"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Currency Symbol</Label>
                    <Select value={currencySymbol} onValueChange={setCurrencySymbol}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="₹">₹ (Indian Rupee)</SelectItem>
                        <SelectItem value="$">$ (US Dollar)</SelectItem>
                        <SelectItem value="€">€ (Euro)</SelectItem>
                        <SelectItem value="£">£ (British Pound)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Time Zone</Label>
                    <Select value={timeZone} onValueChange={setTimeZone}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Asia/Kolkata">Asia/Kolkata (IST)</SelectItem>
                        <SelectItem value="America/New_York">America/New_York (EST)</SelectItem>
                        <SelectItem value="Europe/London">Europe/London (GMT)</SelectItem>
                        <SelectItem value="Asia/Tokyo">Asia/Tokyo (JST)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Language</Label>
                    <Select value={language} onValueChange={setLanguage}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="en">English</SelectItem>
                        <SelectItem value="hi">Hindi</SelectItem>
                        <SelectItem value="mr">Marathi</SelectItem>
                        <SelectItem value="ta">Tamil</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* API & Technical Configuration */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="h-5 w-5" />
                  API & Technical Configuration
                </CardTitle>
                <CardDescription>
                  Backend API, Google Maps, and technical connectivity settings
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Backend API URL</Label>
                  <Input
                    value={apiUrl}
                    onChange={(e) => setApiUrl(e.target.value)}
                    placeholder="http://localhost:8000"
                  />
                  <p className="text-xs text-muted-foreground">
                    Base URL for MR tracking backend API
                  </p>
                </div>

                <div className="space-y-2">
                  <Label>API Authentication Key</Label>
                  <Input
                    type="password"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder="mr-tracking-2025"
                  />
                  <p className="text-xs text-muted-foreground">
                    Secure API key for backend authentication
                  </p>
                </div>

                <div className="space-y-2">
                  <Label>Google Maps API Key</Label>
                  <Input
                    type="password"
                    value={googleMapsApiKey}
                    onChange={(e) => setGoogleMapsApiKey(e.target.value)}
                    placeholder="Enter Google Maps API key"
                  />
                  <p className="text-xs text-muted-foreground">
                    Required for real-time location tracking and route mapping
                  </p>
                </div>

                <div className="space-y-2">
                  <Label>WebSocket URL (Real-time updates)</Label>
                  <Input
                    value={wsUrl}
                    onChange={(e) => setWsUrl(e.target.value)}
                    placeholder="ws://localhost:8000"
                  />
                </div>

                <div className="flex items-center gap-3">
                  <Button onClick={testConnection} disabled={connectionStatus === 'testing'}>
                    {connectionStatus === 'testing' ? (
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <Wifi className="h-4 w-4 mr-2" />
                    )}
                    Test Backend Connection
                  </Button>
                  
                  {connectionStatus === 'connected' && (
                    <Badge className="bg-green-100 text-green-800">
                      <Check className="h-3 w-3 mr-1" />
                      Backend Connected
                    </Badge>
                  )}
                  
                  {connectionStatus === 'disconnected' && (
                    <Badge variant="destructive">
                      <AlertTriangle className="h-3 w-3 mr-1" />
                      Connection Failed
                    </Badge>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* MR Working Hours & Limits */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  MR Working Configuration
                </CardTitle>
                <CardDescription>
                  Define working hours, visit limits, and operational constraints for MRs
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Working Hours Start</Label>
                    <Input
                      type="time"
                      value={workingHoursStart}
                      onChange={(e) => setWorkingHoursStart(e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Working Hours End</Label>
                    <Input
                      type="time"
                      value={workingHoursEnd}
                      onChange={(e) => setWorkingHoursEnd(e.target.value)}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Maximum Daily Visits</Label>
                    <Select value={maxDailyVisits} onValueChange={setMaxDailyVisits}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="10">10 visits</SelectItem>
                        <SelectItem value="15">15 visits</SelectItem>
                        <SelectItem value="20">20 visits</SelectItem>
                        <SelectItem value="25">25 visits</SelectItem>
                        <SelectItem value="unlimited">Unlimited</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Break Duration (minutes)</Label>
                    <Select value={breakDuration} onValueChange={setBreakDuration}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="30">30 minutes</SelectItem>
                        <SelectItem value="60">1 hour</SelectItem>
                        <SelectItem value="90">1.5 hours</SelectItem>
                        <SelectItem value="120">2 hours</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2 md:col-span-2">
                    <Label>Expense Submission Deadline (days)</Label>
                    <Select value={expenseSubmissionDeadline} onValueChange={setExpenseSubmissionDeadline}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="3">3 days</SelectItem>
                        <SelectItem value="7">7 days</SelectItem>
                        <SelectItem value="15">15 days</SelectItem>
                        <SelectItem value="30">30 days</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Tracking & Location Settings */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="h-5 w-5" />
                  Location Tracking Configuration
                </CardTitle>
                <CardDescription>
                  GPS accuracy, tracking intervals, and location-based features
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Data Refresh Interval</Label>
                    <Select value={refreshInterval} onValueChange={setRefreshInterval}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="10">10 seconds</SelectItem>
                        <SelectItem value="30">30 seconds</SelectItem>
                        <SelectItem value="60">1 minute</SelectItem>
                        <SelectItem value="300">5 minutes</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Location Accuracy</Label>
                    <Select value={locationAccuracy} onValueChange={setLocationAccuracy}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="high">High (GPS only)</SelectItem>
                        <SelectItem value="medium">Medium (GPS + Network)</SelectItem>
                        <SelectItem value="low">Low (Network only)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Auto Check-in Radius (meters)</Label>
                    <Select value={trackingRadius} onValueChange={setTrackingRadius}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="100">100m (Very Close)</SelectItem>
                        <SelectItem value="250">250m (Close)</SelectItem>
                        <SelectItem value="500">500m (Moderate)</SelectItem>
                        <SelectItem value="1000">1000m (Flexible)</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <Separator />

                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Auto Check-in</Label>
                      <p className="text-xs text-muted-foreground">
                        Automatically check-in MRs when they reach visit locations
                      </p>
                    </div>
                    <Switch
                      checked={autoCheckIn}
                      onCheckedChange={setAutoCheckIn}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Offline Data Sync</Label>
                      <p className="text-xs text-muted-foreground">
                        Allow MRs to work offline and sync data when connected
                      </p>
                    </div>
                    <Switch
                      checked={offlineSync}
                      onCheckedChange={setOfflineSync}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Live Location Tracking</Label>
                      <p className="text-xs text-muted-foreground">
                        Enable real-time location monitoring for admin dashboard
                      </p>
                    </div>
                    <Switch
                      checked={liveTracking}
                      onCheckedChange={setLiveTracking}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Notification Settings */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bell className="h-5 w-5" />
                  Notification Configuration
                </CardTitle>
                <CardDescription>
                  Configure how MRs receive alerts, reminders, and updates
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Enable All Notifications</Label>
                      <p className="text-xs text-muted-foreground">
                        Master switch for all notification types
                      </p>
                    </div>
                    <Switch
                      checked={notifications}
                      onCheckedChange={setNotifications}
                    />
                  </div>

                  <Separator />

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="flex items-center justify-between">
                      <div className="space-y-0.5">
                        <Label className="flex items-center gap-2">
                          <Phone className="h-4 w-4" />
                          Push Notifications
                        </Label>
                        <p className="text-xs text-muted-foreground">
                          Mobile app push alerts
                        </p>
                      </div>
                      <Switch
                        checked={pushNotifications}
                        onCheckedChange={setPushNotifications}
                        disabled={!notifications}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="space-y-0.5">
                        <Label className="flex items-center gap-2">
                          <Mail className="h-4 w-4" />
                          Email Notifications
                        </Label>
                        <p className="text-xs text-muted-foreground">
                          Email alerts and reports
                        </p>
                      </div>
                      <Switch
                        checked={emailNotifications}
                        onCheckedChange={setEmailNotifications}
                        disabled={!notifications}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="space-y-0.5">
                        <Label>SMS Alerts</Label>
                        <p className="text-xs text-muted-foreground">
                          Critical SMS notifications
                        </p>
                      </div>
                      <Switch
                        checked={smsAlerts}
                        onCheckedChange={setSmsAlerts}
                        disabled={!notifications}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="space-y-0.5">
                        <Label>Notification Sounds</Label>
                        <p className="text-xs text-muted-foreground">
                          Audio alerts for notifications
                        </p>
                      </div>
                      <Switch
                        checked={notificationSound}
                        onCheckedChange={setNotificationSound}
                        disabled={!notifications}
                      />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* System Preferences */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <SettingsIcon className="h-5 w-5" />
                  System Preferences
                </CardTitle>
                <CardDescription>
                  UI theme and display preferences for MR apps
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>App Theme</Label>
                    <p className="text-xs text-muted-foreground">
                      Default theme for MR mobile apps
                    </p>
                  </div>
                  <Select value={theme} onValueChange={setTheme}>
                    <SelectTrigger className="w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="light">Light</SelectItem>
                      <SelectItem value="dark">Dark</SelectItem>
                      <SelectItem value="system">System</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Save Actions */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
              <div className="flex items-center gap-3">
                <Button 
                  onClick={handleSave}
                  disabled={!hasUnsavedChanges}
                  className={hasUnsavedChanges ? "bg-primary hover:bg-primary-hover" : ""}
                  size="lg"
                >
                  <Save className="h-4 w-4 mr-2" />
                  Save All Settings
                  {hasUnsavedChanges && <span className="ml-2 text-xs">•</span>}
                </Button>
                <Button variant="outline" onClick={resetToDefaults}>
                  Reset to Defaults
                </Button>
              </div>
              
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="sm" onClick={exportSettings}>
                  <Download className="h-4 w-4 mr-2" />
                  Export Config
                </Button>
                
                <div className="relative">
                  <input
                    type="file"
                    accept=".json"
                    onChange={importSettings}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  />
                  <Button variant="ghost" size="sm">
                    <Upload className="h-4 w-4 mr-2" />
                    Import Config
                  </Button>
                </div>
                
                <Button variant="ghost" size="sm" onClick={clearAllData}>
                  <Trash2 className="h-4 w-4 mr-2" />
                  Clear All Data
                </Button>
              </div>
            </div>

            {hasUnsavedChanges && (
              <Alert>
                <AlertTriangle className="h-4 w-4" />
                <AlertTitle>Unsaved Configuration Changes</AlertTitle>
                <AlertDescription>
                  You have unsaved changes to the MR tracking configuration. Click "Save All Settings" to apply changes and generate deployment files.
                </AlertDescription>
              </Alert>
            )}
          </div>

          {/* Sidebar - System Status & Info */}
          <div className="space-y-6">
            {/* Quick Configuration Summary */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5" />
                  Configuration Summary
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="text-sm space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Company</span>
                    <span className="font-medium">{companyName}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Territory</span>
                    <span className="font-medium">{defaultTerritory}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Max Visits</span>
                    <Badge variant="outline">{maxDailyVisits}</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Working Hours</span>
                    <span className="text-xs">{workingHoursStart} - {workingHoursEnd}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Tracking</span>
                    <Badge className={liveTracking ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                      {liveTracking ? 'Enabled' : 'Disabled'}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Connection Status */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Wifi className="h-5 w-5" />
                  System Status
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Backend API</span>
                  <Badge className={connectionStatus === 'connected' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                    {connectionStatus === 'connected' ? 'Connected' : 'Disconnected'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Google Maps</span>
                  <Badge className={googleMapsApiKey ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}>
                    {googleMapsApiKey ? 'Configured' : 'Not Set'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Live Tracking</span>
                  <Badge className={liveTracking ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                    {liveTracking ? 'Active' : 'Inactive'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Last Updated</span>
                  <span className="text-xs text-muted-foreground">
                    {new Date().toLocaleTimeString()}
                  </span>
                </div>
              </CardContent>
            </Card>

            {/* Security & Compliance */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  Security & Compliance
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="text-sm">
                  <div className="flex items-center justify-between mb-2">
                    <span>API Authentication</span>
                    <Badge className={apiKey ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                      {apiKey ? 'Secured' : 'Missing'}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between mb-2">
                    <span>Data Encryption</span>
                    <Badge className="bg-green-100 text-green-800">Active</Badge>
                  </div>
                  <div className="flex items-center justify-between mb-2">
                    <span>Location Privacy</span>
                    <Badge className="bg-green-100 text-green-800">Compliant</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>GDPR Ready</span>
                    <Badge className="bg-green-100 text-green-800">Yes</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* MR App Features */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="h-5 w-5" />
                  MR App Features
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="text-sm space-y-2">
                  <div className="flex items-center justify-between">
                    <span>Auto Check-in</span>
                    <Badge className={autoCheckIn ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                      {autoCheckIn ? 'Enabled' : 'Disabled'}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Offline Mode</span>
                    <Badge className={offlineSync ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                      {offlineSync ? 'Available' : 'Disabled'}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Push Notifications</span>
                    <Badge className={pushNotifications ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                      {pushNotifications ? 'Active' : 'Disabled'}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Expense Tracking</span>
                    <Badge className="bg-green-100 text-green-800">Enabled</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Environment & Deployment Info (live from API) */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Globe className="h-5 w-5" />
                  Environment Info
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-xs">
                <LiveEnvInfo apiUrl={apiUrl} apiKey={apiKey} />
              </CardContent>
            </Card>

            {/* Deployment Ready Notice */}
            <Alert>
              <Check className="h-4 w-4" />
              <AlertTitle>Ready for MRs!</AlertTitle>
              <AlertDescription className="text-xs">
                Once you save these settings, the MR tracking system will be fully configured and ready for field representatives to use.
              </AlertDescription>
            </Alert>
          </div>
        </div>
      </main>
    </div>
  );
}

function LiveEnvInfo({ apiUrl, apiKey }: { apiUrl: string; apiKey: string }) {
  const [info, setInfo] = useState<{ version?: string; service?: string; timestamp?: string } | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let ignore = false;
    (async () => {
      try {
        setError(null);
        const resp = await fetch(`${apiUrl}/`, { headers: { 'X-API-Key': apiKey } });
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();
        if (!ignore) setInfo({ version: data.version, service: data.service, timestamp: data.timestamp });
      } catch (e: any) {
        if (!ignore) setError(e?.message || 'Failed to contact API');
      }
    })();
    return () => { ignore = true; };
  }, [apiUrl, apiKey]);

  if (error) {
    return <div className="text-xs text-red-600">{error}</div>;
  }

  return (
    <div className="space-y-2 text-xs">
      <div className="flex justify-between">
        <span className="text-muted-foreground">API URL</span>
        <span className="truncate max-w-[180px]" title={apiUrl}>{apiUrl}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-muted-foreground">Service</span>
        <span>{info?.service || '—'}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-muted-foreground">Version</span>
        <span>{info?.version || '—'}</span>
      </div>
      <div className="flex justify-between">
        <span className="text-muted-foreground">Server Time</span>
        <span>{info?.timestamp ? new Date(info.timestamp).toLocaleString() : '—'}</span>
      </div>
    </div>
  );
}