import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, Thermometer, Droplets, Wind, Sun, Eye, Activity, AlertTriangle, CheckCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export default function Dashboard() {
  const { user, isAuthenticated } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');

   // State for fetched data
  const [loading, setLoading] = useState(true);
  const [currentWeather, setCurrentWeather] = useState(null);
  const [trendData, setTrendData] = useState([]);
  const [weeklyData, setWeeklyData] = useState([]);
  const [regionData, setRegionData] = useState([]);
  const [alerts, setAlerts] = useState([]);

   // Fetch backend data
  useEffect(() => {
    if (!isAuthenticated) return;

    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        const token = localStorage.getItem('access_token');
        const headers = {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        };

        // Fetch current weather
        const currentRes = await fetch('http://localhost:8000/api/dashboard/weather/current', { headers });
        const currentData = await currentRes.json();
        setCurrentWeather(currentData);

        // Fetch trend data based on selected time range
        const trendRes = await fetch(`http://localhost:8000/api/dashboard/weather/trend?time_range=${selectedTimeRange}`, { headers });
        const trendData = await trendRes.json();
        setTrendData(trendData);

        // Fetch weekly data
        const weeklyRes = await fetch('http://localhost:8000/api/dashboard/weather/weekly', { headers });
        const weeklyData = await weeklyRes.json();
        setWeeklyData(weeklyData);

        // Fetch regional data
        const regionRes = await fetch('http://localhost:8000/api/dashboard/weather/regions', { headers });
        const regionData = await regionRes.json();
        setRegionData(regionData);

        // Fetch alerts
        const alertsRes = await fetch('http://localhost:8000/api/dashboard/alerts', { headers });
        const alertsData = await alertsRes.json();
        setAlerts(alertsData);

      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
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
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-indigo-50 to-pink-50" style={{ backgroundColor: '#F5EFFF' }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {/* Dashboard Header */}
        <div className="mb-6 sm:mb-8">
          <div className="bg-white/80 backdrop-blur-xl rounded-3xl p-6 sm:p-8 shadow-xl border border-purple-100/50">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <div className="w-12 h-12 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg">
                    <Activity className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h1 className="text-2xl sm:text-3xl font-bold bg-gradient-to-r from-purple-600 via-indigo-600 to-pink-600 bg-clip-text text-transparent">
                      Weather Dashboard
                    </h1>
                    <p className="text-sm text-gray-500 mt-0.5">Real-time Climate Intelligence</p>
                  </div>
                </div>
                <p className="text-gray-600 mt-3 flex items-center gap-2">
                  <span className="font-medium text-gray-800">Welcome back, {user?.name}!</span>
                  <span className="hidden sm:inline">•</span>
                  <span className="hidden sm:inline text-sm">Here's your weather analytics overview</span>
                </p>
              </div>
              <div className="flex items-center gap-3">
                <select
                  value={selectedTimeRange}
                  onChange={(e) => setSelectedTimeRange(e.target.value)}
                  className="px-4 py-2.5 border-2 border-purple-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-purple-400 bg-white text-gray-700 font-medium transition-all duration-200 hover:border-purple-300 cursor-pointer shadow-sm"
                >
                  <option value="24h">Last 24 Hours</option>
                  <option value="7d">Last 7 Days</option>
                  <option value="30d">Last 30 Days</option>
                  <option value="90d">Last 90 Days</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6 mb-6 sm:mb-8">
          {/* Current Temperature */}
          <div className="bg-white/90 backdrop-blur-xl rounded-2xl p-5 sm:p-6 shadow-lg hover:shadow-2xl transition-all duration-300 border border-purple-100/50 hover:border-purple-200 hover:scale-[1.02] group">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-gray-500 text-xs sm:text-sm font-medium uppercase tracking-wide mb-2">Temperature</p>
                <p className="text-2xl sm:text-3xl font-bold text-gray-800 mb-1">
                  {currentWeather ? `${currentWeather.temperature}°C` : loading ? '...' : 'N/A'}
                </p>
                <p className="text-green-600 text-xs flex items-center gap-1 font-medium">
                  <TrendingUp className="w-3.5 h-3.5" /> +2.5° from yesterday
                </p>
              </div>
              <div className="w-14 h-14 bg-gradient-to-br from-orange-400 to-red-500 rounded-2xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                <Thermometer className="w-7 h-7 text-white" />
              </div>
            </div>
          </div>

          {/* Humidity */}
          <div className="bg-white/90 backdrop-blur-xl rounded-2xl p-5 sm:p-6 shadow-lg hover:shadow-2xl transition-all duration-300 border border-purple-100/50 hover:border-purple-200 hover:scale-[1.02] group">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-gray-500 text-xs sm:text-sm font-medium uppercase tracking-wide mb-2">Humidity</p>
                <p className="text-2xl sm:text-3xl font-bold text-gray-800 mb-1">
                  {currentWeather ? `${currentWeather.humidity}%` : loading ? '...' : 'N/A'}
                </p>
                <p className="text-blue-600 text-xs flex items-center gap-1 font-medium">
                  <Droplets className="w-3.5 h-3.5" /> Normal range
                </p>
              </div>
              <div className="w-14 h-14 bg-gradient-to-br from-blue-400 to-cyan-500 rounded-2xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                <Droplets className="w-7 h-7 text-white" />
              </div>
            </div>
          </div>

          {/* Wind Speed */}
          <div className="bg-white/90 backdrop-blur-xl rounded-2xl p-5 sm:p-6 shadow-lg hover:shadow-2xl transition-all duration-300 border border-purple-100/50 hover:border-purple-200 hover:scale-[1.02] group">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-gray-500 text-xs sm:text-sm font-medium uppercase tracking-wide mb-2">Wind Speed</p>
                <p className="text-2xl sm:text-3xl font-bold text-gray-800 mb-1">
                  {currentWeather ? `${currentWeather.wind_speed}` : loading ? '...' : 'N/A'}
                </p>
                <p className="text-gray-600 text-xs flex items-center gap-1 font-medium">
                  <Wind className="w-3.5 h-3.5" /> Light breeze
                </p>
              </div>
              <div className="w-14 h-14 bg-gradient-to-br from-slate-400 to-slate-600 rounded-2xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                <Wind className="w-7 h-7 text-white" />
              </div>
            </div>
          </div>

          {/* UV Index */}
          <div className="bg-white/90 backdrop-blur-xl rounded-2xl p-5 sm:p-6 shadow-lg hover:shadow-2xl transition-all duration-300 border border-purple-100/50 hover:border-purple-200 hover:scale-[1.02] group">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <p className="text-gray-500 text-xs sm:text-sm font-medium uppercase tracking-wide mb-2">UV Index</p>
                <p className="text-2xl sm:text-3xl font-bold text-gray-800 mb-1">
                  {currentWeather ? currentWeather.uv_index : loading ? '...' : 'N/A'}
                </p>
                <p className="text-red-600 text-xs flex items-center gap-1 font-medium">
                  <Sun className="w-3.5 h-3.5" /> Very High
                </p>
              </div>
              <div className="w-14 h-14 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-2xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300">
                <Sun className="w-7 h-7 text-white" />
              </div>
            </div>
          </div>
        </div>

        {/* Main Dashboard Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 sm:gap-8">
          {/* Temperature Trend Chart */}
          <div className="lg:col-span-2">
            <div className="bg-white/90 backdrop-blur-xl rounded-2xl p-5 sm:p-6 shadow-lg border border-purple-100/50 hover:shadow-xl transition-shadow duration-300">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-3">
                <div>
                  <h3 className="text-lg sm:text-xl font-bold text-gray-800 mb-1">Temperature Trend</h3>
                  <p className="text-xs sm:text-sm text-gray-500">Real-time climate data visualization</p>
                </div>
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => setActiveTab('temperature')}
                    className={`px-3 sm:px-4 py-2 rounded-lg text-xs sm:text-sm font-medium transition-all duration-200 ${
                      activeTab === 'temperature'
                        ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-md'
                        : 'text-gray-600 hover:text-purple-600 hover:bg-purple-50 border border-gray-200'
                    }`}
                  >
                    Temperature
                  </button>
                  <button
                    onClick={() => setActiveTab('humidity')}
                    className={`px-3 sm:px-4 py-2 rounded-lg text-xs sm:text-sm font-medium transition-all duration-200 ${
                      activeTab === 'humidity'
                        ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-md'
                        : 'text-gray-600 hover:text-purple-600 hover:bg-purple-50 border border-gray-200'
                    }`}
                  >
                    Humidity
                  </button>
                </div>
              </div>
              <div className="h-64 sm:h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={trendData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                    <XAxis dataKey="time" stroke="#6B7280" fontSize={12} />
                    <YAxis stroke="#6B7280" fontSize={12} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'rgba(255, 255, 255, 0.95)',
                        border: '1px solid #D1D5DB',
                        borderRadius: '12px',
                        boxShadow: '0 10px 25px -3px rgba(0, 0, 0, 0.1)',
                      }}
                    />
                    <defs>
                      <linearGradient id="tempGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.4} />
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
            <div className="bg-white/90 backdrop-blur-xl rounded-2xl p-5 sm:p-6 shadow-lg border border-purple-100/50 hover:shadow-xl transition-shadow duration-300">
              <div className="mb-4">
                <h3 className="text-lg font-bold text-gray-800 mb-1">Regional Distribution</h3>
                <p className="text-xs text-gray-500">Weather patterns by region</p>
              </div>
              <div className="h-48 mb-4">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie 
                      data={regionData} 
                      cx="50%" 
                      cy="50%" 
                      innerRadius={45} 
                      outerRadius={75} 
                      dataKey="value"
                      paddingAngle={2}
                    >
                      {regionData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{
                        backgroundColor: 'rgba(255, 255, 255, 0.95)',
                        border: '1px solid #D1D5DB',
                        borderRadius: '8px',
                        fontSize: '12px'
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="space-y-2.5">
                {regionData.map((region, index) => (
                  <div key={index} className="flex items-center justify-between p-2.5 rounded-lg hover:bg-gray-50 transition-colors">
                    <div className="flex items-center gap-2.5">
                      <div className="w-3.5 h-3.5 rounded-full shadow-sm" style={{ backgroundColor: region.color }}></div>
                      <span className="text-sm font-medium text-gray-700">{region.name}</span>
                    </div>
                    <span className="text-sm font-bold text-gray-800 bg-gray-100 px-2.5 py-1 rounded-lg">{region.value}%</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Alerts */}
            <div className="bg-white/90 backdrop-blur-xl rounded-2xl p-5 sm:p-6 shadow-lg border border-purple-100/50 hover:shadow-xl transition-shadow duration-300">
              <div className="mb-4">
                <h3 className="text-lg font-bold text-gray-800 mb-1">Recent Alerts</h3>
                <p className="text-xs text-gray-500">Latest weather notifications</p>
              </div>
              <div className="space-y-3">
                {alerts.length > 0 ? (
                  alerts.map((alert) => (
                    <div key={alert.id} className="flex items-start gap-3 p-3.5 rounded-xl bg-gradient-to-r from-gray-50 to-gray-100 hover:from-purple-50 hover:to-indigo-50 transition-all duration-200 border border-gray-100 hover:border-purple-200">
                      <div
                        className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 shadow-sm ${
                          alert.type === 'warning' 
                            ? 'bg-gradient-to-br from-yellow-100 to-yellow-200' 
                            : alert.type === 'info' 
                            ? 'bg-gradient-to-br from-blue-100 to-blue-200' 
                            : 'bg-gradient-to-br from-green-100 to-green-200'
                        }`}
                      >
                        {alert.type === 'warning' && <AlertTriangle className="w-4 h-4 text-yellow-600" />}
                        {alert.type === 'info' && <Eye className="w-4 h-4 text-blue-600" />}
                        {alert.type === 'success' && <CheckCircle className="w-4 h-4 text-green-600" />}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-800 leading-snug">{alert.message}</p>
                        <p className="text-xs text-gray-500 mt-1.5">{alert.time}</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-center py-6">
                    <CheckCircle className="w-10 h-10 text-gray-300 mx-auto mb-2" />
                    <p className="text-sm text-gray-500">No alerts at this time</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Weekly Overview */}
        <div className="mt-6 sm:mt-8">
          <div className="bg-white/90 backdrop-blur-xl rounded-2xl p-5 sm:p-6 shadow-lg border border-purple-100/50 hover:shadow-xl transition-shadow duration-300">
            <div className="mb-6">
              <h3 className="text-lg sm:text-xl font-bold text-gray-800 mb-1">Weekly Overview</h3>
              <p className="text-xs sm:text-sm text-gray-500">Temperature and rainfall trends over the week</p>
            </div>
            <div className="h-64 sm:h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={weeklyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis dataKey="day" stroke="#6B7280" fontSize={12} />
                  <YAxis stroke="#6B7280" fontSize={12} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(255, 255, 255, 0.95)',
                      border: '1px solid #D1D5DB',
                      borderRadius: '12px',
                      boxShadow: '0 10px 25px -3px rgba(0, 0, 0, 0.1)',
                    }}
                  />
                  <Bar dataKey="temp" fill="#8B5CF6" radius={[8, 8, 0, 0]} name="Temperature" />
                  <Bar dataKey="rainfall" fill="#06B6D4" radius={[8, 8, 0, 0]} name="Rainfall" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
