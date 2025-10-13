import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Cloud, MapPin, Bell, Settings, Search, Menu, LogOut, User, Shield, Brain, ChevronDown, Home, BarChart3, Bot, X } from 'lucide-react';
import NotificationPanel from './NotificationPanel';

export default function Header() {
  const { user, logout, isAuthenticated } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  const handleLogout = async () => {
    setIsDropdownOpen(false);
    try {
      await logout();
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      // Force redirect to login page
      window.location.href = '/login';
    }
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  // Filter navigation items based on user role
  const allNavigationItems = [
    { name: 'Dashboard', href: '/dashboard', icon: BarChart3, adminOnly: false },
    { name: 'Workflow', href: '/workflow', icon: Bot, adminOnly: false },
    { name: 'Chat Assistant', href: '/chat', icon: Bot, adminOnly: false },
  ];

  // Only show non-admin items, or all items if user is admin viewing as regular user
  const navigationItems = allNavigationItems.filter(item => !item.adminOnly || user?.is_admin);

  return (
    <header className="bg-white/95 backdrop-blur-lg border-b border-purple-100 sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Brand */}
          <div className="flex items-center space-x-4">
            <a href="/" className="flex items-center space-x-3 group">
              <div className="w-10 h-10 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-xl flex items-center justify-center group-hover:scale-105 transition-transform duration-200">
                <Cloud className="w-5 h-5 text-white" />
              </div>
              <div className="hidden sm:block">
                <h1 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                  GeoWeather AI
                </h1>
                <p className="text-xs text-gray-500 -mt-1">Climate Intelligence Platform</p>
              </div>
            </a>
          </div>

          {/* Navigation Links */}
          <nav className="hidden lg:flex items-center space-x-1">
            {navigationItems.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className="flex items-center space-x-2 px-4 py-2 rounded-lg text-gray-700 hover:text-purple-600 hover:bg-purple-50 transition-all duration-200 group"
              >
                <item.icon className="w-4 h-4 group-hover:scale-110 transition-transform" />
                <span className="font-medium">{item.name}</span>
              </Link>
            ))}
            {user?.is_admin && (
              <a
                href="/admin/dashboard"
                className="flex items-center space-x-2 px-4 py-2 rounded-lg text-gray-700 hover:text-purple-600 hover:bg-purple-50 transition-all duration-200 ml-2 border-l border-gray-200 pl-6"
              >
                <Settings className="w-4 h-4" />
                <span className="font-medium">Admin</span>
              </a>
            )}
          </nav>

          {/* Right Side Actions */}
          <div className="flex items-center space-x-3">
            {isAuthenticated ? (
              <>
                {/* Search */}
                <button className="hidden xl:flex items-center space-x-2 px-4 py-2 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors text-gray-500 hover:text-gray-700">
                  <Search className="w-4 h-4" />
                  <span className="text-sm">Search...</span>
                </button>

                {/* Notifications */}
                <NotificationPanel />

                {/* User Menu */}
                <div className="relative">
                  <button 
                    onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                    className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="hidden sm:block text-right">
                      <p className="text-sm font-medium text-gray-800">{user?.name}</p>
                      <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
                    </div>
                    <div className="w-10 h-10 bg-gradient-to-r from-purple-400 to-indigo-500 rounded-lg flex items-center justify-center">
                      <span className="text-white font-medium text-sm">
                        {user?.name?.split(' ').map(n => n[0]).join('') || 'U'}
                      </span>
                    </div>
                    <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform duration-200 ${isDropdownOpen ? 'rotate-180' : ''}`} />
                  </button>
                  
                  {/* Dropdown Menu */}
                  {isDropdownOpen && (
                    <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-lg border border-gray-200 z-50">
                      <div className="p-4 border-b border-gray-100">
                        <p className="font-medium text-gray-800">{user?.name}</p>
                        <p className="text-sm text-gray-500">{user?.email}</p>
                      </div>
                      <div className="py-2">
                        <Link
                          to="/settings"
                          className="flex items-center space-x-3 px-4 py-3 text-gray-700 hover:bg-gray-50 transition-colors"
                          onClick={() => setIsDropdownOpen(false)}
                        >
                          <User className="w-4 h-4" />
                          <span>Profile Settings</span>
                        </Link>
                        <Link
                          to="/settings"
                          className="flex items-center space-x-3 px-4 py-3 text-gray-700 hover:bg-gray-50 transition-colors"
                          onClick={() => setIsDropdownOpen(false)}
                        >
                          <Settings className="w-4 h-4" />
                          <span>Settings</span>
                        </Link>
                        <hr className="my-2 border-gray-100" />
                        <button
                          onClick={handleLogout}
                          className="flex items-center space-x-3 w-full px-4 py-3 text-gray-700 hover:bg-red-50 hover:text-red-600 transition-colors"
                        >
                          <LogOut className="w-4 h-4" />
                          <span>Sign Out</span>
                        </button>
                      </div>
                    </div>
                  )}
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
                  className="px-6 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:from-purple-700 hover:to-indigo-700 transition-all duration-200 font-medium shadow-md hover:shadow-lg"
                >
                  Get Started
                </a>
              </div>
            )}

            {/* Mobile Menu Button */}
            <button 
              onClick={toggleMobileMenu}
              className="lg:hidden p-2 text-gray-600 hover:text-purple-600 hover:bg-purple-50 rounded-lg transition-all duration-200"
            >
              {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMobileMenuOpen && (
          <div className="lg:hidden border-t border-gray-100 py-4 bg-white rounded-b-lg shadow-lg">
            <nav className="flex flex-col space-y-2">
              {navigationItems.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className="flex items-center space-x-3 px-4 py-3 text-gray-700 hover:text-purple-600 hover:bg-purple-50 transition-all duration-200 rounded-lg mx-2"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  <item.icon className="w-5 h-5" />
                  <span className="font-medium">{item.name}</span>
                </Link>
              ))}
              {user?.is_admin && (
                <a
                  href="/admin/dashboard"
                  className="flex items-center space-x-3 px-4 py-3 text-gray-700 hover:text-purple-600 hover:bg-purple-50 transition-all duration-200 rounded-lg mx-2 mt-2 pt-4 border-t border-gray-100"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  <Settings className="w-5 h-5" />
                  <span className="font-medium">Admin Panel</span>
                </a>
              )}
            </nav>
          </div>
        )}
      </div>
    </header>
  );
}