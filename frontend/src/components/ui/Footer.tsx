'use client';

import React from 'react';
import Link from 'next/link';

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">MR</span>
              </div>
              <h3 className="text-lg font-semibold text-gray-900">MR Tracking Pro</h3>
            </div>
            <p className="text-gray-600 text-sm leading-relaxed max-w-md">
              Professional route analytics and visit tracking system for medical representatives. 
              Optimize your field work with intelligent route blueprints and comprehensive performance insights.
            </p>
            <div className="mt-4 flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm text-gray-500">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span>System Online</span>
              </div>
              <div className="text-sm text-gray-500">
                <span>Last updated: {new Date().toLocaleDateString()}</span>
              </div>
            </div>
          </div>

          {/* Features Section */}
          <div>
            <h4 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4">Features</h4>
            <ul className="space-y-2">
              <li>
                <span className="text-sm text-gray-600 flex items-center">
                  <span className="mr-2">📍</span>
                  Route Blueprints
                </span>
              </li>
              <li>
                <span className="text-sm text-gray-600 flex items-center">
                  <span className="mr-2">📊</span>
                  Performance Analytics
                </span>
              </li>
              <li>
                <span className="text-sm text-gray-600 flex items-center">
                  <span className="mr-2">🗺️</span>
                  Interactive Maps
                </span>
              </li>
              <li>
                <span className="text-sm text-gray-600 flex items-center">
                  <span className="mr-2">⚡</span>
                  Real-time Updates
                </span>
              </li>
              <li>
                <span className="text-sm text-gray-600 flex items-center">
                  <span className="mr-2">📱</span>
                  Mobile Optimized
                </span>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4">Links</h4>
            <ul className="space-y-2">
              <li>
                <Link href="/" className="text-sm text-gray-600 hover:text-blue-600 transition-colors">
                  Dashboard
                </Link>
              </li>
              <li>
                <Link href="/about" className="text-sm text-gray-600 hover:text-blue-600 transition-colors">
                  About Platform
                </Link>
              </li>
              <li>
                <Link href="/contact" className="text-sm text-gray-600 hover:text-blue-600 transition-colors">
                  Contact Support
                </Link>
              </li>
              <li>
                <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" 
                   className="text-sm text-gray-600 hover:text-blue-600 transition-colors">
                  API Documentation
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="mt-8 pt-6 border-t border-gray-200">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            
            {/* Copyright */}
            <div className="text-sm text-gray-500">
              © {currentYear} MR Tracking Pro. Built with modern web technologies.
            </div>

            <div className="flex items-center space-x-4 text-xs text-gray-400">
              <span className="flex items-center space-x-1">
                <span>React</span>
              </span>
              <span className="flex items-center space-x-1">
                <span>TypeScript</span>
              </span>
              <span className="flex items-center space-x-1">
                <span>Tailwind</span>
              </span>
              <span className="flex items-center space-x-1">
                <span>FastAPI</span>
              </span>
              <span className="flex items-center space-x-1">
                <span>Leaflet</span>
              </span>
            </div>

            {/* Status */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <span className="text-xs text-gray-500">API Connected</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-xs text-gray-500">v2.0.0</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Removed extra info bar for a cleaner SaaS look */}
    </footer>
  );
};

export default Footer;
