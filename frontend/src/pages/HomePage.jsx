import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar } from 'recharts';
import { Menu, X, TrendingUp, Cloud, MessageSquare, FileText, Home, Info, Mail, HelpCircle, FileCheck, LogIn, LogOut, ChevronDown, Sun, Thermometer, Droplets, Wind, User } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import ChatWindow from '../components/ChatWindow';

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
    { condition: 'Clear', count: 45, color: '#A294F9' },
    { condition: 'Partly Cloudy', count: 38, color: '#CDC1FF' },
    { condition: 'Cloudy', count: 22, color: '#E5D9F2' },
    { condition: 'Rainy', count: 15, color: '#F5EFFF' }
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
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-50" style={{backgroundColor: '#F5EFFF'}}>

      {/* Hero Section */}
      <section className="relative py-20 px-4 overflow-hidden">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <div className="inline-flex items-center justify-center mb-6 transition-all duration-1000 transform">
              <div className="p-4 rounded-full" style={{backgroundColor: '#E5D9F2'}}>
                {heroSlides[currentSlide].icon}
              </div>
            </div>
            <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
              {heroSlides[currentSlide].title}
            </h1>
            <p className="text-xl text-gray-600 mb-12 max-w-3xl mx-auto">
              {heroSlides[currentSlide].subtitle}
            </p>
            
            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row justify-center items-center space-y-4 sm:space-y-0 sm:space-x-6">
              <Link to="/chat" className="px-8 py-4 rounded-xl text-white font-semibold text-lg transition-all duration-200 hover:scale-105 shadow-lg hover:shadow-xl flex items-center space-x-2" style={{backgroundColor: '#A294F9'}}>
                <MessageSquare className="w-5 h-5" />
                <span>Chat with AI</span>
              </Link>
              <Link to="/pricing" className="px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-200 hover:scale-105 shadow-lg hover:shadow-xl border-2 flex items-center space-x-2" style={{borderColor: '#CDC1FF', color: '#6B46C1', backgroundColor: 'white'}}>
                <TrendingUp className="w-5 h-5" />
                <span>View Plans</span>
              </Link>
            </div>

            {/* Slide indicators */}
            <div className="flex justify-center space-x-3 mt-8">
              {heroSlides.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentSlide(index)}
                  className={`w-3 h-3 rounded-full transition-all duration-300 ${
                    index === currentSlide ? 'w-8' : ''
                  }`}
                  style={{backgroundColor: index === currentSlide ? '#A294F9' : '#E5D9F2'}}
                />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 px-4" style={{backgroundColor: 'white'}}>
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="text-center p-6 rounded-xl transition-transform hover:scale-105" style={{backgroundColor: '#F5EFFF'}}>
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-lg mb-4" style={{backgroundColor: '#A294F9'}}>
                <Thermometer className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-gray-800">30.5°C</h3>
              <p className="text-gray-600">Avg Temperature</p>
            </div>
            <div className="text-center p-6 rounded-xl transition-transform hover:scale-105" style={{backgroundColor: '#E5D9F2'}}>
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-lg mb-4" style={{backgroundColor: '#CDC1FF'}}>
                <Droplets className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-gray-800">76.2%</h3>
              <p className="text-gray-600">Humidity</p>
            </div>
            <div className="text-center p-6 rounded-xl transition-transform hover:scale-105" style={{backgroundColor: '#CDC1FF'}}>
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-lg mb-4" style={{backgroundColor: '#A294F9'}}>
                <Sun className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-2xl font-bold text-gray-800">127</h3>
              <p className="text-gray-600">Clear Days</p>
            </div>
            <div className="text-center p-6 rounded-xl transition-transform hover:scale-105" style={{backgroundColor: '#A294F9'}}>
              <div className="inline-flex items-center justify-center w-12 h-12 rounded-lg mb-4" style={{backgroundColor: 'white'}}>
                <Wind className="w-6 h-6" style={{color: '#A294F9'}} />
              </div>
              <h3 className="text-2xl font-bold text-white">25+ Years</h3>
              <p className="text-purple-100">Data Coverage</p>
            </div>
          </div>
        </div>
      </section>

      {/* Data Visualizations */}
      <section className="py-20 px-4" style={{backgroundColor: '#F5EFFF'}}>
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-6 text-gray-800">Climate Trends & Analytics</h2>
            <p className="text-xl text-gray-600">Real-time insights from decades of weather data</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
            {/* Temperature Chart */}
            <div className="bg-white rounded-2xl p-6 shadow-xl hover:shadow-2xl transition-shadow border border-purple-100">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-gray-800">Temperature Trends</h3>
                <div className="flex items-center space-x-4 text-sm">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 rounded-full" style={{backgroundColor: '#A294F9'}}></div>
                    <span>Max Temp</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 rounded-full" style={{backgroundColor: '#CDC1FF'}}></div>
                    <span>Min Temp</span>
                  </div>
                </div>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={temperatureData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5D9F2" />
                  <XAxis dataKey="month" stroke="#6B7280" />
                  <YAxis stroke="#6B7280" />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #E5D9F2',
                      borderRadius: '8px'
                    }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="tempmax" 
                    stroke="#A294F9" 
                    strokeWidth={3}
                    dot={{ fill: '#A294F9', strokeWidth: 2, r: 4 }}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="tempmin" 
                    stroke="#CDC1FF" 
                    strokeWidth={3}
                    dot={{ fill: '#CDC1FF', strokeWidth: 2, r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Humidity Chart */}
            <div className="bg-white rounded-2xl p-6 shadow-xl hover:shadow-2xl transition-shadow border border-purple-100">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-gray-800">Humidity Levels</h3>
                <span className="text-sm text-gray-500">Monthly Average (%)</span>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={humidityData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5D9F2" />
                  <XAxis dataKey="month" stroke="#6B7280" />
                  <YAxis stroke="#6B7280" />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #E5D9F2',
                      borderRadius: '8px'
                    }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="humidity" 
                    stroke="#A294F9" 
                    fill="url(#humidityGradient)"
                    strokeWidth={2}
                  />
                  <defs>
                    <linearGradient id="humidityGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#A294F9" stopOpacity={0.8}/>
                      <stop offset="100%" stopColor="#A294F9" stopOpacity={0.1}/>
                    </linearGradient>
                  </defs>
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Weather Conditions Chart */}
          <div className="bg-white rounded-2xl p-6 shadow-xl hover:shadow-2xl transition-shadow border border-purple-100">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-gray-800">Weather Conditions Distribution</h3>
              <span className="text-sm text-gray-500">Days per Year</span>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={weatherConditions}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5D9F2" />
                <XAxis dataKey="condition" stroke="#6B7280" />
                <YAxis stroke="#6B7280" />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: 'white',
                    border: '1px solid #E5D9F2',
                    borderRadius: '8px'
                  }}
                />
                <Bar 
                  dataKey="count" 
                  radius={[4, 4, 0, 0]}
                  fill="#A294F9"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-6 text-gray-800">Powerful Features</h2>
            <p className="text-xl text-gray-600">Everything you need to analyze climate data effectively</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center p-8 rounded-2xl transition-all duration-300 hover:scale-105 hover:shadow-xl" style={{backgroundColor: '#F5EFFF'}}>
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full mb-6" style={{backgroundColor: '#A294F9'}}>
                <TrendingUp className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold mb-4 text-gray-800">Advanced Analytics</h3>
              <p className="text-gray-600">Sophisticated algorithms analyze patterns and predict future climate trends with high accuracy.</p>
            </div>

            <div className="text-center p-8 rounded-2xl transition-all duration-300 hover:scale-105 hover:shadow-xl" style={{backgroundColor: '#E5D9F2'}}>
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full mb-6" style={{backgroundColor: '#CDC1FF'}}>
                <MessageSquare className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold mb-4 text-gray-800">AI Chat Assistant</h3>
              <p className="text-gray-600">Get instant answers about climate data and weather patterns through our intelligent chat interface.</p>
            </div>

            <div className="text-center p-8 rounded-2xl transition-all duration-300 hover:scale-105 hover:shadow-xl" style={{backgroundColor: '#CDC1FF'}}>
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full mb-6" style={{backgroundColor: '#A294F9'}}>
                <FileText className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold mb-4 text-gray-800">Custom Reports</h3>
              <p className="text-gray-600">Generate detailed reports tailored to your specific research needs and data requirements.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Chat Window */}
      <ChatWindow />
    </div>
  );
};

export default ClimateHomepage;