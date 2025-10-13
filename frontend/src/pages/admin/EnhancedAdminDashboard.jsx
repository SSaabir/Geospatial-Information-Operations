import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { Users, Database, Server, Activity, TrendingUp, AlertCircle, Shield, Settings, Eye, Download, RefreshCw, Filter, Search, MoreVertical, UserCheck, UserX, Globe, Brain, Lock, BarChart3, Bell, CheckCircle, Info, AlertTriangle } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import SecurityDashboard from '../SecurityDashboard';
import AIEthicsDashboard from '../AIEthicsDashboard';
import Analytics from '../Analytics';
import AddAdminPanel from '../../components/AddAdminPanel';

export default function EnhancedAdminDashboard() {
  const { user, isAuthenticated, apiCall } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');
  const [dashboardStats, setDashboardStats] = useState(null);
  const [recentUsers, setRecentUsers] = useState([]);
  const [userActivity, setUserActivity] = useState([]);
  const [systemAlerts, setSystemAlerts] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(true);

  console.log('🎯 EnhancedAdminDashboard RENDERING', { user, isAuthenticated, activeTab });

  // Fetch dashboard data
  useEffect(() => {
    fetchDashboardData();
  }, [selectedTimeRange]);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      // Fetch all data in parallel
      const [statsResponse, usersResponse, activityResponse, alertsResponse, notificationsResponse] = await Promise.all([
        apiCall('/admin/dashboard/stats'),
        apiCall('/admin/dashboard/users/recent?limit=10'),
        apiCall('/admin/dashboard/activity'),
        apiCall('/admin/dashboard/alerts?limit=10'),
        apiCall('/admin/dashboard/notifications?limit=20')
      ]);

      setDashboardStats(statsResponse);
      setRecentUsers(usersResponse.users || []);
      setUserActivity(activityResponse.activity || []);
      setSystemAlerts(alertsResponse.alerts || []);
      setNotifications(notificationsResponse.notifications || []);
      setUnreadCount(notificationsResponse.unread_count || 0);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Admin dashboard data - mock for now, will be replaced with real data
  const systemStats = dashboardStats ? [
    { name: 'Total Users', value: dashboardStats.total_users, color: '#8B5CF6', status: 'normal', unit: '' },
    { name: 'Active Users', value: dashboardStats.active_users, color: '#06B6D4', status: 'normal', unit: '' },
    { name: 'Security Alerts', value: dashboardStats.security_alerts, color: '#F59E0B', status: dashboardStats.security_alerts > 5 ? 'warning' : 'normal', unit: '' },
    { name: 'Incidents', value: dashboardStats.security_incidents, color: '#EF4444', status: dashboardStats.security_incidents > 0 ? 'high' : 'normal', unit: '' }
  ] : [
    { name: 'Loading...', value: 0, color: '#8B5CF6', status: 'normal', unit: '' },
    { name: 'Loading...', value: 0, color: '#06B6D4', status: 'normal', unit: '' },
    { name: 'Loading...', value: 0, color: '#10B981', status: 'normal', unit: '' },
    { name: 'Loading...', value: 0, color: '#F59E0B', status: 'normal', unit: '' }
  ];

  // Keep mock data for data sources (will be implemented later)
  const dataSourceStats = [
    { source: 'Weather Stations', count: 45, status: 'online', lastSync: '2 min ago' },
    { source: 'Satellite Data', count: 12, status: 'online', lastSync: '5 min ago' },
    { source: 'Radar Systems', count: 8, status: 'warning', lastSync: '15 min ago' },
    { source: 'IoT Sensors', count: 234, status: 'online', lastSync: '1 min ago' }
  ];

  // Check admin access using is_admin boolean field (not role)
  if (!isAuthenticated || !user?.is_admin) {
    console.log('❌ EnhancedAdminDashboard - Access check failed:', { 
      isAuthenticated, 
      'user?.is_admin': user?.is_admin,
      'user?.role (does not exist)': user?.role 
    });
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

  console.log('✅ EnhancedAdminDashboard - Access granted, rendering dashboard');

  // Tab configuration
  const tabs = [
    { id: 'overview', label: 'System Overview', icon: Activity },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'ai-ethics', label: 'AI Ethics', icon: Brain },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 }
  ];

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
                System monitoring, security, AI ethics, and analytics console
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <AddAdminPanel />
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

        {/* Tab Navigation */}
        <div className="bg-white rounded-xl shadow-lg mb-6 border border-purple-100">
          <div className="flex overflow-x-auto">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-6 py-4 border-b-2 font-medium transition-all whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-purple-600 text-purple-600 bg-purple-50'
                    : 'border-transparent text-gray-600 hover:text-purple-600 hover:bg-purple-50'
                }`}
              >
                <tab.icon className="w-5 h-5" />
                <span>{tab.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* System Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {systemStats.map((stat, index) => (
                <div key={index} className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-purple-100">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-gray-600 text-sm font-medium">{stat.name}</h3>
                    <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                      stat.status === 'normal' ? 'bg-green-100 text-green-700' :
                      stat.status === 'warning' ? 'bg-yellow-100 text-yellow-700' :
                      'bg-red-100 text-red-700'
                    }`}>
                      {stat.status}
                    </div>
                  </div>
                  <div className="flex items-end justify-between">
                    <div>
                      <p className="text-3xl font-bold text-gray-800">{stat.value}{stat.unit || ''}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* User Activity Chart */}
              <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-purple-100">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">User Activity</h3>
                <ResponsiveContainer width="100%" height={250}>
                  <AreaChart data={userActivity}>
                    <defs>
                      <linearGradient id="colorActive" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0.1}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                    <XAxis dataKey="time" stroke="#6B7280" />
                    <YAxis stroke="#6B7280" />
                    <Tooltip />
                    <Area 
                      type="monotone" 
                      dataKey="active" 
                      stroke="#8B5CF6" 
                      fillOpacity={1} 
                      fill="url(#colorActive)" 
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              {/* System Alerts */}
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
              
              {/* Notifications */}
              <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-purple-100">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-800">Recent Notifications</h3>
                  <div className="flex items-center space-x-2">
                    <Bell className="w-5 h-5 text-purple-600" />
                    {unreadCount > 0 && (
                      <span className="px-2 py-0.5 text-xs font-medium bg-red-100 text-red-600 rounded-full">
                        {unreadCount} new
                      </span>
                    )}
                  </div>
                </div>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {notifications.length === 0 ? (
                    <div className="text-center py-8 text-gray-400">
                      <Bell className="w-12 h-12 mx-auto mb-2 opacity-30" />
                      <p className="text-sm">No notifications</p>
                    </div>
                  ) : (
                    notifications.map((notification) => (
                      <div 
                        key={notification.id} 
                        className={`flex items-start space-x-3 p-3 rounded-xl ${
                          notification.read ? 'bg-gray-50' : 'bg-purple-50 border border-purple-100'
                        }`}
                      >
                        <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${
                          notification.level === 'critical' || notification.level === 'error' ? 'bg-red-100' :
                          notification.level === 'warning' ? 'bg-yellow-100' :
                          notification.level === 'success' ? 'bg-green-100' : 'bg-blue-100'
                        }`}>
                          {notification.level === 'critical' || notification.level === 'error' ? (
                            <AlertCircle className="w-3 h-3 text-red-600" />
                          ) : notification.level === 'warning' ? (
                            <AlertTriangle className="w-3 h-3 text-yellow-600" />
                          ) : notification.level === 'success' ? (
                            <CheckCircle className="w-3 h-3 text-green-600" />
                          ) : (
                            <Info className="w-3 h-3 text-blue-600" />
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between">
                            <p className="text-sm font-medium text-gray-800">{notification.subject}</p>
                            {notification.is_system_wide && (
                              <span className="ml-2 px-2 py-0.5 text-xs bg-purple-100 text-purple-600 rounded-full flex-shrink-0">
                                System
                              </span>
                            )}
                          </div>
                          <p className="text-xs text-gray-600 mt-1">{notification.message}</p>
                          <div className="flex items-center justify-between mt-2">
                            <p className="text-xs text-gray-500">
                              {notification.username !== 'System' && `User: ${notification.username} • `}
                              {new Date(notification.timestamp).toLocaleString('en-US', { 
                                month: 'short', 
                                day: 'numeric', 
                                hour: '2-digit', 
                                minute: '2-digit' 
                              })}
                            </p>
                            {!notification.read && (
                              <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>

            {/* Data Sources & Users Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Data Sources Status */}
              <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-purple-100">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-800">Data Sources</h3>
                  <Database className="w-5 h-5 text-purple-600" />
                </div>
                <div className="space-y-3">
                  {dataSourceStats.map((source, index) => (
                    <div key={index} className="flex items-center justify-between p-3 rounded-xl hover:bg-gray-50 transition-colors">
                      <div className="flex items-center space-x-3">
                        <div className={`w-2 h-2 rounded-full ${
                          source.status === 'online' ? 'bg-green-500' :
                          source.status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
                        }`}></div>
                        <div>
                          <p className="text-sm font-medium text-gray-800">{source.source}</p>
                          <p className="text-xs text-gray-500">{source.count} active</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-gray-500">{source.lastSync}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recent Users */}
              <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-purple-100">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-800">Recent Users</h3>
                  <Users className="w-5 h-5 text-purple-600" />
                </div>
                <div className="space-y-3">
                  {recentUsers.map((user) => (
                    <div key={user.id} className="flex items-center justify-between p-3 rounded-xl hover:bg-gray-50 transition-colors">
                      <div className="flex items-center space-x-3">
                        <div className={`w-8 h-8 ${user.status === 'online' ? 'bg-gradient-to-r from-green-400 to-emerald-500' : 'bg-gradient-to-r from-purple-400 to-indigo-500'} rounded-lg flex items-center justify-center`}>
                          <span className="text-white font-medium text-xs">
                            {user.username ? user.username.substring(0, 2).toUpperCase() : '??'}
                          </span>
                        </div>
                        <div>
                          <p className="font-medium text-gray-800">{user.username || 'Unknown'}</p>
                          <p className="text-sm text-gray-600">{user.tier || 'free'} {user.is_admin && '• Admin'}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-gray-500">
                          {user.last_login ? new Date(user.last_login).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : 'Never'}
                        </p>
                        <div className="flex justify-end mt-1">
                          <span className={`text-xs px-2 py-0.5 rounded-full ${user.status === 'online' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
                            {user.status || 'offline'}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Security Tab */}
        {activeTab === 'security' && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <SecurityDashboard />
          </div>
        )}

        {/* AI Ethics Tab */}
        {activeTab === 'ai-ethics' && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <AIEthicsDashboard />
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div className="bg-white rounded-xl shadow-lg p-6">
            <Analytics />
          </div>
        )}
      </div>
    </div>
  );
}
