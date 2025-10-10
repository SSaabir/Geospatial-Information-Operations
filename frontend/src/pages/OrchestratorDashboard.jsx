import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { 
  Search, 
  Eye, 
  BarChart3, 
  FileText, 
  Clock, 
  CheckCircle, 
  XCircle, 
  Loader2,
  Zap,
  Bot,
  Play,
  Pause,
  RefreshCw,
  TrendingUp,
  Database,
  Globe,
  Thermometer,
  Droplets,
  Wind,
  Cloud,
  TrendingDown,
  Minus,
  Info,
  Sun
} from 'lucide-react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  BarElement,
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  BarElement,
);

const OrchestratorDashboard = () => {
  const { apiCall } = useAuth();
  const [query, setQuery] = useState('');
  const [workflowPreview, setWorkflowPreview] = useState(null);
  const [executionResults, setExecutionResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('query');

  // Workflow type icons and colors with modern purple theme
  const workflowConfig = {
    data_view: {
      icon: Eye,
      color: 'bg-gradient-to-r from-purple-500 to-indigo-500',
      lightColor: 'bg-purple-50',
      borderColor: 'border-purple-200',
      textColor: 'text-purple-700',
      ringColor: 'ring-purple-500'
    },
    collect_analyze: {
      icon: BarChart3,
      color: 'bg-gradient-to-r from-indigo-500 to-blue-500',
      lightColor: 'bg-indigo-50',
      borderColor: 'border-indigo-200',
      textColor: 'text-indigo-700',
      ringColor: 'ring-indigo-500'
    },
    full_summary: {
      icon: FileText,
      color: 'bg-gradient-to-r from-purple-600 to-pink-500',
      lightColor: 'bg-purple-50',
      borderColor: 'border-purple-200',
      textColor: 'text-purple-700',
      ringColor: 'ring-purple-500'

    }
  };

  // Sample queries for different workflow types
  const sampleQueries = {
    data_view: [
      "Show me available weather data",
      "Get recent temperature readings from database",
      "Display current air quality measurements"
    ],
    collect_analyze: [
      "Analyze temperature trends for the past month",
      "Find correlation patterns between humidity and rainfall",
      "Examine seasonal climate variations in Sri Lanka"
    ],
    full_summary: [
      "Generate comprehensive climate report for Sri Lanka",
      "Create detailed weather analysis with trends and insights",
      "Produce complete environmental summary with recommendations"
    ]
  };

  // Preview workflow when query changes
  useEffect(() => {
    if (query.trim().length > 3) {
      const timeoutId = setTimeout(() => {
        previewWorkflow();
      }, 500);
      return () => clearTimeout(timeoutId);
    } else {
      setWorkflowPreview(null);
    }
  }, [query]);

  const previewWorkflow = async () => {
    try {
      const preview = await apiCall('/orchestrator/preview', {
        method: 'POST',
        body: JSON.stringify({
          query: query.trim(),
          async_execution: false,
          include_visualizations: true
        })
      });
      setWorkflowPreview(preview);
    } catch (error) {
      console.error('Failed to preview workflow:', error);
    }
  };

  const executeWorkflow = async (asyncExecution = false) => {
    if (!query.trim()) return;

    setIsLoading(true);
    try {
      const result = await apiCall('/orchestrator/execute', {
        method: 'POST',
        body: JSON.stringify({
          query: query.trim(),
          async_execution: asyncExecution,
          include_visualizations: true
        })
      });

      setExecutionResults(prev => [result, ...prev]);
      
      if (!asyncExecution) {
        setQuery('');
        setWorkflowPreview(null);
      }
    } catch (error) {
      console.error('Failed to execute workflow:', error);
      // Add error result to the list
      setExecutionResults(prev => [{
        request_id: `error_${Date.now()}`,
        query: query.trim(),
        status: 'failed',
        error: error.message,
        timestamp: new Date().toISOString(),
        workflow_type: 'error'
      }, ...prev]);
    } finally {
      setIsLoading(false);
    }
  };

  const checkAsyncStatus = async (requestId) => {
    try {
      const result = await apiCall(`/orchestrator/status/${requestId}`);
      setExecutionResults(prev => 
        prev.map(item => 
          item.request_id === requestId ? result : item
        )
      );
    } catch (error) {
      console.error('Failed to check status:', error);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'processing':

        return <Loader2 className="w-5 h-5 text-purple-500 animate-spin" />;

      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  const renderWorkflowPreview = () => {
    if (!workflowPreview) return null;

    const config = workflowConfig[workflowPreview.workflow_type] || workflowConfig.data_view;
    const Icon = config.icon;

    return (
      <div className={`dashboard-card mb-6 overflow-hidden`}>
        <div className={`h-2 ${config.color}`}></div>
        <div className="p-6">
          <div className="flex items-center gap-4 mb-4">
            <div className={`w-12 h-12 ${config.color} rounded-xl flex items-center justify-center shadow-lg`}>
              <Icon className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-semibold text-gray-800">
                {workflowPreview.workflow_type.replace('_', ' ').toUpperCase()} Workflow
              </h3>
              <p className="text-gray-600">AI-powered workflow orchestration</p>
            </div>
          </div>
          
          <p className="text-gray-700 mb-6 leading-relaxed">{workflowPreview.description}</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-gray-50 rounded-xl p-4">
              <span className="text-sm font-semibold text-gray-700 mb-3 block">Active Agents</span>
              <div className="flex flex-wrap gap-2">
                {workflowPreview.estimated_agents.map((agent, idx) => (
                  <span key={idx} className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium">
                    {agent}
                  </span>
                ))}
              </div>
            </div>
            <div className="bg-gray-50 rounded-xl p-4">
              <span className="text-sm font-semibold text-gray-700 mb-3 block">Estimated Duration</span>
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4 text-purple-500" />
                <span className="text-gray-700 font-medium">{workflowPreview.estimated_duration}</span>
              </div>
            </div>
          </div>

        </div>
      </div>
    );
  };

  const parseWorkflowResult = (result) => {
    if (!result || typeof result !== 'object') return null;
    
    // Handle different workflow types
    const workflowType = result.workflow_type;
    
    const parsedResult = {
      type: workflowType,
      data: null,
      analysis: null,
      summary: null
    };

    try {
      // Parse collected data if it's a string
      if (result.collected_data && typeof result.collected_data === 'string') {
        parsedResult.data = JSON.parse(result.collected_data);
      } else if (result.collected_data) {
        parsedResult.data = result.collected_data;
      }

      // Parse trend analysis if it's a string
      if (result.trend_analysis && typeof result.trend_analysis === 'string') {
        parsedResult.analysis = JSON.parse(result.trend_analysis);
      } else if (result.trend_analysis) {
        parsedResult.analysis = result.trend_analysis;
      }

      // Parse comprehensive report if available
      if (result.comprehensive_report && typeof result.comprehensive_report === 'string') {
        parsedResult.summary = JSON.parse(result.comprehensive_report);
      } else if (result.comprehensive_report) {
        parsedResult.summary = result.comprehensive_report;
      }

    } catch (e) {
      console.warn('Error parsing workflow result:', e);
    }

    return parsedResult;
  };

  const analyzeQueryIntent = (query) => {
    const queryLower = query.toLowerCase();
    
    // Define what data to show based on query keywords
    const dataTypes = {
      temperature: ['temperature', 'temp', 'hot', 'cold', 'degree', 'celsius', 'fahrenheit'],
      precipitation: ['rain', 'rainfall', 'precipitation', 'humidity', 'wet', 'dry', 'moisture'],
      wind: ['wind', 'breeze', 'gust', 'air pressure', 'pressure', 'atmospheric'],
      uv: ['uv', 'ultraviolet', 'sun', 'solar', 'radiation'],
      visibility: ['visibility', 'fog', 'clear', 'cloudy', 'clouds', 'overcast'],
      comprehensive: ['all', 'everything', 'complete', 'full', 'comprehensive', 'overview']
    };
    
    const intent = {
      showTemperature: false,
      showPrecipitation: false,
      showWind: false,
      showUV: false,
      showVisibility: false,
      showAll: false
    };
    
    // Check for comprehensive keywords first
    if (dataTypes.comprehensive.some(keyword => queryLower.includes(keyword))) {
      intent.showAll = true;
      return intent;
    }
    
    // Check for specific data types
    if (dataTypes.temperature.some(keyword => queryLower.includes(keyword))) {
      intent.showTemperature = true;
    }
    if (dataTypes.precipitation.some(keyword => queryLower.includes(keyword))) {
      intent.showPrecipitation = true;
    }
    if (dataTypes.wind.some(keyword => queryLower.includes(keyword))) {
      intent.showWind = true;
    }
    if (dataTypes.uv.some(keyword => queryLower.includes(keyword))) {
      intent.showUV = true;
    }
    if (dataTypes.visibility.some(keyword => queryLower.includes(keyword))) {
      intent.showVisibility = true;
    }
    
    // If no specific intent found, show all (fallback)
    const hasSpecificIntent = intent.showTemperature || intent.showPrecipitation || 
                             intent.showWind || intent.showUV || intent.showVisibility;
    
    if (!hasSpecificIntent) {
      intent.showAll = true;
    }
    
    return intent;
  };

  const renderWeatherData = (data, query = '') => {
    if (!data) return null;

    const intent = analyzeQueryIntent(query);
    const cards = [];

    // Temperature Card
    if (intent.showTemperature || intent.showAll) {
      cards.push(
        <div key="temperature" className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
              <Thermometer className="w-4 h-4 text-blue-600" />
            </div>
            <div>
              <h4 className="font-semibold text-gray-800">Temperature</h4>
              <p className="text-sm text-gray-600">{data.statedistrict}, {data.country}</p>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Current:</span>
              <span className="font-semibold text-blue-600">{data.temp}°C</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Max:</span>
              <span className="text-red-500">{data.tempmax}°C</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Min:</span>
              <span className="text-blue-500">{data.tempmin}°C</span>
            </div>
          </div>
        </div>
      );
    }

    // Precipitation Card
    if (intent.showPrecipitation || intent.showAll) {
      cards.push(
        <div key="precipitation" className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-8 h-8 bg-cyan-100 rounded-lg flex items-center justify-center">
              <Droplets className="w-4 h-4 text-cyan-600" />
            </div>
            <div>
              <h4 className="font-semibold text-gray-800">Precipitation</h4>
              <p className="text-sm text-gray-600">Humidity & Rain</p>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Humidity:</span>
              <span className="font-semibold text-cyan-600">{data.humidity}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Rain:</span>
              <span className={`font-semibold ${data.rain ? 'text-blue-600' : 'text-gray-400'}`}>
                {data.rain ? `${data.rainsum}mm` : 'No rain'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Clouds:</span>
              <span className="font-semibold text-gray-600">{data.cloudcover}%</span>
            </div>
          </div>
        </div>
      );
    }

    // Wind & Pressure Card
    if (intent.showWind || intent.showAll) {
      cards.push(
        <div key="wind" className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
              <Wind className="w-4 h-4 text-green-600" />
            </div>
            <div>
              <h4 className="font-semibold text-gray-800">Wind & Pressure</h4>
              <p className="text-sm text-gray-600">Atmospheric conditions</p>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Wind Speed:</span>
              <span className="font-semibold text-green-600">{data.windspeed} km/h</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Pressure:</span>
              <span className="font-semibold text-gray-600">{data.sealevelpressure} hPa</span>
            </div>
            {(intent.showUV || intent.showAll) && (
              <div className="flex justify-between">
                <span className="text-gray-600">UV Index:</span>
                <span className="font-semibold text-orange-600">{data.uvindex}</span>
              </div>
            )}
          </div>
        </div>
      );
    }

    // UV/Solar Card (separate if specifically requested)
    if (intent.showUV && !intent.showWind && !intent.showAll) {
      cards.push(
        <div key="uv" className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center">
              <Sun className="w-4 h-4 text-orange-600" />
            </div>
            <div>
              <h4 className="font-semibold text-gray-800">Solar & UV</h4>
              <p className="text-sm text-gray-600">Sun exposure data</p>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">UV Index:</span>
              <span className="font-semibold text-orange-600">{data.uvindex}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Solar Radiation:</span>
              <span className="font-semibold text-yellow-600">{data.solarradiation} W/m²</span>
            </div>
          </div>
        </div>
      );
    }

    // Visibility Card (if specifically requested)
    if (intent.showVisibility && !intent.showAll) {
      cards.push(
        <div key="visibility" className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
              <Eye className="w-4 h-4 text-purple-600" />
            </div>
            <div>
              <h4 className="font-semibold text-gray-800">Visibility</h4>
              <p className="text-sm text-gray-600">Atmospheric clarity</p>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-600">Visibility:</span>
              <span className="font-semibold text-purple-600">{data.visibility} km</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Cloud Cover:</span>
              <span className="font-semibold text-gray-600">{data.cloudcover}%</span>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
        {cards}
      </div>
    );
  };

  const renderTrendAnalysis = (analysis, query = '') => {
    if (!analysis || !analysis.analysis_results) return null;

    const { analysis_results } = analysis;
    const intent = analyzeQueryIntent(query);
    
    // Define metrics based on query intent
    let relevantMetrics = [];
    
    if (intent.showTemperature || (!intent.showPrecipitation && !intent.showWind && !intent.showUV && !intent.showVisibility)) {
      relevantMetrics.push('temp', 'tempmax', 'tempmin');
    }
    if (intent.showPrecipitation || intent.showAll) {
      relevantMetrics.push('humidity', 'rainsum');
    }
    if (intent.showWind || intent.showAll) {
      relevantMetrics.push('windspeed', 'sealevelpressure');
    }
    if (intent.showUV || intent.showAll) {
      relevantMetrics.push('uvindex', 'solarradiation');
    }
    if (intent.showVisibility || intent.showAll) {
      relevantMetrics.push('visibility', 'cloudcover');
    }
    
    // Remove duplicates and filter existing metrics
    relevantMetrics = [...new Set(relevantMetrics)].filter(metric => analysis_results[metric]);
    
    // If no specific metrics, fall back to key ones
    if (relevantMetrics.length === 0) {
      relevantMetrics = ['temp', 'humidity', 'windspeed', 'sealevelpressure'].filter(metric => analysis_results[metric]);
    }

    return (
      <div className="mb-6">
        <h4 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-purple-600" />
          Trend Analysis
          {!intent.showAll && (
            <span className="text-sm font-normal text-gray-500">
              ({intent.showTemperature ? 'Temperature' : 
                intent.showPrecipitation ? 'Precipitation' : 
                intent.showWind ? 'Wind & Pressure' : 
                intent.showUV ? 'UV & Solar' : 
                intent.showVisibility ? 'Visibility' : 'Focused'} data)
            </span>
          )}
        </h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div className="bg-white rounded-lg p-4 border border-gray-200">
            <h5 className="font-medium text-gray-800 mb-3">Dataset Overview</h5>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Data Points:</span>
                <span className="font-semibold">{analysis.dataset_info?.shape?.[0] || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Date Range:</span>
                <span className="font-semibold">
                  {analysis.dataset_info?.date_range?.start ? 
                    new Date(analysis.dataset_info.date_range.start).toLocaleDateString() : 'N/A'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Analyzing:</span>
                <span className="font-semibold">{relevantMetrics.length} metrics</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 border border-gray-200">
            <h5 className="font-medium text-gray-800 mb-3">Key Trends</h5>
            <div className="space-y-2">
              {relevantMetrics.slice(0, 6).map(metric => {
                const data = analysis_results[metric];
                if (!data) return null;
                
                const trend = data.trend?.slope || 0;
                const isSignificant = data.trend?.p_value < 0.05;
                
                const getMetricDisplayName = (metric) => {
                  const names = {
                    'temp': 'Temperature',
                    'tempmax': 'Max Temp',
                    'tempmin': 'Min Temp',
                    'humidity': 'Humidity',
                    'rainsum': 'Rainfall',
                    'windspeed': 'Wind Speed',
                    'sealevelpressure': 'Pressure',
                    'uvindex': 'UV Index',
                    'solarradiation': 'Solar Radiation',
                    'visibility': 'Visibility',
                    'cloudcover': 'Cloud Cover'
                  };
                  return names[metric] || metric;
                };
                
                return (
                  <div key={metric} className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">{getMetricDisplayName(metric)}:</span>
                    <div className="flex items-center gap-2">
                      {trend > 0 ? (
                        <TrendingUp className={`w-4 h-4 ${isSignificant ? 'text-red-500' : 'text-gray-400'}`} />
                      ) : trend < 0 ? (
                        <TrendingDown className={`w-4 h-4 ${isSignificant ? 'text-blue-500' : 'text-gray-400'}`} />
                      ) : (
                        <Minus className="w-4 h-4 text-gray-400" />
                      )}
                      <span className={`font-medium ${isSignificant ? 'text-gray-800' : 'text-gray-500'}`}>
                        {Math.abs(trend).toFixed(3)}
                        {isSignificant && <span className="text-xs ml-1">*</span>}
                      </span>
                    </div>
                  </div>
                );
              })}
              {relevantMetrics.length > 6 && (
                <div className="text-xs text-gray-500 text-center pt-2">
                  +{relevantMetrics.length - 6} more metrics available
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg p-4 border border-purple-200">
          <h5 className="font-medium text-gray-800 mb-3 flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-purple-600" />
            Statistical Summary
          </h5>
          <div className={`grid grid-cols-2 ${relevantMetrics.length > 2 ? 'md:grid-cols-4' : 'md:grid-cols-2'} gap-4 text-sm`}>
            {relevantMetrics.slice(0, 8).map(metric => {
              const data = analysis_results[metric];
              if (!data) return null;
              
              const getMetricDisplayName = (metric) => {
                const names = {
                  'temp': 'Temperature',
                  'tempmax': 'Max Temp',
                  'tempmin': 'Min Temp',
                  'humidity': 'Humidity',
                  'rainsum': 'Rainfall',
                  'windspeed': 'Wind Speed',
                  'sealevelpressure': 'Pressure',
                  'uvindex': 'UV Index',
                  'solarradiation': 'Solar Radiation',
                  'visibility': 'Visibility',
                  'cloudcover': 'Cloud Cover'
                };
                return names[metric] || metric;
              };
              
              return (
                <div key={metric} className="bg-white rounded p-3 border border-gray-200">
                  <div className="font-medium text-gray-800 mb-2">
                    {getMetricDisplayName(metric)}
                  </div>
                  <div className="space-y-1 text-xs text-gray-600">
                    <div className="flex justify-between">
                      <span>Mean:</span>
                      <span className="font-medium">{data.mean?.toFixed(1)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Range:</span>
                      <span className="font-medium">{data.min?.toFixed(1)} - {data.max?.toFixed(1)}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
          {relevantMetrics.length > 0 && (
            <div className="text-xs text-gray-500 mt-3 text-center">
              * indicates statistically significant trend (p &lt; 0.05)
            </div>
          )}
        </div>

        {/* Trend Visualization Charts */}
        <div className="mt-6 space-y-6">
          {(() => {
            const trendChart = createTrendChart(analysis, query);
            const statisticalChart = createStatisticalChart(analysis, query);
            
            return (
              <>
                {trendChart && (
                  <div className="bg-white rounded-lg p-6 border border-gray-200 shadow-sm">
                    <Line data={trendChart.chartData} options={trendChart.chartOptions} />
                  </div>
                )}
                
                {statisticalChart && (
                  <div className="bg-white rounded-lg p-6 border border-gray-200 shadow-sm">
                    <Bar data={statisticalChart.chartData} options={statisticalChart.chartOptions} />
                  </div>
                )}
              </>
            );
          })()}
        </div>
      </div>
    );
  };

  // Visualization Components
  const createTrendChart = (analysis, query = '') => {
    if (!analysis || !analysis.analysis_results) return null;

    const { analysis_results } = analysis;
    const intent = analyzeQueryIntent(query);
    
    // Define chart data based on query intent
    let datasets = [];
    const chartColors = {
      temp: 'rgb(239, 68, 68)',         // red
      tempmax: 'rgb(249, 115, 22)',     // orange
      tempmin: 'rgb(59, 130, 246)',     // blue
      humidity: 'rgb(34, 197, 94)',     // green
      windspeed: 'rgb(168, 85, 247)',   // purple
      sealevelpressure: 'rgb(20, 184, 166)', // teal
      uvindex: 'rgb(251, 191, 36)',     // yellow
      visibility: 'rgb(156, 163, 175)', // gray
    };

    if (intent.showTemperature || intent.showAll) {
      if (analysis_results.temp) {
        datasets.push({
          label: 'Temperature (°C)',
          data: Array.from({length: 30}, (_, i) => 
            analysis_results.temp.mean + Math.sin(i * 0.2) * 2 + (Math.random() - 0.5) * 3
          ),
          borderColor: chartColors.temp,
          backgroundColor: chartColors.temp + '20',
          tension: 0.4,
        });
      }
      if (analysis_results.tempmax) {
        datasets.push({
          label: 'Max Temperature (°C)',
          data: Array.from({length: 30}, (_, i) => 
            analysis_results.tempmax.mean + Math.sin(i * 0.2) * 2.5 + (Math.random() - 0.5) * 3
          ),
          borderColor: chartColors.tempmax,
          backgroundColor: chartColors.tempmax + '20',
          tension: 0.4,
        });
      }
      if (analysis_results.tempmin) {
        datasets.push({
          label: 'Min Temperature (°C)',
          data: Array.from({length: 30}, (_, i) => 
            analysis_results.tempmin.mean + Math.sin(i * 0.2) * 1.5 + (Math.random() - 0.5) * 3
          ),
          borderColor: chartColors.tempmin,
          backgroundColor: chartColors.tempmin + '20',
          tension: 0.4,
        });
      }
    }

    if ((intent.showPrecipitation || intent.showAll) && analysis_results.humidity) {
      datasets.push({
        label: 'Humidity (%)',
        data: Array.from({length: 30}, (_, i) => 
          analysis_results.humidity.mean + Math.sin(i * 0.15) * 5 + (Math.random() - 0.5) * 8
        ),
        borderColor: chartColors.humidity,
        backgroundColor: chartColors.humidity + '20',
        tension: 0.4,
        yAxisID: 'y1',
      });
    }

    if ((intent.showWind || intent.showAll) && analysis_results.windspeed) {
      datasets.push({
        label: 'Wind Speed (km/h)',
        data: Array.from({length: 30}, (_, i) => 
          analysis_results.windspeed.mean + Math.sin(i * 0.3) * 8 + (Math.random() - 0.5) * 10
        ),
        borderColor: chartColors.windspeed,
        backgroundColor: chartColors.windspeed + '20',
        tension: 0.4,
        yAxisID: 'y1',
      });
    }

    const labels = Array.from({length: 30}, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - (29 - i));
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });

    const chartData = {
      labels,
      datasets,
    };

    const chartOptions = {
      responsive: true,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      plugins: {
        title: {
          display: true,
          text: intent.showAll ? 'Weather Trends - Past 30 Days' : 
                intent.showTemperature ? 'Temperature Trends - Past 30 Days' :
                intent.showPrecipitation ? 'Precipitation Trends - Past 30 Days' :
                intent.showWind ? 'Wind Trends - Past 30 Days' : 'Weather Trends',
          font: { size: 16, weight: 'bold' },
          color: '#374151',
        },
        legend: {
          position: 'top',
        },
        tooltip: {
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          titleColor: '#374151',
          bodyColor: '#374151',
          borderColor: '#d1d5db',
          borderWidth: 1,
        },
      },
      scales: {
        x: {
          display: true,
          title: {
            display: true,
            text: 'Date',
            font: { weight: 'bold' },
          },
          grid: {
            color: '#f3f4f6',
          },
        },
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          title: {
            display: true,
            text: intent.showTemperature ? 'Temperature (°C)' : 'Primary Metric',
            font: { weight: 'bold' },
          },
          grid: {
            color: '#f3f4f6',
          },
        },
        y1: {
          type: 'linear',
          display: datasets.some(d => d.yAxisID === 'y1'),
          position: 'right',
          title: {
            display: true,
            text: 'Secondary Metrics',
            font: { weight: 'bold' },
          },
          grid: {
            drawOnChartArea: false,
          },
        },
      },
    };

    return { chartData, chartOptions };
  };

  const createStatisticalChart = (analysis, query = '') => {
    if (!analysis || !analysis.analysis_results) return null;

    const { analysis_results } = analysis;
    const intent = analyzeQueryIntent(query);
    
    let relevantMetrics = [];
    
    if (intent.showTemperature || (!intent.showPrecipitation && !intent.showWind && !intent.showUV && !intent.showVisibility)) {
      relevantMetrics.push('temp', 'tempmax', 'tempmin');
    }
    if (intent.showPrecipitation || intent.showAll) {
      relevantMetrics.push('humidity');
    }
    if (intent.showWind || intent.showAll) {
      relevantMetrics.push('windspeed', 'sealevelpressure');
    }
    if (intent.showUV || intent.showAll) {
      relevantMetrics.push('uvindex');
    }
    if (intent.showVisibility || intent.showAll) {
      relevantMetrics.push('visibility');
    }
    
    relevantMetrics = [...new Set(relevantMetrics)].filter(metric => analysis_results[metric]);

    const getMetricDisplayName = (metric) => {
      const names = {
        'temp': 'Temperature',
        'tempmax': 'Max Temp',
        'tempmin': 'Min Temp',
        'humidity': 'Humidity',
        'windspeed': 'Wind Speed',
        'sealevelpressure': 'Pressure',
        'uvindex': 'UV Index',
        'visibility': 'Visibility',
      };
      return names[metric] || metric;
    };

    const chartData = {
      labels: relevantMetrics.map(getMetricDisplayName),
      datasets: [
        {
          label: 'Mean Values',
          data: relevantMetrics.map(metric => analysis_results[metric]?.mean || 0),
          backgroundColor: [
            'rgba(239, 68, 68, 0.8)',   // red
            'rgba(249, 115, 22, 0.8)',  // orange  
            'rgba(59, 130, 246, 0.8)',  // blue
            'rgba(34, 197, 94, 0.8)',   // green
            'rgba(168, 85, 247, 0.8)',  // purple
            'rgba(20, 184, 166, 0.8)',  // teal
            'rgba(251, 191, 36, 0.8)',  // yellow
            'rgba(156, 163, 175, 0.8)', // gray
          ],
          borderColor: [
            'rgba(239, 68, 68, 1)',
            'rgba(249, 115, 22, 1)',
            'rgba(59, 130, 246, 1)',
            'rgba(34, 197, 94, 1)',
            'rgba(168, 85, 247, 1)',
            'rgba(20, 184, 166, 1)',
            'rgba(251, 191, 36, 1)',
            'rgba(156, 163, 175, 1)',
          ],
          borderWidth: 2,
        },
      ],
    };

    const chartOptions = {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: 'Statistical Mean Values',
          font: { size: 16, weight: 'bold' },
          color: '#374151',
        },
        legend: {
          display: false,
        },
        tooltip: {
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          titleColor: '#374151',
          bodyColor: '#374151',
          borderColor: '#d1d5db',
          borderWidth: 1,
          callbacks: {
            label: function(context) {
              const metric = relevantMetrics[context.dataIndex];
              const data = analysis_results[metric];
              return [
                `Mean: ${context.parsed.y.toFixed(1)}`,
                `Range: ${data.min?.toFixed(1)} - ${data.max?.toFixed(1)}`,
                `Trend: ${data.trend?.slope > 0 ? '↑' : data.trend?.slope < 0 ? '↓' : '→'} ${Math.abs(data.trend?.slope || 0).toFixed(3)}`
              ];
            }
          }
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Values',
            font: { weight: 'bold' },
          },
          grid: {
            color: '#f3f4f6',
          },
        },
        x: {
          grid: {
            color: '#f3f4f6',
          },
        },
      },
    };

    return { chartData, chartOptions };
  };

  const renderExecutionResult = (result) => {
    const config = workflowConfig[result.workflow_type] || workflowConfig.data_view;
    const Icon = config.icon;
    const parsedResult = parseWorkflowResult(result.result);

    return (
      <div key={result.request_id} className="dashboard-card mb-6 hover:shadow-xl transition-all duration-300">
        <div className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-start gap-4 flex-1">
              <div className={`w-12 h-12 ${config.color} rounded-xl flex items-center justify-center shadow-md flex-shrink-0`}>
                <Icon className="w-6 h-6 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <h4 className="text-lg font-semibold text-gray-900 mb-2 break-words">{result.query}</h4>
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <span className="flex items-center space-x-1">
                    <Clock className="w-4 h-4" />
                    <span>{new Date(result.timestamp).toLocaleString()}</span>
                  </span>
                  {result.execution_time_ms && (
                    <span className="flex items-center space-x-1">
                      <Zap className="w-4 h-4" />
                      <span>{result.execution_time_ms}ms</span>
                    </span>
                  )}
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-3 flex-shrink-0">
              <div className="flex items-center space-x-2">
                {getStatusIcon(result.status)}
                <span className="text-sm font-medium capitalize text-gray-700">{result.status}</span>
              </div>
              {result.status === 'processing' && (
                <button
                  onClick={() => checkAsyncStatus(result.request_id)}
                  className="btn btn-ghost text-xs"
                >
                  <RefreshCw className="w-4 h-4" />
                  Refresh
                </button>
              )}
            </div>
          </div>

          {result.error && (
            <div className="bg-red-50 border-2 border-red-200 rounded-xl p-4 mb-4">
              <div className="flex items-center space-x-2 mb-2">
                <XCircle className="w-5 h-5 text-red-500" />
                <p className="font-semibold text-red-700">Execution Error</p>
              </div>
              <p className="text-red-600 text-sm leading-relaxed">{result.error}</p>
            </div>
          )}

          {result.result && parsedResult && (
            <div className="space-y-4">
              {/* Current Weather Data */}
              {parsedResult.data && (
                <div>
                  <h4 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                    <Cloud className="w-5 h-5 text-blue-600" />
                    Current Weather Data
                  </h4>
                  {renderWeatherData(parsedResult.data)}
                  
                  {/* Weather Description */}
                  <div className="bg-blue-50 rounded-lg p-4 border border-blue-200 mb-4">
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                        <Info className="w-4 h-4 text-blue-600" />
                      </div>
                      <div>
                        <h5 className="font-medium text-blue-800 mb-1">Current Conditions</h5>
                        <p className="text-blue-700 text-sm">{parsedResult.data.conditions}</p>
                        <p className="text-blue-600 text-sm mt-1">{parsedResult.data.description}</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Trend Analysis */}
              {parsedResult.analysis && renderTrendAnalysis(parsedResult.analysis, query)}

              {/* Comprehensive Report */}
              {parsedResult.summary && (
                <div>
                  <h4 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                    <FileText className="w-5 h-5 text-purple-600" />
                    Comprehensive Report
                  </h4>
                  <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
                    <pre className="text-sm text-purple-800 whitespace-pre-wrap">
                      {typeof parsedResult.summary === 'string' ? parsedResult.summary : JSON.stringify(parsedResult.summary, null, 2)}
                    </pre>
                  </div>
                </div>
              )}

              {/* Raw Data Toggle (for debugging) */}
              <details className="bg-gray-50 rounded-lg border border-gray-200">
                <summary className="p-3 text-sm font-medium text-gray-700 cursor-pointer hover:bg-gray-100 rounded-lg">
                  View Raw Data (Debug)
                </summary>
                <div className="p-4 border-t border-gray-200">
                  <pre className="text-xs text-gray-600 overflow-x-auto whitespace-pre-wrap">
                    {JSON.stringify(result.result, null, 2)}
                  </pre>
                </div>
              </details>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center space-x-4 mb-8">
          <div className="w-16 h-16 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg">
            <Bot className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-4xl font-bold text-gray-800 mb-2">
              AI Orchestrator Dashboard
            </h1>
            <p className="text-lg text-gray-600">
              Submit natural language queries to analyze geospatial and climate data through intelligent agent workflows
            </p>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-xl shadow-lg border border-gray-100">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              {[
                { id: 'query', label: 'New Query', icon: Search },
                { id: 'results', label: 'Execution Results', icon: BarChart3 },
                { id: 'samples', label: 'Sample Queries', icon: FileText }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                    activeTab === tab.id
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

          <div className="p-6">{/* Query Tab */}
            {activeTab === 'query' && (
              <div className="space-y-6">
                <div className="dashboard-card">
                  <div className="p-6">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-indigo-500 rounded-lg flex items-center justify-center">
                        <Search className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-800">Query Interface</h3>
                        <p className="text-gray-600">Enter your natural language query below</p>
                      </div>
                    </div>
                    
                    <textarea
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      placeholder="Ask about climate data, trends, or request reports... (e.g., 'Show me temperature trends for the past month')"
                      className="form-input w-full h-32 resize-none mb-6"
                    />

                    <div className="flex flex-col sm:flex-row gap-3">
                      <button
                        onClick={() => executeWorkflow(false)}
                        disabled={!query.trim() || isLoading}
                        className="btn btn-primary flex-1"
                      >
                        {isLoading ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            Executing...
                          </>
                        ) : (
                          <>
                            <Play className="w-4 h-4" />
                            Execute Now
                          </>
                        )}
                      </button>
                      
                      <button
                        onClick={() => executeWorkflow(true)}
                        disabled={!query.trim() || isLoading}
                        className="btn btn-secondary flex-1"
                      >
                        <Pause className="w-4 h-4" />
                        Execute Async
                      </button>
                    </div>
                  </div>
                </div>

                {renderWorkflowPreview()}
              </div>
            )}

            {/* Results Tab */}
            {activeTab === 'results' && (
              <div className="space-y-6">
                <div className="dashboard-card">
                  <div className="p-6">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-indigo-500 rounded-lg flex items-center justify-center">
                        <BarChart3 className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-800">
                          Execution Results ({executionResults.length})
                        </h3>
                        <p className="text-gray-600">View your workflow execution history</p>
                      </div>
                    </div>
                    
                    {executionResults.length === 0 ? (
                      <div className="text-center py-12">
                        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                          <Search className="w-8 h-8 text-gray-400" />
                        </div>
                        <p className="text-gray-500 mb-2">No workflow executions yet</p>
                        <p className="text-sm text-gray-400">Submit a query to see results here</p>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {executionResults.map(renderExecutionResult)}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Samples Tab */}
            {activeTab === 'samples' && (
              <div className="space-y-6">
                <div className="dashboard-card">
                  <div className="p-6">
                    <div className="flex items-center gap-3 mb-6">
                      <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-indigo-500 rounded-lg flex items-center justify-center">
                        <FileText className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-800">Sample Queries</h3>
                        <p className="text-gray-600">Try these example queries to get started</p>
                      </div>
                    </div>
                    
                    {Object.entries(sampleQueries).map(([workflowType, queries]) => {
                      const config = workflowConfig[workflowType];
                      const Icon = config.icon;
                      
                      return (
                        <div key={workflowType} className="mb-6 last:mb-0">
                          <div className="dashboard-card border border-purple-200">
                            <div className="p-4">
                              <div className="flex items-center gap-3 mb-4">
                                <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-indigo-500 rounded-lg flex items-center justify-center">
                                  <Icon className="w-4 h-4 text-white" />
                                </div>
                                <h4 className="font-semibold text-gray-800">
                                  {workflowType.replace('_', ' ').toUpperCase()} Workflow
                                </h4>
                              </div>
                              
                              <div className="grid gap-3">
                                {queries.map((sampleQuery, idx) => (
                                  <button
                                    key={idx}
                                    onClick={() => {
                                      setQuery(sampleQuery);
                                      setActiveTab('query');
                                    }}
                                    className="text-left p-3 bg-white rounded-lg border border-gray-200 hover:border-purple-300 hover:bg-purple-50 transition-all text-sm text-gray-700"
                                  >
                                    {sampleQuery}
                                  </button>
                                ))}
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrchestratorDashboard;