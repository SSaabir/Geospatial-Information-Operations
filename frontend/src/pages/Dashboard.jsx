import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, Thermometer, Droplets, Wind, Sun, Eye, Activity, AlertTriangle, CheckCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import UsageWidget from '../components/UsageWidget';
import NewsAlerts from '../components/NewsAlerts';
import HistoricalDataDownload from '../components/HistoricalDataDownload';

export default function Dashboard() {
  const { user, isAuthenticated, apiCall } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');

  // Redirect admins to admin dashboard
  useEffect(() => {
    if (user?.is_admin) {
      navigate('/admin/dashboard');
    }
  }, [user, navigate]);

  // State for fetched data
  const [temperatureData, setTemperatureData] = useState([]);
  const [weeklyData, setWeeklyData] = useState([]);
  const [regionData, setRegionData] = useState([]);
  const [alerts, setAlerts] = useState([]);

  // Fetch backend data
  useEffect(() => {
    if (!isAuthenticated || user?.is_admin) return;

    const fetchDashboardData = async () => {
      try {
        // Fetch real weather trends from backend
        const trendsResponse = await apiCall('/dashboard/weather/trends?days=7');
        if (trendsResponse?.daily_temps) {
          // Transform for hourly view
          const hourlyData = [];
          const latestDay = trendsResponse.daily_temps[trendsResponse.daily_temps.length - 1];
          
          {/* Generate hourly points for today based on latest data */}
          for (let hour = 0; hour <= 20; hour += 4) {
            hourlyData.push({
              time: `${hour.toString().padStart(2, '0')}:00`,
              temp: Math.round((latestDay.temp + (Math.random() * 4 - 2)) * 10) / 10, // Round to 1 decimal
              humidity: Math.round(latestDay.humidity + (Math.random() * 10 - 5))
            });
          }
          setTemperatureData(hourlyData);
          
          // Transform weekly data
          const weekly = trendsResponse.daily_temps.map((day, index) => {
            const date = new Date(day.date);
            const dayName = date.toLocaleDateString('en-US', { weekday: 'short' });
            return {
              day: dayName,
              temp: Math.round(day.temp),
              rainfall: Math.round(Math.random() * 15), // Mock rainfall for now
              wind: Math.round(day.wind_speed || 0)
            };
          });
          setWeeklyData(weekly);
        }

        // Fetch real alerts from notifications
        const alertsResponse = await apiCall('/dashboard/activity/recent?limit=5');
        if (alertsResponse?.activities) {
          const formattedAlerts = alertsResponse.activities.map(activity => ({
            id: activity.id,
            type: activity.type === 'warning' || activity.type === 'error' ? 'warning' :
                  activity.type === 'success' ? 'success' : 'info',
            message: activity.message || activity.title,
            time: calculateTimeAgo(activity.timestamp)
          }));
          setAlerts(formattedAlerts);
        }

        // Regional data (keep as mock for now - would need regional weather data)
        setRegionData([
          { name: 'Colombo', value: 30, color: '#8B5CF6' },
          { name: 'Kandy', value: 25, color: '#6366F1' },
          { name: 'Galle', value: 28, color: '#A855F7' },
          { name: 'Jaffna', value: 32, color: '#EC4899' }
        ]);

      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        // Fallback to mock data on error
        setTemperatureData([
          { time: '00:00', temp: 24.5, humidity: 78 },
          { time: '04:00', temp: 23.2, humidity: 82 },
          { time: '08:00', temp: 26.8, humidity: 75 },
          { time: '12:00', temp: 31.5, humidity: 65 },
          { time: '16:00', temp: 29.3, humidity: 70 },
          { time: '20:00', temp: 26.1, humidity: 76 }
        ]);
      }
    };

    fetchDashboardData();
  }, [isAuthenticated, user?.is_admin, selectedTimeRange]);

  // Helper function to calculate time ago
  const calculateTimeAgo = (timestamp) => {
    if (!timestamp) return 'Unknown';
    const now = new Date();
    const time = new Date(timestamp);
    const diffMs = now - time;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffDays > 0) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    if (diffHours > 0) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffMins > 0) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    return 'Just now';
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 to-amber-50 flex items-center justify-center" style={{ backgroundColor: '#F9F5F0' }}>
        <div className="text-center p-8">
          <Activity className="w-16 h-16 text-orange-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Dashboard Access Restricted</h2>
          <p className="text-gray-600 mb-6">Please log in to access your weather dashboard.</p>
          <a
            href="/login"
            className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-orange-600 to-green-800 text-white rounded-xl hover:from-orange-700 hover:to-green-900 transition-all duration-200"
          >
            Go to Login
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-amber-50" style={{ backgroundColor: '#F9F5F0' }}>
      <div className="container mx-auto px-4 py-8">

        <UsageWidget />

        {/* Dashboard Header */}
        <div className="mb-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
            <div className="mb-4 lg:mb-0">
              <h1 className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-green-800 bg-clip-text text-transparent">
                Weather Dashboard
              </h1>
              <p className="text-gray-600 mt-2">
                Welcome back, {user?.name}! Here's your weather analytics overview.
              </p>
            </div>
          </div>
        </div>

        {/* Quick Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Current Temperature */}
          <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border" style={{borderColor: '#F2EAD3'}}>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Current Temperature</p>
                <p className="text-2xl font-bold text-gray-800">
                  {temperatureData.length ? `${Math.round(temperatureData[temperatureData.length - 1].temp * 10) / 10}°C` : '...'}
                </p>
                <p className="text-green-600 text-xs flex items-center mt-1">
                  <TrendingUp className="w-3 h-3 mr-1" /> +2° from yesterday
                </p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-r from-orange-400 to-red-500 rounded-xl flex items-center justify-center">
                <Thermometer className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>

          {/* Humidity */}
          <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-orange-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Humidity</p>
                <p className="text-2xl font-bold text-gray-800">
                  {temperatureData.length ? `${Math.round(temperatureData[temperatureData.length - 1].humidity)}%` : '...'}
                </p>
                <p className="text-blue-600 text-xs flex items-center mt-1">
                  <Droplets className="w-3 h-3 mr-1" /> Normal range
                </p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-r from-blue-400 to-cyan-500 rounded-xl flex items-center justify-center">
                <Droplets className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>

          {/* Wind Speed */}
          <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-orange-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Wind Speed</p>
                <p className="text-2xl font-bold text-gray-800">
                  {weeklyData.length ? `${weeklyData[weeklyData.length - 1].wind} km/h` : '...'}
                </p>
                <p className="text-gray-600 text-xs flex items-center mt-1">
                  <Wind className="w-3 h-3 mr-1" /> Light breeze
                </p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-r from-gray-400 to-gray-600 rounded-xl flex items-center justify-center">
                <Wind className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>

          {/* UV Index */}
          <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-orange-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">UV Index</p>
                <p className="text-2xl font-bold text-gray-800">8</p>
                <p className="text-red-600 text-xs flex items-center mt-1">
                  <Sun className="w-3 h-3 mr-1" /> Very High
                </p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-xl flex items-center justify-center">
                <Sun className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        </div>

        {/* Main Dashboard Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Temperature Trend Chart */}
          <div className="lg:col-span-2">
            <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-orange-100">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-gray-800">Temperature Trend</h3>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setActiveTab('temperature')}
                    className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                      activeTab === 'temperature'
                        ? 'bg-orange-100 text-orange-700'
                        : 'text-gray-600 hover:text-orange-600'
                    }`}
                  >
                    Temperature
                  </button>
                  <button
                    onClick={() => setActiveTab('humidity')}
                    className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                      activeTab === 'humidity'
                        ? 'bg-orange-100 text-orange-700'
                        : 'text-gray-600 hover:text-orange-600'
                    }`}
                  >
                    Humidity
                  </button>
                </div>
              </div>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={temperatureData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                    <XAxis dataKey="time" stroke="#6B7280" fontSize={12} />
                    <YAxis stroke="#6B7280" fontSize={12} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'white',
                        border: '1px solid #D1D5DB',
                        borderRadius: '12px',
                        boxShadow: '0 10px 25px -3px rgba(0, 0, 0, 0.1)',
                      }}
                    />
                    <defs>
                      <linearGradient id="tempGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0.05} />
                      </linearGradient>
                    </defs>
                    <Area
                      type="monotone"
                      dataKey={activeTab === 'temperature' ? 'temp' : 'humidity'}
                      stroke="#8B5CF6"
                      strokeWidth={3}
                      fill="url(#tempGradient)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Regional Weather Distribution */}
          <div className="space-y-6">
            <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-orange-100">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Regional Distribution</h3>
              <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie data={regionData} cx="50%" cy="50%" innerRadius={40} outerRadius={80} dataKey="value">
                      {regionData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="space-y-2">
                {regionData.map((region, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: region.color }}></div>
                      <span className="text-sm text-gray-600">{region.name}</span>
                    </div>
                    <span className="text-sm font-medium text-gray-800">{region.value}%</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Alerts */}
            <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-orange-100">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Recent Alerts</h3>
              <div className="space-y-3">
                {alerts.map((alert) => (
                  <div key={alert.id} className="flex items-start space-x-3 p-3 rounded-xl bg-gray-50">
                    <div
                      className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${
                        alert.type === 'warning' ? 'bg-yellow-100' : alert.type === 'info' ? 'bg-blue-100' : 'bg-green-100'
                      }`}
                    >
                      {alert.type === 'warning' && <AlertTriangle className="w-3 h-3 text-yellow-600" />}
                      {alert.type === 'info' && <Eye className="w-3 h-3 text-blue-600" />}
                      {alert.type === 'success' && <CheckCircle className="w-3 h-3 text-green-600" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-800">{alert.message}</p>
                      <p className="text-xs text-gray-500 mt-1">{alert.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Historical Data Download Section */}
        <div className="mt-8">
          <HistoricalDataDownload />
        </div>

        {/* News & Alerts Section */}
        <div className="mt-8">
          <NewsAlerts />
        </div>

        {/* Weekly Overview */}
        <div className="mt-8">
          <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-orange-100">
            <h3 className="text-xl font-semibold text-gray-800 mb-6">Weekly Overview</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={weeklyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis dataKey="day" stroke="#6B7280" fontSize={12} />
                  <YAxis stroke="#6B7280" fontSize={12} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #D1D5DB',
                      borderRadius: '12px',
                      boxShadow: '0 10px 25px -3px rgba(0, 0, 0, 0.1)',
                    }}
                  />
                  <Bar dataKey="temp" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="rainfall" fill="#06B6D4" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
