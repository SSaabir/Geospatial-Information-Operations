import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Eye, EyeOff, Mail, Lock, User, ArrowRight, Sparkles, Shield } from 'lucide-react';

export default function Login() {
  const [isLogin, setIsLogin] = useState(true);
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    name: ''
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    if (isLogin) {
      // LOGIN
      try {
        const res = await fetch('http://localhost:8000/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: formData.email, password: formData.password })
        });
        const data = await res.json();
        setIsLoading(false);

        if (!res.ok) {
          setError(data.detail || 'Login failed');
        } else {
          // Login successful
          navigate('/home');
        }
      } catch (err) {
        setIsLoading(false);
        setError(err.message);
      }
    } else {
      // SIGNUP
      if (formData.password !== formData.confirmPassword) {
        setError('Passwords do not match');
        setIsLoading(false);
        return;
      }

      try {
        const res = await fetch('http://localhost:8000/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: formData.email, // username can be email
            email: formData.email,
            password: formData.password,
            confirm_password: formData.confirmPassword,
            full_name: formData.name,
            is_active: true
          })
        });
        const data = await res.json();
        setIsLoading(false);

        if (!res.ok) {
          setError(data.detail || 'Signup failed');
        } else {
          // Signup successful → switch to login
          setIsLogin(true);
          setFormData({ ...formData, password: '', confirmPassword: '' });
          setError('Signup successful! Please login.');
        }
      } catch (err) {
        setIsLoading(false);
        setError(err.message);
      }
    }
  };

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-50 flex items-center justify-center p-4" style={{backgroundColor: '#F5EFFF'}}>
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-indigo-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-10 animate-pulse delay-500"></div>
      </div>

      <div className="relative w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl mb-4 shadow-lg">
            <Sparkles className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
            Geospatial Analytics
          </h1>
          <p className="text-gray-600 mt-2">Welcome back to your weather dashboard</p>
        </div>

        <div className="bg-white/80 backdrop-blur-md rounded-3xl shadow-2xl p-8 border border-purple-100">
          <div className="flex bg-purple-50 rounded-2xl p-1 mb-6">
            <button
              onClick={() => {setIsLogin(true); setError('');}}
              className={`flex-1 py-2 px-4 rounded-xl font-medium transition-all duration-200 ${isLogin ? 'bg-white text-purple-600 shadow-sm' : 'text-gray-500 hover:text-purple-600'}`}
            >
              Login
            </button>
            <button
              onClick={() => {setIsLogin(false); setError('');}}
              className={`flex-1 py-2 px-4 rounded-xl font-medium transition-all duration-200 ${!isLogin ? 'bg-white text-purple-600 shadow-sm' : 'text-gray-500 hover:text-purple-600'}`}
            >
              Sign Up
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {!isLogin && (
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Full Name</label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    className="w-full pl-10 pr-4 py-3 border border-purple-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 bg-white/50"
                    placeholder="Enter your full name"
                    required={!isLogin}
                  />
                </div>
              </div>
            )}

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">Email Address</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className="w-full pl-10 pr-4 py-3 border border-purple-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 bg-white/50"
                  placeholder="Enter your email"
                  required
                />
              </div>
            </div>

            {!isLogin && (
              <div className="space-y-2">
                <label className="text-sm font-medium text-gray-700">Confirm Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type={showPassword ? "text" : "password"}
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleInputChange}
                    className="w-full pl-10 pr-12 py-3 border border-purple-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 bg-white/50"
                    placeholder="Confirm your password"
                    required={!isLogin}
                  />
                </div>
              </div>
            )}

            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type={showPassword ? "text" : "password"}
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  className="w-full pl-10 pr-12 py-3 border border-purple-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 bg-white/50"
                  placeholder="Enter your password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-purple-600 transition-colors"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-xl p-3">
                <p className="text-red-600 text-sm">{error}</p>
              </div>
            )}

            <div className="bg-purple-50 border border-purple-200 rounded-xl p-3">
              <div className="flex items-center space-x-2 mb-2">
                <Shield className="w-4 h-4 text-purple-600" />
                <p className="text-purple-600 text-sm font-medium">Demo Mode</p>
              </div>
              <p className="text-purple-600 text-xs">Use any email/password combination to login</p>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-3 px-4 rounded-xl font-medium hover:from-purple-700 hover:to-indigo-700 focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed group"
            >
              <div className="flex items-center justify-center space-x-2">
                {isLoading ? (
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                ) : (
                  <>
                    <span>{isLogin ? 'Sign In' : 'Create Account'}</span>
                    <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </div>
            </button>
          </form>

          <div className="mt-6 text-center space-y-2">
            {isLogin && (
              <Link to="/forgot-password" className="text-sm text-purple-600 hover:text-purple-800 transition-colors">
                Forgot your password?
              </Link>
            )}
            <div className="border-t border-purple-100 pt-4">
              <Link to="/home" className="text-sm text-gray-500 hover:text-purple-600 transition-colors">
                ← Back to Homepage
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
