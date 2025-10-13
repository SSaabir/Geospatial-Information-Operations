import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  AlertTriangle, 
  Activity, 
  Eye, 
  Lock, 
  Users,
  TrendingUp,
  RefreshCw,
  Clock,
  MapPin,
  AlertCircle,
  CheckCircle,
  XCircle,
  Server,
  Database,
  Wifi,
  Globe,
  Filter,
  Download,
  Settings
} from 'lucide-react';

import { useAuth } from '../contexts/AuthContext';

const SecurityDashboard = () => {
  const { apiCall } = useAuth();
  const [securityData, setSecurityData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedTab, setSelectedTab] = useState('overview');
  const [timeRange, setTimeRange] = useState('24h');

  // Mock data for demonstration - replace with API calls
  const mockSecurityData = {
    overview: {
      total_incidents_24h: 12,
      critical_incidents: 2,
      high_incidents: 5,
      open_incidents: 8,
      system_health: "healthy",
      threat_score: 25,
      security_score: 94,
      active_threats: 3
    },
    recent_incidents: [
      {
        id: "SEC001",
        timestamp: "2025-09-30T14:30:00Z",
        title: "Unusual API Access Pattern",
        threat_level: "medium",
        category: "api_usage",
        status: "investigating",
        source: "192.168.1.105",
        description: "Multiple rapid API calls detected from single IP"
      },
      {
        id: "SEC002", 
        timestamp: "2025-09-30T13:15:00Z",
        title: "Failed Login Attempts",
        threat_level: "low",
        category: "authentication",
        status: "resolved",
        source: "203.94.87.12",
        description: "5 consecutive failed login attempts"
      },
      {
        id: "SEC003",
        timestamp: "2025-09-30T12:45:00Z",
        title: "Data Validation Anomaly",
        threat_level: "high",
        category: "data_integrity",
        status: "open",
        source: "Internal System",
        description: "Unexpected data format in climate dataset upload"
      },
      {
        id: "SEC004",
        timestamp: "2025-09-30T11:20:00Z",
        title: "Suspicious File Upload",
        threat_level: "critical",
        category: "file_upload",
        status: "blocked",
        source: "104.28.234.67",
        description: "Potentially malicious file upload attempt blocked"
      }
    ],
    metrics: {
      requests_per_hour: 1247,
      blocked_attempts: 23,
      data_processed_gb: 45.7,
      uptime_percentage: 99.97
    },
    threat_sources: [
      { country: "Unknown", count: 8, percentage: 35 },
      { country: "Russia", count: 5, percentage: 22 },
      { country: "China", count: 4, percentage: 17 },
      { country: "USA", count: 3, percentage: 13 },
      { country: "Brazil", count: 3, percentage: 13 }
    ]
  };

  useEffect(() => {
    fetchSecurityData();
  }, [timeRange]);

  const fetchSecurityData = async () => {
    setLoading(true);
    try {
      const [overviewData, incidentsData, threatsData] = await Promise.all([
        apiCall(`/security-dashboard/overview?time_range=${timeRange}`),
        apiCall('/security-dashboard/incidents?limit=20'),
        apiCall('/security-dashboard/threat-sources')
      ]);

      setSecurityData({
        overview: overviewData.overview,
        metrics: overviewData.metrics,
        recent_incidents: incidentsData.incidents || [],
        threat_sources: threatsData.threat_sources || []
      });
      setLoading(false);
    } catch (error) {
      console.error('Error fetching security data:', error);
      // Fallback to mock data on error
      setSecurityData(mockSecurityData);
      setLoading(false);
    }
  };

  const refreshData = async () => {
    setRefreshing(true);
    await fetchSecurityData();
    setRefreshing(false);
  };

  const getThreatLevelColor = (level) => {
    switch (level) {
      case 'critical': return 'text-red-600 bg-red-50 border-red-200';
      case 'high': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'resolved': return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'investigating': return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'blocked': return <XCircle className="w-4 h-4 text-red-500" />;
      case 'open': return <AlertCircle className="w-4 h-4 text-orange-500" />;
      default: return <Activity className="w-4 h-4 text-gray-500" />;
    }
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
            <div className="h-96 bg-gray-200 rounded-xl"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center space-x-3 mb-4 sm:mb-0">
            <div className="w-12 h-12 bg-gradient-to-r from-red-500 to-red-600 rounded-xl flex items-center justify-center">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-800">Security Dashboard</h1>
              <p className="text-gray-600">Real-time security monitoring and threat detection</p>
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
            
            <button className="btn btn-secondary">
              <Download className="w-4 h-4" />
              Export
            </button>
          </div>
        </div>

        {/* Security Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* System Health */}
          <div className="dashboard-card">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                  <Activity className="w-6 h-6 text-green-600" />
                </div>
                <span className="text-xs font-medium text-green-600 bg-green-100 px-2 py-1 rounded-full">
                  {securityData.overview.system_health.toUpperCase()}
                </span>
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-800">{securityData.overview.security_score}%</p>
                <p className="text-sm text-gray-600">Security Score</p>
              </div>
            </div>
          </div>

          {/* Active Incidents */}
          <div className="dashboard-card">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                  <AlertTriangle className="w-6 h-6 text-red-600" />
                </div>
                <TrendingUp className="w-5 h-5 text-red-500" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-800">{securityData.overview.open_incidents}</p>
                <p className="text-sm text-gray-600">Open Incidents</p>
              </div>
            </div>
          </div>

          {/* Threat Level */}
          <div className="dashboard-card">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                  <Eye className="w-6 h-6 text-orange-600" />
                </div>
                <span className="text-xs font-medium text-orange-600 bg-orange-100 px-2 py-1 rounded-full">
                  LOW
                </span>
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-800">{securityData.overview.threat_score}</p>
                <p className="text-sm text-gray-600">Threat Score</p>
              </div>
            </div>
          </div>

          {/* Data Protection */}
          <div className="dashboard-card">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Lock className="w-6 h-6 text-blue-600" />
                </div>
                <CheckCircle className="w-5 h-5 text-green-500" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-800">{securityData.metrics.uptime_percentage}%</p>
                <p className="text-sm text-gray-600">System Uptime</p>
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
                { id: 'incidents', label: 'Incidents', icon: AlertTriangle },
                { id: 'metrics', label: 'Metrics', icon: TrendingUp },
                { id: 'sources', label: 'Threat Sources', icon: Globe }
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
            {selectedTab === 'overview' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* System Metrics */}
                  <div className="bg-gray-50 rounded-xl p-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">System Metrics</h3>
                    <div className="space-y-4">
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Requests/Hour</span>
                        <span className="font-semibold">{securityData.metrics.requests_per_hour.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Blocked Attempts</span>
                        <span className="font-semibold text-red-600">{securityData.metrics.blocked_attempts}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Data Processed</span>
                        <span className="font-semibold">{securityData.metrics.data_processed_gb} GB</span>
                      </div>
                    </div>
                  </div>

                  {/* Quick Stats */}
                  <div className="bg-purple-50 rounded-xl p-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Security Summary</h3>
                    <div className="space-y-4">
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Critical Incidents</span>
                        <span className="font-semibold text-red-600">{securityData.overview.critical_incidents}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">High Priority</span>
                        <span className="font-semibold text-orange-600">{securityData.overview.high_incidents}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-gray-600">Total 24h</span>
                        <span className="font-semibold">{securityData.overview.total_incidents_24h}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {selectedTab === 'incidents' && (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-semibold text-gray-800">Recent Security Incidents</h3>
                  <div className="flex space-x-2">
                    <button className="btn btn-ghost text-xs">
                      <Filter className="w-4 h-4" />
                      Filter
                    </button>
                  </div>
                </div>
                
                <div className="space-y-3">
                  {securityData.recent_incidents.map((incident) => (
                    <div key={incident.id} className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-3 mb-2">
                            {getStatusIcon(incident.status)}
                            <h4 className="font-medium text-gray-800">{incident.title}</h4>
                            <span className={`text-xs px-2 py-1 rounded-full border ${getThreatLevelColor(incident.threat_level)}`}>
                              {incident.threat_level.toUpperCase()}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 mb-2">{incident.description}</p>
                          <div className="flex items-center space-x-4 text-xs text-gray-500">
                            <span className="flex items-center space-x-1">
                              <Clock className="w-3 h-3" />
                              <span>{new Date(incident.timestamp).toLocaleString()}</span>
                            </span>
                            <span className="flex items-center space-x-1">
                              <MapPin className="w-3 h-3" />
                              <span>{incident.source}</span>
                            </span>
                            <span className="capitalize">{incident.category.replace('_', ' ')}</span>
                          </div>
                        </div>
                        <div className="flex flex-col items-end space-y-2">
                          <span className="text-xs font-medium text-gray-500">#{incident.id}</span>
                          <button className="text-xs text-purple-600 hover:text-purple-700">
                            View Details
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {selectedTab === 'metrics' && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-blue-50 rounded-xl p-6 text-center">
                  <Server className="w-8 h-8 text-blue-600 mx-auto mb-3" />
                  <p className="text-2xl font-bold text-blue-900">{securityData.metrics.requests_per_hour}</p>
                  <p className="text-sm text-blue-700">Requests/Hour</p>
                </div>
                <div className="bg-red-50 rounded-xl p-6 text-center">
                  <AlertTriangle className="w-8 h-8 text-red-600 mx-auto mb-3" />
                  <p className="text-2xl font-bold text-red-900">{securityData.metrics.blocked_attempts}</p>
                  <p className="text-sm text-red-700">Blocked Attempts</p>
                </div>
                <div className="bg-green-50 rounded-xl p-6 text-center">
                  <Database className="w-8 h-8 text-green-600 mx-auto mb-3" />
                  <p className="text-2xl font-bold text-green-900">{securityData.metrics.data_processed_gb}</p>
                  <p className="text-sm text-green-700">GB Processed</p>
                </div>
                <div className="bg-purple-50 rounded-xl p-6 text-center">
                  <Wifi className="w-8 h-8 text-purple-600 mx-auto mb-3" />
                  <p className="text-2xl font-bold text-purple-900">{securityData.metrics.uptime_percentage}%</p>
                  <p className="text-sm text-purple-700">Uptime</p>
                </div>
              </div>
            )}

            {selectedTab === 'sources' && (
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-800">Threat Sources by Country</h3>
                <div className="space-y-3">
                  {securityData.threat_sources.map((source, index) => (
                    <div key={index} className="flex items-center justify-between bg-gray-50 rounded-lg p-4">
                      <div className="flex items-center space-x-3">
                        <Globe className="w-5 h-5 text-gray-500" />
                        <span className="font-medium text-gray-800">{source.country}</span>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-2">
                          <div className="w-32 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-red-500 h-2 rounded-full" 
                              style={{ width: `${source.percentage}%` }}
                            ></div>
                          </div>
                          <span className="text-sm text-gray-600">{source.percentage}%</span>
                        </div>
                        <span className="font-semibold text-gray-800 w-8 text-right">{source.count}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SecurityDashboard;