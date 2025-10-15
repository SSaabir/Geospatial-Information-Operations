import React, { useState, useEffect } from 'react';
import {
  Brain,
  Scale,
  Eye,
  AlertTriangle,
  CheckCircle,
  BarChart3,
  TrendingUp,
  RefreshCw,
  FileText,
  Shield,
  Users,
  Clock,
  Target,
  Award
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const AIEthicsDashboard = () => {
  const { apiCall } = useAuth();
  const [ethicsData, setEthicsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedTab, setSelectedTab] = useState('overview');

  // Mock data for demonstration - replace with API calls
  const mockEthicsData = {
    overview: {
      overall_ethics_score: 8.7,
      models_monitored: 5,
      bias_alerts_24h: 3,
      fairness_compliance: 94.2,
      transparency_score: 9.1
    },
    bias_detection: {
      geographical_bias: [
        {
          location: "Urban Areas",
          bias_score: 0.12,
          severity: "low",
          affected_predictions: 245
        },
        {
          location: "Rural Areas", 
          bias_score: 0.34,
          severity: "medium",
          affected_predictions: 89
        },
        {
          location: "Coastal Regions",
          bias_score: 0.08,
          severity: "low",
          affected_predictions: 156
        }
      ],
      temporal_bias: [
        {
          time_period: "Morning (6-12)",
          bias_score: 0.09,
          severity: "low"
        },
        {
          time_period: "Afternoon (12-18)",
          bias_score: 0.15,
          severity: "low"
        },
        {
          time_period: "Evening (18-24)",
          bias_score: 0.28,
          severity: "medium"
        },
        {
          time_period: "Night (0-6)",
          bias_score: 0.41,
          severity: "high"
        }
      ]
    },
    fairness_metrics: {
      demographic_parity: {
        score: 0.89,
        threshold: 0.8,
        status: "compliant"
      },
      equal_opportunity: {
        score: 0.92,
        threshold: 0.85,
        status: "compliant"
      },
      prediction_equity: {
        score: 0.87,
        threshold: 0.8,
        status: "compliant"
      }
    },
    model_assessments: [
      {
        model_name: "WeatherPredictor_v2.1",
        ethics_score: 8.9,
        last_assessment: "2025-09-30T10:30:00Z",
        status: "compliant",
        issues: []
      },
      {
        model_name: "TrendAnalyzer_v1.5",
        ethics_score: 8.5,
        last_assessment: "2025-09-30T09:15:00Z", 
        status: "review_needed",
        issues: ["Temporal bias in night predictions"]
      },
      {
        model_name: "AlertSystem_v3.0",
        ethics_score: 9.2,
        last_assessment: "2025-09-30T08:45:00Z",
        status: "compliant",
        issues: []
      }
    ],
    transparency_reports: [
      {
        id: "TR_20250930_001",
        model: "WeatherPredictor_v2.1",
        generated: "2025-09-30T14:00:00Z",
        explainability_score: 9.1,
        data_sources: ["Satellite Data", "Weather Stations", "IoT Sensors"],
        key_features: ["Temperature", "Humidity", "Pressure", "Wind Speed"]
      },
      {
        id: "TR_20250930_002", 
        model: "TrendAnalyzer_v1.5",
        generated: "2025-09-30T13:30:00Z",
        explainability_score: 8.7,
        data_sources: ["Historical Data", "Real-time Feeds"],
        key_features: ["Historical Patterns", "Seasonal Trends", "Anomalies"]
      }
    ]
  };

  useEffect(() => {
    fetchEthicsData();
    const interval = setInterval(() => {
      refreshData();
    }, 60000); // Refresh every minute

    return () => clearInterval(interval);
  }, []);

  const fetchEthicsData = async () => {
    try {
      const [overviewData, biasData, fairnessData, reportsData, assessmentsData] = await Promise.all([
        apiCall('/ai-ethics-dashboard/overview'),
        apiCall('/ai-ethics-dashboard/bias-detection'),
        apiCall('/ai-ethics-dashboard/fairness-metrics'),
        apiCall('/ai-ethics-dashboard/recent-reports?limit=10'),
        apiCall('/ai-ethics-dashboard/model-assessments')
      ]);

      setEthicsData({
        overview: overviewData.overview,
        bias_detection: biasData.bias_detection,
        fairness_metrics: fairnessData.fairness_metrics,
        recent_reports: reportsData.reports || [],
        model_assessments: assessmentsData.model_assessments || []
      });
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch AI ethics data:', error);
      // Fallback to mock data
      setEthicsData(mockEthicsData);
      setLoading(false);
    }
  };

  const refreshData = async () => {
    setRefreshing(true);
    try {
      await fetchEthicsData();
    } finally {
      setRefreshing(false);
    }
  };

  const getBiasColor = (severity) => {
    switch (severity) {
      case 'high': return 'text-red-600 bg-red-100';
      case 'medium': return 'text-orange-600 bg-orange-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getComplianceColor = (status) => {
    switch (status) {
      case 'compliant': return 'text-green-600 bg-green-100';
      case 'review_needed': return 'text-orange-600 bg-orange-100';
      case 'non_compliant': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getScoreColor = (score) => {
    if (score >= 9) return 'text-green-600';
    if (score >= 7) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto text-orange-600" />
          <p className="mt-2 text-gray-600">Loading AI Ethics dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center">
              <Brain className="h-8 w-8 mr-3 text-orange-600" />
              AI Ethics Dashboard
            </h1>
            <p className="text-gray-600 mt-1">Responsible AI monitoring and compliance tracking</p>
          </div>
          <button
            onClick={refreshData}
            disabled={refreshing}
            className="flex items-center px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <Award className="h-8 w-8 text-orange-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Ethics Score</p>
                <p className={`text-2xl font-bold ${getScoreColor(ethicsData.overview.overall_ethics_score)}`}>
                  {ethicsData.overview.overall_ethics_score}/10
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <Brain className="h-8 w-8 text-blue-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Models Monitored</p>
                <p className="text-2xl font-bold text-gray-900">{ethicsData.overview.models_monitored}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <AlertTriangle className="h-8 w-8 text-orange-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Bias Alerts (24h)</p>
                <p className="text-2xl font-bold text-gray-900">{ethicsData.overview.bias_alerts_24h}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <Scale className="h-8 w-8 text-green-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Fairness Compliance</p>
                <p className="text-2xl font-bold text-green-600">{ethicsData.overview.fairness_compliance}%</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <Eye className="h-8 w-8 text-amber-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Transparency</p>
                <p className={`text-2xl font-bold ${getScoreColor(ethicsData.overview.transparency_score)}`}>
                  {ethicsData.overview.transparency_score}/10
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              {[
                { id: 'overview', label: 'Overview', icon: Brain },
                { id: 'bias', label: 'Bias Detection', icon: Target },
                { id: 'fairness', label: 'Fairness Metrics', icon: Scale },
                { id: 'transparency', label: 'Transparency', icon: Eye }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setSelectedTab(tab.id)}
                  className={`flex items-center py-4 px-1 border-b-2 font-medium text-sm ${
                    selectedTab === tab.id
                      ? 'border-orange-500 text-orange-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <tab.icon className="h-4 w-4 mr-2" />
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {selectedTab === 'overview' && (
              <div className="space-y-6">
                {/* Model Assessments */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Model Ethics Assessments</h3>
                  <div className="space-y-3">
                    {ethicsData.model_assessments.map((model) => (
                      <div key={model.model_name} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="font-medium text-gray-900">{model.model_name}</h4>
                            <p className="text-sm text-gray-600">Last assessed: {new Date(model.last_assessment).toLocaleString()}</p>
                            {model.issues.length > 0 && (
                              <div className="mt-2">
                                <p className="text-sm text-orange-600">Issues:</p>
                                <ul className="text-sm text-gray-600 ml-4">
                                  {model.issues.map((issue, index) => (
                                    <li key={index} className="list-disc">{issue}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                          <div className="text-right">
                            <div className={`text-2xl font-bold ${getScoreColor(model.ethics_score)}`}>
                              {model.ethics_score}/10
                            </div>
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getComplianceColor(model.status)}`}>
                              {model.status.replace('_', ' ').toUpperCase()}
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {selectedTab === 'bias' && (
              <div className="space-y-6">
                {/* Geographical Bias */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Geographical Bias Detection</h3>
                  <div className="space-y-3">
                    {ethicsData.bias_detection.geographical_bias.map((bias, index) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="font-medium text-gray-900">{bias.location}</h4>
                            <p className="text-sm text-gray-600">Affected predictions: {bias.affected_predictions}</p>
                          </div>
                          <div className="text-right">
                            <div className="text-lg font-semibold text-gray-900">
                              Bias Score: {bias.bias_score}
                            </div>
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getBiasColor(bias.severity)}`}>
                              {bias.severity.toUpperCase()}
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Temporal Bias */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Temporal Bias Detection</h3>
                  <div className="space-y-3">
                    {ethicsData.bias_detection.temporal_bias.map((bias, index) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="font-medium text-gray-900">{bias.time_period}</h4>
                          </div>
                          <div className="text-right">
                            <div className="text-lg font-semibold text-gray-900">
                              Bias Score: {bias.bias_score}
                            </div>
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getBiasColor(bias.severity)}`}>
                              {bias.severity.toUpperCase()}
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {selectedTab === 'fairness' && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Fairness Metrics</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {Object.entries(ethicsData.fairness_metrics).map(([metric, data]) => (
                    <div key={metric} className="border border-gray-200 rounded-lg p-6">
                      <h4 className="font-medium text-gray-900 mb-4 capitalize">
                        {metric.replace('_', ' ')}
                      </h4>
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Current Score</span>
                          <span className="font-semibold">{data.score}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Threshold</span>
                          <span className="font-semibold">{data.threshold}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Status</span>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getComplianceColor(data.status)}`}>
                            {data.status.replace('_', ' ').toUpperCase()}
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2 mt-3">
                          <div 
                            className={`h-2 rounded-full ${data.score >= data.threshold ? 'bg-green-500' : 'bg-red-500'}`}
                            style={{ width: `${(data.score / 1) * 100}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {selectedTab === 'transparency' && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Transparency Reports</h3>
                <div className="space-y-4">
                  {ethicsData.transparency_reports.map((report) => (
                    <div key={report.id} className="border border-gray-200 rounded-lg p-6">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center mb-2">
                            <FileText className="h-5 w-5 text-blue-500 mr-2" />
                            <h4 className="font-medium text-gray-900">{report.model}</h4>
                          </div>
                          <p className="text-sm text-gray-600 mb-3">Report ID: {report.id}</p>
                          
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <p className="text-sm font-medium text-gray-700 mb-2">Data Sources:</p>
                              <div className="space-y-1">
                                {report.data_sources.map((source, index) => (
                                  <span key={index} className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded mr-2">
                                    {source}
                                  </span>
                                ))}
                              </div>
                            </div>
                            
                            <div>
                              <p className="text-sm font-medium text-gray-700 mb-2">Key Features:</p>
                              <div className="space-y-1">
                                {report.key_features.map((feature, index) => (
                                  <span key={index} className="inline-block bg-orange-100 text-orange-800 text-xs px-2 py-1 rounded mr-2">
                                    {feature}
                                  </span>
                                ))}
                              </div>
                            </div>
                          </div>
                        </div>
                        
                        <div className="text-right ml-4">
                          <div className={`text-xl font-bold ${getScoreColor(report.explainability_score)}`}>
                            {report.explainability_score}/10
                          </div>
                          <p className="text-xs text-gray-500">Explainability Score</p>
                          <p className="text-xs text-gray-500 mt-2">
                            {new Date(report.generated).toLocaleString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>AI Ethics monitoring powered by Phase 3 Responsible AI Framework</p>
          <p>Last updated: {new Date().toLocaleString()}</p>
        </div>
      </div>
    </div>
  );
};

export default AIEthicsDashboard;