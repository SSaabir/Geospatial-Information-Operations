import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Shield, LogIn } from 'lucide-react';

const ProtectedRoute = ({ children, requireAdmin = false }) => {
  const { isAuthenticated, isLoading, user } = useAuth();

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-50 flex items-center justify-center" style={{backgroundColor: '#F5EFFF'}}>
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-purple-200 border-t-purple-600 rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Checking authentication...</p>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-50 flex items-center justify-center" style={{backgroundColor: '#F5EFFF'}}>
        <div className="max-w-md w-full bg-white/80 backdrop-blur-md rounded-3xl shadow-2xl p-8 border border-purple-100 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl mb-6">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Authentication Required</h2>
          <p className="text-gray-600 mb-6">
            You need to be signed in to access this page. Please log in to continue.
          </p>
          <a
            href="/login"
            className="inline-flex items-center justify-center w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl hover:from-purple-700 hover:to-indigo-700 transition-all duration-200 space-x-2"
          >
            <LogIn className="w-4 h-4" />
            <span>Sign In</span>
          </a>
        </div>
      </div>
    );
  }

  // Check admin requirement
  if (requireAdmin && !user?.is_admin) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-50 flex items-center justify-center" style={{backgroundColor: '#F5EFFF'}}>
        <div className="max-w-md w-full bg-white/80 backdrop-blur-md rounded-3xl shadow-2xl p-8 border border-purple-100 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-red-500 to-pink-600 rounded-2xl mb-6">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Access Denied</h2>
          <p className="text-gray-600 mb-6">
            You don't have the required permissions to access this page. Admin privileges are required.
          </p>
          <a
            href="/dashboard"
            className="inline-flex items-center justify-center w-full px-6 py-3 bg-gradient-to-r from-gray-600 to-gray-700 text-white rounded-xl hover:from-gray-700 hover:to-gray-800 transition-all duration-200"
          >
            Go to Dashboard
          </a>
        </div>
      </div>
    );
  }

  // Render children if authenticated and authorized
  return children;
};

export default ProtectedRoute;