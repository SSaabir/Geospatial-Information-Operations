import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Cloud, MapPin, Bell, Settings, Search, Menu, LogOut, User } from 'lucide-react';

export default function Header() {
  const { user, logout, isAuthenticated } = useAuth();

  const handleLogout = () => {
    logout();
    window.location.href = '/';
  };

  return (
    <header className="bg-white/80 backdrop-blur-md border-b border-purple-100 sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Brand */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-xl flex items-center justify-center">
                <Cloud className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                  GeoWeather
                </h1>
                <p className="text-xs text-gray-500 -mt-1">Sri Lanka Weather Analytics</p>
              </div>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-8">
            <a
              href="/dashboard"
              className="text-gray-700 hover:text-purple-600 transition-colors font-medium"
            >
              Dashboard
            </a>
            <a
              href="/chat"
              className="text-gray-700 hover:text-purple-600 transition-colors font-medium"
            >
              Chat Assistant
            </a>
            {user?.role === 'admin' && (
              <a
                href="/admin/dashboard"
                className="text-gray-700 hover:text-purple-600 transition-colors font-medium"
              >
                Admin Panel
              </a>
            )}
            <a
              href="#"
              className="text-gray-700 hover:text-purple-600 transition-colors font-medium"
            >
              Analytics
            </a>
          </nav>

          {/* Right Side Actions */}
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                {/* Search */}
                <button className="hidden lg:flex items-center space-x-2 px-4 py-2 bg-gray-100 rounded-xl hover:bg-gray-200 transition-colors">
                  <Search className="w-4 h-4 text-gray-500" />
                  <span className="text-gray-500 text-sm">Search...</span>
                </button>

                {/* Notifications */}
                <button className="relative p-2 text-gray-600 hover:text-purple-600 transition-colors">
                  <Bell className="w-5 h-5" />
                  <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full"></div>
                </button>

                {/* Settings */}
                <button className="p-2 text-gray-600 hover:text-purple-600 transition-colors">
                  <Settings className="w-5 h-5" />
                </button>

                {/* User Menu */}
                <div className="flex items-center space-x-3">
                  <div className="hidden sm:block text-right">
                    <p className="text-sm font-medium text-gray-800">{user?.name}</p>
                    <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
                  </div>
                  <div className="relative group">
                    <button className="w-10 h-10 bg-gradient-to-r from-purple-400 to-indigo-500 rounded-xl flex items-center justify-center hover:from-purple-500 hover:to-indigo-600 transition-all duration-200">
                      <span className="text-white font-medium text-sm">
                        {user?.name?.split(' ').map(n => n[0]).join('') || 'U'}
                      </span>
                    </button>
                    
                    {/* Dropdown Menu */}
                    <div className="absolute right-0 mt-2 w-48 bg-white rounded-xl shadow-lg border border-gray-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
                      <div className="p-3 border-b border-gray-100">
                        <p className="font-medium text-gray-800">{user?.name}</p>
                        <p className="text-sm text-gray-500">{user?.email}</p>
                      </div>
                      <div className="py-2">
                        <a
                          href="#"
                          className="flex items-center space-x-3 px-4 py-2 text-gray-700 hover:bg-gray-50 transition-colors"
                        >
                          <User className="w-4 h-4" />
                          <span>Profile</span>
                        </a>
                        <a
                          href="#"
                          className="flex items-center space-x-3 px-4 py-2 text-gray-700 hover:bg-gray-50 transition-colors"
                        >
                          <Settings className="w-4 h-4" />
                          <span>Settings</span>
                        </a>
                        <hr className="my-2 border-gray-100" />
                        <button
                          onClick={handleLogout}
                          className="flex items-center space-x-3 w-full px-4 py-2 text-gray-700 hover:bg-red-50 hover:text-red-600 transition-colors"
                        >
                          <LogOut className="w-4 h-4" />
                          <span>Sign Out</span>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex items-center space-x-3">
                <a
                  href="/login"
                  className="px-4 py-2 text-purple-600 hover:text-purple-700 font-medium transition-colors"
                >
                  Sign In
                </a>
                <a
                  href="/login"
                  className="px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl hover:from-purple-700 hover:to-indigo-700 transition-all duration-200"
                >
                  Get Started
                </a>
              </div>
            )}

            {/* Mobile Menu Button */}
            <button className="md:hidden p-2 text-gray-600 hover:text-purple-600 transition-colors">
              <Menu className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className="md:hidden border-t border-gray-100 py-4">
          <nav className="flex flex-col space-y-4">
            <a
              href="/dashboard"
              className="text-gray-700 hover:text-purple-600 transition-colors font-medium"
            >
              Dashboard
            </a>
            <a
              href="/chat"
              className="text-gray-700 hover:text-purple-600 transition-colors font-medium"
            >
              Chat Assistant
            </a>
            {user?.role === 'admin' && (
              <a
                href="/admin/dashboard"
                className="text-gray-700 hover:text-purple-600 transition-colors font-medium"
              >
                Admin Panel
              </a>
            )}
            <a
              href="#"
              className="text-gray-700 hover:text-purple-600 transition-colors font-medium"
            >
              Analytics
            </a>
          </nav>
        </div>
      </div>
    </header>
  );
}