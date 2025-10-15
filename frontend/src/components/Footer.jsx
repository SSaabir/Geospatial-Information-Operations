import React from 'react';
import { Cloud, MapPin, Mail, Phone, Globe, Github, Twitter, Linkedin, Heart, ExternalLink } from 'lucide-react';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-white/90 backdrop-blur-md border-t border-orange-100 mt-auto">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Brand Section */}
          <div className="lg:col-span-1">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-r from-orange-600 to-green-800 rounded-xl flex items-center justify-center">
                <Cloud className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-bold bg-gradient-to-r from-orange-600 to-green-800 bg-clip-text text-transparent">
                  GeoWeather
                </h3>
                <p className="text-xs text-gray-500 -mt-1">Sri Lanka Weather Analytics</p>
              </div>
            </div>
            <p className="text-gray-600 text-sm mb-4 leading-relaxed">
              Advanced geospatial weather intelligence platform providing comprehensive climate analytics and forecasting for Sri Lanka.
            </p>
            <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
              <MapPin className="w-4 h-4" />
              <span>Colombo, Sri Lanka</span>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <Globe className="w-4 h-4" />
              <span>Serving nationwide coverage</span>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="font-semibold text-gray-800 mb-4">Platform</h4>
            <ul className="space-y-3">
              <li>
                <a href="/dashboard" className="text-gray-600 hover:text-orange-600 transition-colors text-sm flex items-center space-x-2">
                  <span>Dashboard</span>
                </a>
              </li>
              <li>
                <a href="/chat" className="text-gray-600 hover:text-orange-600 transition-colors text-sm flex items-center space-x-2">
                  <span>AI Assistant</span>
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-600 hover:text-orange-600 transition-colors text-sm flex items-center space-x-2">
                  <span>Weather Analytics</span>
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-600 hover:text-orange-600 transition-colors text-sm flex items-center space-x-2">
                  <span>Climate Reports</span>
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-600 hover:text-orange-600 transition-colors text-sm flex items-center space-x-2">
                  <span>API Access</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className="font-semibold text-gray-800 mb-4">Resources</h4>
            <ul className="space-y-3">
              <li>
                <a href="#" className="text-gray-600 hover:text-orange-600 transition-colors text-sm">
                  Documentation
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-600 hover:text-orange-600 transition-colors text-sm">
                  Weather Data Sources
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-600 hover:text-orange-600 transition-colors text-sm">
                  Research Papers
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-600 hover:text-orange-600 transition-colors text-sm">
                  Climate Models
                </a>
              </li>
              <li>
                <a href="#" className="text-gray-600 hover:text-orange-600 transition-colors text-sm">
                  Support Center
                </a>
              </li>
            </ul>
          </div>

          {/* Contact & Social */}
          <div>
            <h4 className="font-semibold text-gray-800 mb-4">Connect</h4>
            <div className="space-y-3 mb-6">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <Mail className="w-4 h-4" />
                <span>contact@geoweather.lk</span>
              </div>
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <Phone className="w-4 h-4" />
                <span>+94 11 234 5678</span>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <a
                href="#"
                className="w-8 h-8 bg-gray-100 hover:bg-orange-100 rounded-lg flex items-center justify-center transition-colors group"
              >
                <Github className="w-4 h-4 text-gray-600 group-hover:text-orange-600" />
              </a>
              <a
                href="#"
                className="w-8 h-8 bg-gray-100 hover:bg-orange-100 rounded-lg flex items-center justify-center transition-colors group"
              >
                <Twitter className="w-4 h-4 text-gray-600 group-hover:text-orange-600" />
              </a>
              <a
                href="#"
                className="w-8 h-8 bg-gray-100 hover:bg-orange-100 rounded-lg flex items-center justify-center transition-colors group"
              >
                <Linkedin className="w-4 h-4 text-gray-600 group-hover:text-orange-600" />
              </a>
            </div>
          </div>
        </div>

        {/* Divider */}
        <div className="border-t border-gray-200 mt-8 pt-8">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div className="flex items-center space-x-4 mb-4 md:mb-0">
              <p className="text-sm text-gray-600">
                © {currentYear} GeoWeather Platform. All rights reserved.
              </p>
            </div>
            
            <div className="flex items-center space-x-6">
              <a href="#" className="text-sm text-gray-600 hover:text-orange-600 transition-colors">
                Privacy Policy
              </a>
              <a href="#" className="text-sm text-gray-600 hover:text-orange-600 transition-colors">
                Terms of Service
              </a>
              <a href="#" className="text-sm text-gray-600 hover:text-orange-600 transition-colors">
                Data Usage Policy
              </a>
            </div>
          </div>
          
          <div className="mt-4 pt-4 border-t border-gray-100">
            <div className="flex items-center justify-between text-xs text-gray-500">
              <p>
                Powered by advanced meteorological data processing and machine learning algorithms
              </p>
              <div className="flex items-center space-x-1">
                <span>Made with</span>
                <Heart className="w-3 h-3 text-red-400 fill-current" />
                <span>for Sri Lanka</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}