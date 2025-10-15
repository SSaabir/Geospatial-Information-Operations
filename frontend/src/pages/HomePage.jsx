import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar, RadialBarChart, RadialBar, Legend } from 'recharts';
import { Menu, X, TrendingUp, Cloud, MessageSquare, FileText, Home, Info, Mail, HelpCircle, FileCheck, LogIn, LogOut, ChevronDown, Sun, Thermometer, Droplets, Wind, User, Zap, Globe, BarChart3, Clock, ArrowRight, CheckCircle, Star } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const ClimateHomepage = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [currentSlide, setCurrentSlide] = useState(0);
  const { user, logout, isAuthenticated } = useAuth();

  // Sample climate data based on your dataset structure
  const temperatureData = [
    { month: 'Jan', tempmax: 30.0, tempmin: 23.2, year: 1997 },
    { month: 'Feb', tempmax: 31.2, tempmin: 24.1, year: 1997 },
    { month: 'Mar', tempmax: 32.5, tempmin: 25.3, year: 1997 },
    { month: 'Apr', tempmax: 33.1, tempmin: 26.2, year: 1997 },
    { month: 'May', tempmax: 32.8, tempmin: 25.9, year: 1997 },
    { month: 'Jun', tempmax: 31.5, tempmin: 24.8, year: 1997 },
    { month: 'Jul', tempmax: 30.9, tempmin: 24.2, year: 1997 },
    { month: 'Aug', tempmax: 31.3, tempmin: 24.6, year: 1997 },
    { month: 'Sep', tempmax: 31.8, tempmin: 25.1, year: 1997 },
    { month: 'Oct', tempmax: 31.4, tempmin: 24.9, year: 1997 },
    { month: 'Nov', tempmax: 30.7, tempmin: 24.3, year: 1997 },
    { month: 'Dec', tempmax: 30.2, tempmin: 23.8, year: 1997 }
  ];

  const humidityData = [
    { month: 'Jan', humidity: 75.4 },
    { month: 'Feb', humidity: 72.7 },
    { month: 'Mar', humidity: 76.0 },
    { month: 'Apr', humidity: 74.0 },
    { month: 'May', humidity: 78.5 },
    { month: 'Jun', humidity: 82.1 },
    { month: 'Jul', humidity: 81.3 },
    { month: 'Aug', humidity: 79.8 },
    { month: 'Sep', humidity: 77.2 },
    { month: 'Oct', humidity: 76.9 },
    { month: 'Nov', humidity: 78.3 },
    { month: 'Dec', humidity: 76.1 }
  ];

  const weatherConditions = [
    { condition: 'Clear', count: 45, color: '#F4991A' },
    { condition: 'Partly Cloudy', count: 38, color: '#F2EAD3' },
    { condition: 'Cloudy', count: 22, color: '#344F1F' },
    { condition: 'Rainy', count: 15, color: '#F9F5F0' }
  ];

  const heroSlides = [
    {
      title: "Climate Data at Your Fingertips",
      subtitle: "Explore comprehensive weather patterns and climate trends for Colombo, Sri Lanka",
      icon: <Cloud className="w-16 h-16" />
    },
    {
      title: "Advanced Analytics & Predictions",
      subtitle: "Harness AI-powered insights to understand climate patterns and forecast future trends",
      icon: <TrendingUp className="w-16 h-16" />
    },
    {
      title: "Interactive Data Exploration",
      subtitle: "Dive deep into historical weather data with intuitive visualizations and reports",
      icon: <FileText className="w-16 h-16" />
    }
  ];

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % heroSlides.length);
    }, 4000);
    return () => clearInterval(timer);
  }, []);

  const menuItems = [
    { name: 'Home', icon: Home, href: '/home' },
    { name: 'About Us', icon: Info, href: '/about' },
    { name: 'Contact Us', icon: Mail, href: '/contact' },
    { name: 'Terms', icon: FileCheck, href: '/terms' },
    { name: 'FAQ', icon: HelpCircle, href: '/faq' }
  ];

  return (
    <div className="min-h-screen" style={{backgroundColor: '#F9F5F0'}}>

      {/* Hero Section - Modern Design */}
      <section className="relative overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-5">
          <div className="absolute inset-0" style={{
            backgroundImage: `radial-gradient(circle at 20px 20px, #344F1F 2px, transparent 0)`,
            backgroundSize: '40px 40px'
          }}></div>
        </div>

        <div className="max-w-7xl mx-auto px-4 py-24 relative">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Column - Content */}
            <div className="space-y-8">
              <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-full border-2" style={{borderColor: '#F4991A', backgroundColor: 'white'}}>
                <Zap className="w-4 h-4" style={{color: '#F4991A'}} />
                <span className="text-sm font-semibold" style={{color: '#344F1F'}}>AI-Powered Climate Intelligence</span>
              </div>

              <h1 className="text-6xl md:text-7xl font-bold leading-tight">
                <span className="bg-gradient-to-r from-orange-600 to-green-800 bg-clip-text text-transparent">
                  Climate Data
                </span>
                <br />
                <span className="text-gray-800">Simplified</span>
              </h1>

              <p className="text-xl text-gray-600 leading-relaxed max-w-xl">
                Access 25+ years of climate data for Colombo, Sri Lanka. Get AI-powered insights, predictions, and interactive visualizations at your fingertips.
              </p>

              {/* Features List */}
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-5 h-5" style={{color: '#F4991A'}} />
                  <span className="text-gray-700 font-medium">Real-time Data</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-5 h-5" style={{color: '#F4991A'}} />
                  <span className="text-gray-700 font-medium">AI Predictions</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-5 h-5" style={{color: '#F4991A'}} />
                  <span className="text-gray-700 font-medium">25+ Years History</span>
                </div>
                <div className="flex items-center space-x-2">
                  <CheckCircle className="w-5 h-5" style={{color: '#F4991A'}} />
                  <span className="text-gray-700 font-medium">Interactive Charts</span>
                </div>
              </div>

              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row gap-4 pt-4">
                <Link 
                  to="/chat" 
                  className="group px-8 py-4 rounded-xl text-white font-semibold text-lg transition-all duration-300 hover:scale-105 shadow-lg hover:shadow-2xl flex items-center justify-center space-x-2" 
                  style={{backgroundColor: '#F4991A'}}
                >
                  <MessageSquare className="w-5 h-5" />
                  <span>Start Chatting</span>
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Link>
                <Link 
                  to="/weather-predictor" 
                  className="px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-300 hover:scale-105 shadow-lg hover:shadow-xl border-2 flex items-center justify-center space-x-2" 
                  style={{borderColor: '#344F1F', color: '#344F1F', backgroundColor: 'white'}}
                >
                  <BarChart3 className="w-5 h-5" />
                  <span>Try Predictor</span>
                </Link>
              </div>
            </div>

            {/* Right Column - Visual */}
            <div className="relative">
              <div className="relative rounded-3xl p-8 shadow-2xl" style={{backgroundColor: 'white', border: '2px solid #F2EAD3'}}>
                {/* Mini Dashboard Preview */}
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xl font-bold text-gray-800">Live Climate Data</h3>
                    <div className="flex items-center space-x-2 px-3 py-1 rounded-full" style={{backgroundColor: '#F9F5F0'}}>
                      <div className="w-2 h-2 rounded-full animate-pulse" style={{backgroundColor: '#F4991A'}}></div>
                      <span className="text-sm font-medium" style={{color: '#344F1F'}}>Live</span>
                    </div>
                  </div>

                  {/* Stats Grid */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 rounded-xl" style={{backgroundColor: '#F9F5F0'}}>
                      <div className="flex items-center space-x-2 mb-2">
                        <Thermometer className="w-5 h-5" style={{color: '#F4991A'}} />
                        <span className="text-sm text-gray-600">Temperature</span>
                      </div>
                      <p className="text-3xl font-bold text-gray-800">30.5°C</p>
                      <p className="text-xs text-gray-500 mt-1">↑ 2.3° from avg</p>
                    </div>
                    <div className="p-4 rounded-xl" style={{backgroundColor: '#F2EAD3'}}>
                      <div className="flex items-center space-x-2 mb-2">
                        <Droplets className="w-5 h-5" style={{color: '#344F1F'}} />
                        <span className="text-sm text-gray-600">Humidity</span>
                      </div>
                      <p className="text-3xl font-bold text-gray-800">76%</p>
                      <p className="text-xs text-gray-500 mt-1">Normal range</p>
                    </div>
                  </div>

                  {/* Mini Chart */}
                  <div className="pt-4" style={{borderTop: '1px solid #F2EAD3'}}>
                    <ResponsiveContainer width="100%" height={150}>
                      <AreaChart data={temperatureData.slice(0, 6)}>
                        <defs>
                          <linearGradient id="tempGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#F4991A" stopOpacity={0.3}/>
                            <stop offset="100%" stopColor="#F4991A" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <Area 
                          type="monotone" 
                          dataKey="tempmax" 
                          stroke="#F4991A" 
                          fill="url(#tempGradient)"
                          strokeWidth={2}
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Floating Elements */}
                <div className="absolute -top-4 -right-4 w-24 h-24 rounded-2xl shadow-xl flex items-center justify-center animate-bounce" style={{backgroundColor: '#F4991A'}}>
                  <Cloud className="w-12 h-12 text-white" />
                </div>
                <div className="absolute -bottom-4 -left-4 w-20 h-20 rounded-xl shadow-lg flex items-center justify-center" style={{backgroundColor: '#344F1F'}}>
                  <TrendingUp className="w-10 h-10 text-white" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section - Redesigned */}
      <section className="py-20 px-4" style={{backgroundColor: 'white'}}>
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4 text-gray-800">Trusted Climate Intelligence</h2>
            <p className="text-xl text-gray-600">Powering data-driven decisions with precision</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="group relative overflow-hidden p-8 rounded-2xl transition-all duration-300 hover:scale-105 hover:shadow-2xl" style={{backgroundColor: '#F9F5F0'}}>
              <div className="absolute top-0 right-0 w-32 h-32 rounded-full -mr-16 -mt-16 opacity-20" style={{backgroundColor: '#F4991A'}}></div>
              <div className="relative">
                <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl mb-4 group-hover:scale-110 transition-transform" style={{backgroundColor: '#F4991A'}}>
                  <BarChart3 className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-4xl font-bold text-gray-800 mb-2">9,125+</h3>
                <p className="text-gray-600 font-medium">Data Points</p>
                <p className="text-sm text-gray-500 mt-2">Collected daily</p>
              </div>
            </div>

            <div className="group relative overflow-hidden p-8 rounded-2xl transition-all duration-300 hover:scale-105 hover:shadow-2xl" style={{backgroundColor: '#F2EAD3'}}>
              <div className="absolute top-0 right-0 w-32 h-32 rounded-full -mr-16 -mt-16 opacity-20" style={{backgroundColor: '#344F1F'}}></div>
              <div className="relative">
                <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl mb-4 group-hover:scale-110 transition-transform" style={{backgroundColor: '#344F1F'}}>
                  <Clock className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-4xl font-bold text-gray-800 mb-2">25+</h3>
                <p className="text-gray-600 font-medium">Years of Data</p>
                <p className="text-sm text-gray-500 mt-2">1997 - Present</p>
              </div>
            </div>

            <div className="group relative overflow-hidden p-8 rounded-2xl transition-all duration-300 hover:scale-105 hover:shadow-2xl" style={{backgroundColor: '#F2EAD3'}}>
              <div className="absolute top-0 right-0 w-32 h-32 rounded-full -mr-16 -mt-16 opacity-20" style={{backgroundColor: '#F4991A'}}></div>
              <div className="relative">
                <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl mb-4 group-hover:scale-110 transition-transform" style={{backgroundColor: '#F4991A'}}>
                  <Globe className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-4xl font-bold text-gray-800 mb-2">98.9%</h3>
                <p className="text-gray-600 font-medium">Accuracy Rate</p>
                <p className="text-sm text-gray-500 mt-2">AI predictions</p>
              </div>
            </div>

            <div className="group relative overflow-hidden p-8 rounded-2xl transition-all duration-300 hover:scale-105 hover:shadow-2xl" style={{backgroundColor: '#344F1F'}}>
              <div className="absolute top-0 right-0 w-32 h-32 rounded-full -mr-16 -mt-16 opacity-20" style={{backgroundColor: 'white'}}></div>
              <div className="relative">
                <div className="inline-flex items-center justify-center w-14 h-14 rounded-xl mb-4 group-hover:scale-110 transition-transform" style={{backgroundColor: 'white'}}>
                  <Star className="w-7 h-7" style={{color: '#F4991A'}} />
                </div>
                <h3 className="text-4xl font-bold text-white mb-2">4.9/5</h3>
                <p className="text-green-100 font-medium">User Rating</p>
                <p className="text-sm text-green-200 mt-2">From 2,400+ users</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Data Visualizations */}
      <section className="py-20 px-4" style={{backgroundColor: '#F9F5F0'}}>
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-6 text-gray-800">Climate Trends & Analytics</h2>
            <p className="text-xl text-gray-600">Real-time insights from decades of weather data</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
            {/* Temperature Chart */}
            <div className="bg-white rounded-2xl p-6 shadow-xl hover:shadow-2xl transition-shadow border" style={{borderColor: '#F2EAD3'}}>
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-gray-800">Temperature Trends</h3>
                <div className="flex items-center space-x-4 text-sm">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 rounded-full" style={{backgroundColor: '#F4991A'}}></div>
                    <span>Max Temp</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 rounded-full" style={{backgroundColor: '#344F1F'}}></div>
                    <span>Min Temp</span>
                  </div>
                </div>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={temperatureData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F2EAD3" />
                  <XAxis dataKey="month" stroke="#6B7280" />
                  <YAxis stroke="#6B7280" />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #F2EAD3',
                      borderRadius: '8px'
                    }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="tempmax" 
                    stroke="#F4991A" 
                    strokeWidth={3}
                    dot={{ fill: '#F4991A', strokeWidth: 2, r: 4 }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="tempmin" 
                    stroke="#344F1F" 
                    strokeWidth={3}
                    dot={{ fill: '#344F1F', strokeWidth: 2, r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Humidity Chart */}
            <div className="bg-white rounded-2xl p-6 shadow-xl hover:shadow-2xl transition-shadow border" style={{borderColor: '#F2EAD3'}}>
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-gray-800">Humidity Levels</h3>
                <span className="text-sm text-gray-500">Monthly Average (%)</span>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={humidityData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#F2EAD3" />
                  <XAxis dataKey="month" stroke="#6B7280" />
                  <YAxis stroke="#6B7280" />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #F2EAD3',
                      borderRadius: '8px'
                    }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="humidity" 
                    stroke="#344F1F" 
                    fill="url(#humidityGradient)"
                    strokeWidth={2}
                  />
                  <defs>
                    <linearGradient id="humidityGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#344F1F" stopOpacity={0.8}/>
                      <stop offset="100%" stopColor="#344F1F" stopOpacity={0.1}/>
                    </linearGradient>
                  </defs>
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Weather Conditions Chart */}
          <div className="bg-white rounded-2xl p-6 shadow-xl hover:shadow-2xl transition-shadow border" style={{borderColor: '#F2EAD3'}}>
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-gray-800">Weather Conditions Distribution</h3>
              <span className="text-sm text-gray-500">Days per Year</span>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={weatherConditions}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F2EAD3" />
                <XAxis dataKey="condition" stroke="#6B7280" />
                <YAxis stroke="#6B7280" />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #F2EAD3',
                    borderRadius: '8px'
                  }}
                />
                <Bar 
                  dataKey="count" 
                  radius={[4, 4, 0, 0]}
                  fill="#F4991A"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      {/* Call to Action Section - Redesigned */}
      <section className="relative py-24 px-4 overflow-hidden" style={{backgroundColor: '#344F1F'}}>
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0" style={{
            backgroundImage: `radial-gradient(circle at 30px 30px, white 2px, transparent 0)`,
            backgroundSize: '60px 60px'
          }}></div>
        </div>

        <div className="max-w-5xl mx-auto text-center relative z-10">
          <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-full mb-8" style={{backgroundColor: 'rgba(255, 255, 255, 0.1)', border: '1px solid rgba(255, 255, 255, 0.2)'}}>
            <Zap className="w-4 h-4 text-white" />
            <span className="text-sm font-semibold text-white">Get Started Today</span>
          </div>

          <h2 className="text-5xl md:text-6xl font-bold mb-6 text-white leading-tight">
            Ready to Unlock<br />Climate Insights?
          </h2>
          <p className="text-xl text-green-100 mb-12 max-w-3xl mx-auto">
            Join thousands of users leveraging AI-powered climate intelligence for smarter decisions. Start your free trial today.
          </p>
          
          <div className="flex flex-col sm:flex-row justify-center items-center gap-4">
            <Link 
              to="/chat" 
              className="group px-10 py-5 rounded-xl text-lg font-semibold transition-all duration-300 hover:scale-105 shadow-2xl flex items-center space-x-3" 
              style={{backgroundColor: '#F4991A', color: 'white'}}
            >
              <MessageSquare className="w-6 h-6" />
              <span>Start Free Chat</span>
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link 
              to="/pricing" 
              className="px-10 py-5 rounded-xl text-lg font-semibold transition-all duration-300 hover:scale-105 shadow-xl border-2 flex items-center space-x-3" 
              style={{borderColor: 'white', color: 'white', backgroundColor: 'rgba(255, 255, 255, 0.1)'}}
            >
              <TrendingUp className="w-6 h-6" />
              <span>View Pricing</span>
            </Link>
          </div>

          {/* Trust Indicators */}
          <div className="mt-16 pt-12" style={{borderTop: '1px solid rgba(255, 255, 255, 0.2)'}}>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-white">
              <div>
                <div className="text-3xl font-bold mb-2">2,400+</div>
                <div className="text-green-200">Active Users</div>
              </div>
              <div>
                <div className="text-3xl font-bold mb-2">9,125+</div>
                <div className="text-green-200">Daily Data Points</div>
              </div>
              <div>
                <div className="text-3xl font-bold mb-2">98.9%</div>
                <div className="text-green-200">Prediction Accuracy</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section - Redesigned */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <div className="inline-flex items-center space-x-2 px-4 py-2 rounded-full mb-6" style={{backgroundColor: '#F9F5F0'}}>
              <Star className="w-4 h-4" style={{color: '#F4991A'}} />
              <span className="text-sm font-semibold" style={{color: '#344F1F'}}>Why Choose Us</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-bold mb-6 text-gray-800">Powerful Climate Intelligence</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">Comprehensive tools and AI-driven insights for smarter climate analysis</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="group p-8 rounded-2xl transition-all duration-300 hover:scale-105 hover:shadow-2xl border-2" style={{borderColor: '#F2EAD3', backgroundColor: 'white'}}>
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0 w-14 h-14 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform" style={{backgroundColor: '#F9F5F0'}}>
                  <TrendingUp className="w-7 h-7" style={{color: '#F4991A'}} />
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold mb-3 text-gray-800">Advanced Analytics</h3>
                  <p className="text-gray-600 leading-relaxed">AI algorithms analyze 25+ years of data to identify patterns and predict future climate trends with remarkable accuracy.</p>
                </div>
              </div>
            </div>

            {/* Feature 2 */}
            <div className="group p-8 rounded-2xl transition-all duration-300 hover:scale-105 hover:shadow-2xl border-2" style={{borderColor: '#F2EAD3', backgroundColor: 'white'}}>
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0 w-14 h-14 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform" style={{backgroundColor: '#F2EAD3'}}>
                  <MessageSquare className="w-7 h-7" style={{color: '#344F1F'}} />
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold mb-3 text-gray-800">AI Chat Assistant</h3>
                  <p className="text-gray-600 leading-relaxed">Get instant answers about climate data, weather patterns, and trends through our intelligent conversational interface.</p>
                </div>
              </div>
            </div>

            {/* Feature 3 */}
            <div className="group p-8 rounded-2xl transition-all duration-300 hover:scale-105 hover:shadow-2xl border-2" style={{borderColor: '#F2EAD3', backgroundColor: 'white'}}>
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0 w-14 h-14 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform" style={{backgroundColor: '#F9F5F0'}}>
                  <FileText className="w-7 h-7" style={{color: '#F4991A'}} />
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold mb-3 text-gray-800">Custom Predictions</h3>
                  <p className="text-gray-600 leading-relaxed mb-4">Generate detailed weather forecasts tailored to your location with our advanced prediction engine.</p>
                  <Link 
                    to="/weather-predictor" 
                    className="inline-flex items-center text-sm font-semibold group-hover:translate-x-1 transition-transform" 
                    style={{color: '#F4991A'}}
                  >
                    Try Predictor <ArrowRight className="w-4 h-4 ml-1" />
                  </Link>
                </div>
              </div>
            </div>

            {/* Feature 4 */}
            <div className="group p-8 rounded-2xl transition-all duration-300 hover:scale-105 hover:shadow-2xl border-2" style={{borderColor: '#F2EAD3', backgroundColor: 'white'}}>
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0 w-14 h-14 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform" style={{backgroundColor: '#F2EAD3'}}>
                  <BarChart3 className="w-7 h-7" style={{color: '#344F1F'}} />
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold mb-3 text-gray-800">Interactive Dashboards</h3>
                  <p className="text-gray-600 leading-relaxed">Visualize climate data with beautiful, interactive charts and real-time analytics dashboards.</p>
                </div>
              </div>
            </div>

            {/* Feature 5 */}
            <div className="group p-8 rounded-2xl transition-all duration-300 hover:scale-105 hover:shadow-2xl border-2" style={{borderColor: '#F2EAD3', backgroundColor: 'white'}}>
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0 w-14 h-14 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform" style={{backgroundColor: '#F9F5F0'}}>
                  <Globe className="w-7 h-7" style={{color: '#F4991A'}} />
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold mb-3 text-gray-800">Geospatial Analysis</h3>
                  <p className="text-gray-600 leading-relaxed">Explore climate data with interactive maps and location-based insights for informed decision-making.</p>
                </div>
              </div>
            </div>

            {/* Feature 6 */}
            <div className="group p-8 rounded-2xl transition-all duration-300 hover:scale-105 hover:shadow-2xl border-2" style={{borderColor: '#F2EAD3', backgroundColor: 'white'}}>
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0 w-14 h-14 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform" style={{backgroundColor: '#F2EAD3'}}>
                  <Zap className="w-7 h-7" style={{color: '#344F1F'}} />
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-bold mb-3 text-gray-800">Real-time Updates</h3>
                  <p className="text-gray-600 leading-relaxed">Stay informed with live weather updates, climate news, and automated alerts for critical conditions.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

    </div>
  );
};

export default ClimateHomepage;