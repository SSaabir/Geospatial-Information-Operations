import React, { useEffect, useState } from 'react';
import { 
  BarChart3, 
  FileText, 
  Activity, 
  Download, 
  TrendingUp, 
  Users, 
  Clock,
  RefreshCw,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export default function Analytics() {
  const { apiCall, user } = useAuth();
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedTab, setSelectedTab] = useState('overview');
  const [timeRange, setTimeRange] = useState('24h');

  useEffect(() => {
    fetchAnalyticsData();
  }, [timeRange]);

  const fetchAnalyticsData = async () => {
    setLoading(true);
    try {
      if (user?.is_admin) {
        // Admin view - fetch full dashboard data
        const [overviewData, apiUsageData, userActivityData, topEndpointsData] = await Promise.all([
          apiCall('/analytics-dashboard/overview'),
          apiCall(`/analytics-dashboard/api-usage?time_range=${timeRange}`),
          apiCall('/analytics-dashboard/user-activity'),
          apiCall('/analytics-dashboard/top-endpoints?limit=10')
        ]);

        setAnalyticsData({
          overview: overviewData.overview,
          api_usage: apiUsageData.api_usage || [],
          user_activity: userActivityData.user_activity,
          top_endpoints: topEndpointsData.top_endpoints || []
        });
      } else {
        // Regular user view - fetch personal usage
        const data = await apiCall('/analytics/usage');
        setAnalyticsData({ userMetrics: data });
      }
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch analytics data:', error);
      setLoading(false);
    }
  };

  const refreshData = async () => {
    setRefreshing(true);
    await fetchAnalyticsData();
    setRefreshing(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-gray-200 rounded w-1/4"></div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-32 bg-gray-200 rounded-xl"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Admin Dashboard View
  if (user?.is_admin && analyticsData?.overview) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-50 p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center space-x-3 mb-4 sm:mb-0">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-800">Analytics Dashboard</h1>
                <p className="text-gray-600">Platform usage and performance metrics</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <select 
                value={timeRange} 
                onChange={(e) => setTimeRange(e.target.value)}
                className="form-input w-auto"
              >
                <option value="1h">Last Hour</option>
                <option value="24h">Last 24 Hours</option>
                <option value="7d">Last 7 Days</option>
                <option value="30d">Last 30 Days</option>
              </select>
              
              <button
                onClick={refreshData}
                disabled={refreshing}
                className="btn btn-ghost"
              >
                <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
                Refresh
              </button>
            </div>
          </div>

          {/* Overview Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="dashboard-card">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <Activity className="w-6 h-6 text-blue-600" />
                  </div>
                  <TrendingUp className="w-5 h-5 text-green-500" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-800">{analyticsData.overview.total_api_calls.toLocaleString()}</p>
                  <p className="text-sm text-gray-600">Total API Calls</p>
                  <p className="text-xs text-green-600 mt-1">+{analyticsData.overview.api_calls_24h} in 24h</p>
                </div>
              </div>
            </div>

            <div className="dashboard-card">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                    <Users className="w-6 h-6 text-purple-600" />
                  </div>
                  <CheckCircle className="w-5 h-5 text-green-500" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-800">{analyticsData.overview.active_users_7d}</p>
                  <p className="text-sm text-gray-600">Active Users (7d)</p>
                  <p className="text-xs text-gray-500 mt-1">of {analyticsData.overview.total_users} total</p>
                </div>
              </div>
            </div>

            <div className="dashboard-card">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <FileText className="w-6 h-6 text-green-600" />
                  </div>
                  <TrendingUp className="w-5 h-5 text-green-500" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-800">{analyticsData.overview.reports_generated}</p>
                  <p className="text-sm text-gray-600">Reports Generated</p>
                  <p className="text-xs text-gray-500 mt-1">Last 30 days</p>
                </div>
              </div>
            </div>

            <div className="dashboard-card">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                    <Clock className="w-6 h-6 text-orange-600" />
                  </div>
                  <CheckCircle className="w-5 h-5 text-green-500" />
                </div>
                <div>
                  <p className="text-2xl font-bold text-gray-800">{analyticsData.overview.avg_response_time}ms</p>
                  <p className="text-sm text-gray-600">Avg Response Time</p>
                  <p className="text-xs text-green-600 mt-1">Excellent</p>
                </div>
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="bg-white rounded-xl shadow-lg border border-gray-100">
            <div className="border-b border-gray-200">
              <nav className="flex space-x-8 px-6">
                {[
                  { id: 'overview', label: 'Overview', icon: Activity },
                  { id: 'endpoints', label: 'Top Endpoints', icon: BarChart3 },
                  { id: 'users', label: 'User Activity', icon: Users }
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setSelectedTab(tab.id)}
                    className={`flex items-center space-x-2 py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                      selectedTab === tab.id
                        ? 'border-purple-500 text-purple-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <tab.icon className="w-4 h-4" />
                    <span>{tab.label}</span>
                  </button>
                ))}
              </nav>
            </div>

            <div className="p-6">
              {selectedTab === 'overview' && analyticsData.api_usage && (
                <div className="space-y-6">
                  <h3 className="text-lg font-semibold text-gray-800">API Usage Over Time</h3>
                  <div className="space-y-2">
                    {analyticsData.api_usage.map((item, index) => (
                      <div key={index} className="flex items-center justify-between bg-gray-50 rounded-lg p-4">
                        <span className="text-sm font-medium text-gray-700">{item.time}</span>
                        <div className="flex items-center space-x-4">
                          <div className="w-48 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-blue-500 h-2 rounded-full" 
                              style={{ width: `${Math.min(100, (item.count / Math.max(...analyticsData.api_usage.map(i => i.count))) * 100)}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-semibold text-gray-800 w-16 text-right">{item.count}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {selectedTab === 'endpoints' && analyticsData.top_endpoints && (
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-800">Most Accessed Endpoints</h3>
                  <div className="space-y-3">
                    {analyticsData.top_endpoints.map((endpoint, index) => (
                      <div key={index} className="bg-gray-50 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium text-gray-800">{endpoint.endpoint}</span>
                          <span className="text-sm font-semibold text-purple-600">{endpoint.total_calls.toLocaleString()} calls</span>
                        </div>
                        <div className="flex items-center justify-between text-xs text-gray-600">
                          <span>Avg Response: {endpoint.avg_response_time}ms</span>
                          <div className="w-32 bg-gray-200 rounded-full h-1.5">
                            <div 
                              className="bg-purple-500 h-1.5 rounded-full" 
                              style={{ width: `${Math.min(100, (endpoint.total_calls / analyticsData.top_endpoints[0].total_calls) * 100)}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {selectedTab === 'users' && analyticsData.user_activity && (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-800 mb-4">Users by Tier</h3>
                      <div className="space-y-3">
                        {Object.entries(analyticsData.user_activity.users_by_tier || {}).map(([tier, count]) => (
                          <div key={tier} className="flex items-center justify-between bg-gray-50 rounded-lg p-4">
                            <span className="font-medium text-gray-800 capitalize">{tier}</span>
                            <span className="text-lg font-bold text-purple-600">{count}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-800 mb-4">Registration Trend</h3>
                      <div className="text-center py-8 bg-gray-50 rounded-lg">
                        <p className="text-gray-600">
                          {analyticsData.user_activity.registrations?.length || 0} new users in last 30 days
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Regular User View
  const metrics = analyticsData?.userMetrics || {};
  return (
    <div className="min-h-screen w-full p-6" style={{ background: 'linear-gradient(135deg, #F5EFFF 0%, #E5D9F2 50%, #CDC1FF 100%)' }}>
      <div className="w-full max-w-6xl mx-auto bg-white rounded-2xl shadow-xl p-6">
        <h1 className="text-3xl font-bold mb-6">My Usage Analytics</h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="p-4 rounded-lg border" style={{ borderColor: '#E5D9F2' }}>
            <Activity className="w-5 h-5 inline-block mr-2" /> API Calls
            <div className="text-2xl font-bold mt-2">{metrics.api_calls || 0}</div>
            <div className="text-sm text-gray-500 mt-1">
              {metrics.limit === Infinity ? 'Unlimited' : `${metrics.remaining || 0} remaining of ${metrics.limit || 0}`}
            </div>
            {metrics.remaining === 0 && metrics.limit !== Infinity && (
              <div className="text-xs text-red-500 mt-1">Limit reached - upgrade to continue</div>
            )}
          </div>
          <div className="p-4 rounded-lg border" style={{ borderColor: '#E5D9F2' }}>
            <FileText className="w-5 h-5 inline-block mr-2" /> Reports Generated
            <div className="text-2xl font-bold mt-2">{metrics.reports_generated || 0}</div>
          </div>
          <div className="p-4 rounded-lg border" style={{ borderColor: '#E5D9F2' }}>
            <Download className="w-5 h-5 inline-block mr-2" /> Data Downloads
            <div className="text-2xl font-bold mt-2">{metrics.data_downloads || 0}</div>
          </div>
        </div>

        <div className="p-6 rounded-lg border bg-blue-50" style={{ borderColor: '#E5D9F2' }}>
          <AlertCircle className="w-5 h-5 inline-block mr-2 text-blue-600" />
          <span className="font-semibold text-blue-900">Upgrade to Professional</span>
          <p className="text-sm text-blue-700 mt-2">Get access to advanced analytics, unlimited API calls, and premium features.</p>
        </div>
      </div>
    </div>
  );
}



