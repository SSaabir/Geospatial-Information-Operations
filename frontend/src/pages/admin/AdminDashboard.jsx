import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { Users, Database, Server, Activity, TrendingUp, AlertCircle, Shield, Settings, Eye, Download, RefreshCw, Filter, Search, MoreVertical, UserCheck, UserX, Globe } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

export default function AdminDashboard() {
  const { user, isAuthenticated } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');

  // Admin dashboard data
  const systemStats = [
    { name: 'CPU Usage', value: 65, color: '#8B5CF6', status: 'normal' },
    { name: 'Memory', value: 78, color: '#06B6D4', status: 'warning' },
    { name: 'Storage', value: 45, color: '#10B981', status: 'normal' },
    { name: 'Network', value: 89, color: '#F59E0B', status: 'high' }
  ];

  const userActivityData = [
    { time: '00:00', active: 12, total: 150 },
    { time: '04:00', active: 8, total: 150 },
    { time: '08:00', active: 45, total: 150 },
    { time: '12:00', active: 89, total: 150 },
    { time: '16:00', active: 134, total: 150 },
    { time: '20:00', active: 67, total: 150 }
  ];

  const dataSourceStats = [
    { source: 'Weather Stations', count: 45, status: 'online', lastSync: '2 min ago' },
    { source: 'Satellite Data', count: 12, status: 'online', lastSync: '5 min ago' },
    { source: 'Radar Systems', count: 8, status: 'warning', lastSync: '15 min ago' },
    { source: 'IoT Sensors', count: 234, status: 'online', lastSync: '1 min ago' }
  ];

  const recentUsers = [
    { id: 1, name: 'John Smith', email: 'john@example.com', role: 'User', lastActive: '2 min ago', status: 'online' },
    { id: 2, name: 'Sarah Johnson', email: 'sarah@example.com', role: 'Analyst', lastActive: '5 min ago', status: 'online' },
    { id: 3, name: 'Mike Chen', email: 'mike@example.com', role: 'User', lastActive: '1 hour ago', status: 'offline' },
    { id: 4, name: 'Emily Davis', email: 'emily@example.com', role: 'Admin', lastActive: 'Active now', status: 'online' }
  ];

  const systemAlerts = [
    { id: 1, type: 'critical', message: 'High server load detected on Node-3', time: '5 min ago' },
    { id: 2, type: 'warning', message: 'Data sync delay from Kandy weather station', time: '12 min ago' },
    { id: 3, type: 'info', message: 'System backup completed successfully', time: '1 hour ago' },
    { id: 4, type: 'warning', message: 'Storage usage above 80% threshold', time: '2 hours ago' }
  ];

  if (!isAuthenticated || user?.role !== 'admin') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-50 flex items-center justify-center" style={{backgroundColor: '#F5EFFF'}}>
        <div className="text-center p-8">
          <Shield className="w-16 h-16 text-red-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Access Denied</h2>
          <p className="text-gray-600 mb-6">You need administrator privileges to access this page.</p>
          <a
            href="/dashboard"
            className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl hover:from-purple-700 hover:to-indigo-700 transition-all duration-200"
          >
            Go to User Dashboard
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-50" style={{backgroundColor: '#F5EFFF'}}>
      <div className="container mx-auto px-4 py-8">
        {/* Admin Header */}
        <div className="mb-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
            <div className="mb-4 lg:mb-0">
              <div className="flex items-center space-x-3 mb-2">
                <div className="w-10 h-10 bg-gradient-to-r from-red-500 to-pink-600 rounded-xl flex items-center justify-center">
                  <Shield className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                    Admin Dashboard
                  </h1>
                  <p className="text-red-600 text-sm font-medium">Administrator Access</p>
                </div>
              </div>
              <p className="text-gray-600">
                System monitoring and management console
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <select 
                value={selectedTimeRange}
                onChange={(e) => setSelectedTimeRange(e.target.value)}
                className="px-4 py-2 border border-purple-200 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white"
              >
                <option value="1h">Last Hour</option>
                <option value="24h">Last 24 Hours</option>
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
              </select>
              <button className="flex items-center space-x-2 px-4 py-2 bg-white border border-purple-200 rounded-xl hover:bg-purple-50 transition-colors">
                <RefreshCw className="w-4 h-4" />
                <span>Refresh</span>
              </button>
            </div>
          </div>
        </div>

        {/* System Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-purple-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Users</p>
                <p className="text-2xl font-bold text-gray-800">1,247</p>
                <p className="text-green-600 text-xs flex items-center mt-1">
                  <TrendingUp className="w-3 h-3 mr-1" /> +12% this month
                </p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-cyan-600 rounded-xl flex items-center justify-center">
                <Users className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>

          <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-purple-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Data Sources</p>
                <p className="text-2xl font-bold text-gray-800">299</p>
                <p className="text-yellow-600 text-xs flex items-center mt-1">
                  <AlertCircle className="w-3 h-3 mr-1" /> 3 offline
                </p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl flex items-center justify-center">
                <Database className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>

          <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-purple-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Server Load</p>
                <p className="text-2xl font-bold text-gray-800">68%</p>
                <p className="text-gray-600 text-xs flex items-center mt-1">
                  <Activity className="w-3 h-3 mr-1" /> Normal range
                </p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-indigo-600 rounded-xl flex items-center justify-center">
                <Server className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>

          <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-purple-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Active Sessions</p>
                <p className="text-2xl font-bold text-gray-800">89</p>
                <p className="text-green-600 text-xs flex items-center mt-1">
                  <UserCheck className="w-3 h-3 mr-1" /> Peak: 134
                </p>
              </div>
              <div className="w-12 h-12 bg-gradient-to-r from-orange-500 to-red-600 rounded-xl flex items-center justify-center">
                <Globe className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          {/* System Performance Chart */}
          <div className="lg:col-span-2">
            <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-purple-100">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-semibold text-gray-800">System Performance</h3>
                <div className="flex space-x-2">
                  {systemStats.map((stat, index) => (
                    <div key={index} className="flex items-center space-x-2">
                      <div 
                        className="w-3 h-3 rounded-full" 
                        style={{ backgroundColor: stat.color }}
                      ></div>
                      <span className="text-xs text-gray-600">{stat.name}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={systemStats.map((stat, index) => ({ 
                    name: stat.name, 
                    value: stat.value,
                    time: index * 2 
                  }))}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                    <XAxis dataKey="name" stroke="#6B7280" fontSize={12} />
                    <YAxis stroke="#6B7280" fontSize={12} />
                    <Tooltip 
                      contentStyle={{
                        backgroundColor: 'white',
                        border: '1px solid #D1D5DB',
                        borderRadius: '12px',
                        boxShadow: '0 10px 25px -3px rgba(0, 0, 0, 0.1)'
                      }}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="value" 
                      stroke="#8B5CF6" 
                      strokeWidth={3}
                      dot={{ fill: '#8B5CF6', strokeWidth: 2, r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* System Alerts */}
          <div className="space-y-6">
            <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-purple-100">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">System Alerts</h3>
              <div className="space-y-3">
                {systemAlerts.map((alert) => (
                  <div key={alert.id} className="flex items-start space-x-3 p-3 rounded-xl bg-gray-50">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${
                      alert.type === 'critical' ? 'bg-red-100' :
                      alert.type === 'warning' ? 'bg-yellow-100' : 'bg-blue-100'
                    }`}>
                      <AlertCircle className={`w-3 h-3 ${
                        alert.type === 'critical' ? 'text-red-600' :
                        alert.type === 'warning' ? 'text-yellow-600' : 'text-blue-600'
                      }`} />
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

        {/* Data Sources & Users Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Data Sources Status */}
          <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-purple-100">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-gray-800">Data Sources</h3>
              <button className="flex items-center space-x-2 px-3 py-1 text-sm bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors">
                <Settings className="w-4 h-4" />
                <span>Manage</span>
              </button>
            </div>
            <div className="space-y-4">
              {dataSourceStats.map((source, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${
                      source.status === 'online' ? 'bg-green-500' : 
                      source.status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
                    }`}></div>
                    <div>
                      <p className="font-medium text-gray-800">{source.source}</p>
                      <p className="text-sm text-gray-600">{source.count} active</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-500">Last sync</p>
                    <p className="text-sm font-medium text-gray-700">{source.lastSync}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Users */}
          <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-purple-100">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-gray-800">Recent Users</h3>
              <button className="flex items-center space-x-2 px-3 py-1 text-sm bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors">
                <Eye className="w-4 h-4" />
                <span>View All</span>
              </button>
            </div>
            <div className="space-y-3">
              {recentUsers.map((user) => (
                <div key={user.id} className="flex items-center justify-between p-3 rounded-xl hover:bg-gray-50 transition-colors">
                  <div className="flex items-center space-x-3">
                    <div className="relative">
                      <div className="w-10 h-10 bg-gradient-to-r from-purple-400 to-indigo-500 rounded-xl flex items-center justify-center">
                        <span className="text-white font-medium text-sm">
                          {user.name.split(' ').map(n => n[0]).join('')}
                        </span>
                      </div>
                      <div className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-white ${
                        user.status === 'online' ? 'bg-green-400' : 'bg-gray-400'
                      }`}></div>
                    </div>
                    <div>
                      <p className="font-medium text-gray-800">{user.name}</p>
                      <p className="text-sm text-gray-600">{user.role}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-500">{user.lastActive}</p>
                    <div className="flex justify-end mt-1">
                      <button className="p-1 hover:bg-gray-200 rounded">
                        <MoreVertical className="w-4 h-4 text-gray-400" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}