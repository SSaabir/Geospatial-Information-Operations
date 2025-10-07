import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, Thermometer, Droplets, Wind, Sun, Eye, Activity, AlertTriangle, CheckCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export default function Dashboard() {
  const { user, isAuthenticated } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');

  // State for fetched data
  const [temperatureData, setTemperatureData] = useState([]);
  const [weeklyData, setWeeklyData] = useState([]);
  const [regionData, setRegionData] = useState([]);
  const [alerts, setAlerts] = useState([]);

  // Fetch backend data
  useEffect(() => {
    if (!isAuthenticated) return;
    // Use local fallback/mock data to avoid calling removed /api/weather endpoints
    const now = new Date();

    const makeHourly = () => {
      const arr = [];
      for (let i = 0; i < 24; i++) {
        const t = new Date(now.getTime() - (23 - i) * 60 * 60 * 1000).toISOString();
        arr.push({ time: t, temp: 25 + (i % 6), humidity: 60 + (i % 10), wind: 6 + (i % 4) });
      }
      return arr;
    };

    const makeWeekly = () => {
      const out = [];
      for (let d = 6; d >= 0; d--) {
        const day = new Date(now.getTime() - d * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
        out.push({ day, temp: 26 + (d % 3), wind: 7 + (d % 3), rainfall: 0 });
      }
      return out;
    };

    const makeRegions = () => [
      { name: 'Colombo', value: 45.0, color: '#8B5CF6' },
      { name: 'Kandy', value: 20.0, color: '#06B6D4' },
      { name: 'Galle', value: 12.0, color: '#F59E0B' },
      { name: 'Jaffna', value: 8.0, color: '#EF4444' },
      { name: 'Other', value: 15.0, color: '#10B981' },
    ];

    const makeAlerts = () => [
      { id: 1, message: 'Light showers expected tomorrow in Colombo.', type: 'info', time: new Date().toISOString() },
      { id: 2, message: 'High UV index today - take care.', type: 'warning', time: new Date().toISOString() },
    ];

    setTemperatureData(makeHourly());
    setWeeklyData(makeWeekly());
    setRegionData(makeRegions());
    setAlerts(makeAlerts());
  }, [isAuthenticated, selectedTimeRange]);

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-50 flex items-center justify-center" style={{ backgroundColor: '#F5EFFF' }}>
        <div className="text-center p-8">
          <Activity className="w-16 h-16 text-purple-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Dashboard Access Restricted</h2>
          <p className="text-gray-600 mb-6">Please log in to access your weather dashboard.</p>
          <a
            href="/login"
            className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl hover:from-purple-700 hover:to-indigo-700 transition-all duration-200"
          >
            Go to Login
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-50" style={{ backgroundColor: '#F5EFFF' }}>
      <div className="container mx-auto px-4 py-8">
        {/* Dashboard Header */}
        <div className="mb-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
            <div className="mb-4 lg:mb-0">
              <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                Weather Dashboard
              </h1>
              <p className="text-gray-600 mt-2">
                Welcome back, {user?.name}! Here's your weather analytics overview.
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <select
                value={selectedTimeRange}
                onChange={(e) => setSelectedTimeRange(e.target.value)}
                className="px-4 py-2 border border-purple-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white"
              >
                <option value="24h">Last 24 Hours</option>
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
                <option value="90d">Last 90 Days</option>
              </select>
            </div>
          </div>
        </div>

        {/* Quick Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Current Temperature */}
          <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-purple-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Current Temperature</p>
                <p className="text-2xl font-bold text-gray-800">
                  {temperatureData.length ? `${temperatureData[temperatureData.length - 1].temp}°C` : '...'}
                </p>
                <p className="text-green-600 text-xs flex items-center mt-1">
                  <TrendingUp className="w-3 h-3 mr-1" /> +2.5° from yesterday
                </p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-r from-orange-400 to-red-500 rounded-xl flex items-center justify-center">
                <Thermometer className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>

          {/* Humidity */}
          <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-purple-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Humidity</p>
                <p className="text-2xl font-bold text-gray-800">
                  {temperatureData.length ? `${temperatureData[temperatureData.length - 1].humidity}%` : '...'}
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
          <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-purple-100">
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
          <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-purple-100">
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
            <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-purple-100">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-gray-800">Temperature Trend</h3>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setActiveTab('temperature')}
                    className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                      activeTab === 'temperature'
                        ? 'bg-purple-100 text-purple-700'
                        : 'text-gray-600 hover:text-purple-600'
                    }`}
                  >
                    Temperature
                  </button>
                  <button
                    onClick={() => setActiveTab('humidity')}
                    className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                      activeTab === 'humidity'
                        ? 'bg-purple-100 text-purple-700'
                        : 'text-gray-600 hover:text-purple-600'
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
            <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-purple-100">
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
            <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-purple-100">
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

        {/* Weekly Overview */}
        <div className="mt-8">
          <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-purple-100">
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
