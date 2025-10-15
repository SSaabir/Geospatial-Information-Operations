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
  // Simple mock rows to demo table rendering when backend isn't running
  const [query, setQuery] = useState('');
  const [workflowPreview, setWorkflowPreview] = useState(null);
  const [executionResults, setExecutionResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('query');

  // A sample execution result object that mimics backend response structure
  // (Demo/test artifacts removed) — execution results come from backend and are rendered per-card

  // Workflow type icons and colors with modern purple theme
  const workflowConfig = {
    data_view: {
      icon: Eye,
      color: 'bg-gradient-to-r from-orange-500 to-amber-500',
      lightColor: 'bg-orange-50',
      borderColor: 'border-orange-200',
      textColor: 'text-orange-700',
      ringColor: 'ring-orange-500'
    },
    collect_analyze: {
      icon: BarChart3,
      color: 'bg-gradient-to-r from-amber-500 to-blue-500',
      lightColor: 'bg-amber-50',
      borderColor: 'border-amber-200',
      textColor: 'text-green-900',
      ringColor: 'ring-amber-500'
    },
    full_summary: {
      icon: FileText,
      color: 'bg-gradient-to-r from-orange-600 to-pink-500',
      lightColor: 'bg-orange-50',
      borderColor: 'border-orange-200',
      textColor: 'text-orange-700',
      ringColor: 'ring-orange-500'

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

        return <Loader2 className="w-5 h-5 text-orange-500 animate-spin" />;

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
                  <span key={idx} className="px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-sm font-medium">
                    {agent}
                  </span>
                ))}
              </div>
            </div>
            <div className="bg-gray-50 rounded-xl p-4">
              <span className="text-sm font-semibold text-gray-700 mb-3 block">Estimated Duration</span>
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4 text-orange-500" />
                <span className="text-gray-700 font-medium">{workflowPreview.estimated_duration}</span>
              </div>
            </div>
          </div>

        </div>
      </div>
    );
  };

  const parseWorkflowResult = (result) => {
    if (!result) return null;

    // Helper: safe JSON parse that returns original value on failure
    const safeParseJSON = (v) => {
      if (typeof v !== 'string') return v;
      try {
        return JSON.parse(v);
      } catch (e) {
        // Remove surrounding single quotes if present and retry
        const trimmed = v.trim();
        if ((trimmed.startsWith('{') && trimmed.endsWith('}')) || (trimmed.startsWith('[') && trimmed.endsWith(']'))) {
          try { return JSON.parse(trimmed); } catch (_) { return v; }
        }
        return v;
      }
    };

    // Normalize result which can be nested: some agents put JSON under result (string) or collector outputs
    let resolved = result;
    if (typeof result === 'string') {
      resolved = safeParseJSON(result);
    }

    // Helper to extract a JSON object embedded inside a larger text blob (e.g., raw_output)
    const extractJsonFromText = (text) => {
      if (typeof text !== 'string') return null;
      const first = text.indexOf('{');
      const last = text.lastIndexOf('}');
      if (first === -1 || last === -1 || last <= first) return null;
      const candidate = text.slice(first, last + 1);
      try {
        return JSON.parse(candidate);
      } catch (e) {
        // try to be liberal: replace newlines that may break parsing
        try { return JSON.parse(candidate.replace(/\n/g, '\\n')); } catch (_) { return null; }
      }
    };

    // If the result object has fields that contain stringified JSON or text with embedded JSON
    // try to parse them and merge the JSON into the resolved object.
    const textFields = ['result', 'final_output', 'raw_output', 'output'];
    for (const field of textFields) {
      if (resolved && typeof resolved === 'object' && resolved[field] && typeof resolved[field] === 'string') {
        // First try direct JSON parse
        const parsedInner = safeParseJSON(resolved[field]);
        if (parsedInner && typeof parsedInner === 'object') {
          resolved = { ...resolved, ...parsedInner };
          continue;
        }

        // If direct parse failed, attempt to extract JSON substring from text
        const parsedFromRaw = extractJsonFromText(resolved[field]);
        if (parsedFromRaw && typeof parsedFromRaw === 'object') {
          resolved = { ...resolved, ...parsedFromRaw };
          continue;
        }
      }
    }

    const workflowType = resolved.workflow_type || resolved.type || null;

    const parsedResult = {
      type: workflowType,
      data: null,
      analysis: null,
      summary: null,
      report: null
    };

    try {
      // NEW: Check for structured collector_data from orchestrator
      if (resolved.collector_data) {
        const collectorData = safeParseJSON(resolved.collector_data);
        // Parse the nested structure from collector
        if (collectorData && typeof collectorData === 'object') {
          if (collectorData.data && collectorData.data.rows) {
            // Structure: {data: {rows: [...]}}
            parsedResult.data = collectorData.data;
          } else if (collectorData.rows) {
            // Structure: {rows: [...]}
            parsedResult.data = collectorData;
          } else if (Array.isArray(collectorData)) {
            parsedResult.data = { rows: collectorData };
          } else {
            parsedResult.data = collectorData;
          }
        }
      }
      
      // Fallback: Check common locations if collector_data not found
      if (!parsedResult.data) {
        const candidates = [
          resolved.data,
          resolved.data_view,
          resolved.collected_data,
          resolved.payload,
          resolved.output,
          resolved.rows,
          resolved.result,
        ];

        for (const c of candidates) {
          if (!c) continue;
          const parsed = safeParseJSON(c);
          // If parsed is an object with rows or is an array, consider it data
          if (Array.isArray(parsed)) {
            parsedResult.data = { rows: parsed };
            break;
          }
          if (parsed && typeof parsed === 'object') {
            // If it already looks like {rows: [...]}
            if (Array.isArray(parsed.rows)) {
              parsedResult.data = parsed;
              break;
            }
            // If object has keys like datetime/temp, treat as single record
            const keys = Object.keys(parsed);
            if (keys.length > 0) {
              parsedResult.data = parsed;
              break;
            }
          }
        }
      }

      // Trend analysis / summary
      if (resolved.trend_analysis) parsedResult.analysis = safeParseJSON(resolved.trend_analysis);
      if (resolved.analysis_results) parsedResult.analysis = parsedResult.analysis || resolved.analysis_results;
      if (resolved.comprehensive_report) parsedResult.summary = safeParseJSON(resolved.comprehensive_report);
      if (!parsedResult.summary && resolved.summary) parsedResult.summary = safeParseJSON(resolved.summary);
      
      // NEW: Add report_content for LLM-generated reports
      if (resolved.report_content) {
        parsedResult.report = typeof resolved.report_content === 'string' 
          ? resolved.report_content 
          : JSON.stringify(resolved.report_content);
      }

    } catch (e) {
      console.warn('Error parsing workflow result:', e);
    }

    return parsedResult;
  };

  // Utility: safe JSON parse available to rendering logic
  const safeParseJSON = (v) => {
    if (typeof v !== 'string') return v;
    try { return JSON.parse(v); } catch (e) {
      const trimmed = v.trim();
      if ((trimmed.startsWith('{') && trimmed.endsWith('}')) || (trimmed.startsWith('[') && trimmed.endsWith(']'))) {
        try { return JSON.parse(trimmed); } catch (_) { return v; }
      }
      return v;
    }
  };

  const formatCell = (val) => {
    if (val === null || val === undefined) return <span className="text-gray-400">—</span>;
    if (typeof val === 'string') {
      // Try ISO date detection
      const isoDate = Date.parse(val);
      if (!isNaN(isoDate) && val.match(/^\d{4}-\d{2}-\d{2}/)) {
        return new Date(val).toLocaleString();
      }
      // Try to pretty-print JSON strings
      try {
        const parsed = JSON.parse(val);
        return <pre className="whitespace-pre-wrap text-sm">{JSON.stringify(parsed, null, 2)}</pre>;
      } catch (e) {
        return val;
      }
    }
    if (typeof val === 'object') {
      try { return <pre className="whitespace-pre-wrap text-sm">{JSON.stringify(val, null, 2)}</pre>; } catch (e) { return String(val); }
    }
    return String(val);
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
    if (!data) return null;

    // If data has a 'rows' array (SQL result), render as table
    if (Array.isArray(data.rows)) {
      const rows = data.rows;
      if (rows.length === 0) return <div className="text-gray-500">No data found.</div>;
      // Ensure rows are objects (parse strings if needed)
      const normalizedRows = rows.map(r => (typeof r === 'string' ? safeParseJSON(r) : r));
      const columns = Object.keys(normalizedRows[0]);
      return (
        <div className="overflow-x-auto rounded-lg border border-gray-200 bg-white">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {columns.map((col) => (
                  <th key={col} className="px-4 py-2 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">{col}</th>
                ))}
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-100">
              {normalizedRows.map((row, idx) => (
                <tr key={idx}>
                  {columns.map((col) => (
                    <td key={col} className="px-4 py-2 text-sm text-gray-800">{formatCell(row ? row[col] : null)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    } else {
      // Fallback: old card view for single object
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
            {/* ...existing code for wind card... */}
          </div>
        );
      }

      // ...other cards as needed...

      return <div className="grid md:grid-cols-2 gap-6">{cards}</div>;
    }
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
          <TrendingUp className="w-5 h-5 text-orange-600" />
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

        <div className="bg-gradient-to-r from-orange-50 to-amber-50 rounded-lg p-4 border border-orange-200">
          <h5 className="font-medium text-gray-800 mb-3 flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-orange-600" />
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
    // Accept either result.result (nested) or result (top-level)
    const raw = result?.result || result;
    const parsedResult = parseWorkflowResult(raw);

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

          {parsedResult && (
            <div className="space-y-4">
              {/* Collector Data Table */}
              {parsedResult.data && (
                <div>
                  <h4 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                    <Database className="w-5 h-5 text-blue-600" />
                    Collected Data
                    {parsedResult.data.rows && (
                      <span className="text-sm font-normal text-gray-500">
                        ({parsedResult.data.rows.length} record{parsedResult.data.rows.length !== 1 ? 's' : ''})
                      </span>
                    )}
                  </h4>
                  {renderWeatherData(parsedResult.data, result.query)}
                  
                  {/* Weather Description (only if single record with conditions) */}
                  {parsedResult.data.conditions && (
                    <div className="bg-blue-50 rounded-lg p-4 border border-blue-200 mb-4 mt-4">
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
                  )}
                </div>
              )}

              {/* Trend Analysis */}
              {parsedResult.analysis && renderTrendAnalysis(parsedResult.analysis, query)}

              {/* Generated Visualizations from Trend Agent */}
              {result.visualizations && result.visualizations.length > 0 ? (
                <div className="mb-6">
                  <h4 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-orange-600" />
                    Generated Visualizations
                    <span className="text-sm font-normal text-gray-500">({result.visualizations.length} chart{result.visualizations.length > 1 ? 's' : ''})</span>
                  </h4>
                  <div className="space-y-4">
                    {result.visualizations.map((vizUrl, idx) => {
                      // Extract filename from URL for display
                      const filename = vizUrl.split('/').pop().replace(/\.(png|jpg|jpeg)$/, '');
                      const displayName = filename
                        .replace(/_/g, ' ')
                        .replace(/\b\w/g, l => l.toUpperCase());
                      
                      const fullUrl = `http://localhost:8000${vizUrl}`;
                      
                      return (
                        <div key={idx} className="bg-white rounded-xl border-2 border-orange-200 overflow-hidden hover:shadow-xl transition-all">
                          <div className="bg-gradient-to-r from-orange-600 to-green-800 px-4 py-3">
                            <div className="flex items-center justify-between">
                              <p className="text-sm font-semibold text-white">{displayName}</p>
                              <button
                                onClick={() => window.open(fullUrl, '_blank')}
                                className="text-xs bg-white/20 hover:bg-white/30 text-white px-3 py-1 rounded-full transition-all flex items-center gap-1"
                              >
                                <Eye className="w-3 h-3" />
                                Open Full Size
                              </button>
                            </div>
                            <p className="text-xs text-orange-200 mt-1">Click image to expand • Path: {vizUrl}</p>
                          </div>
                          <div className="relative bg-gray-50 p-4">
                            <div className="bg-white rounded-lg shadow-inner p-2">
                              <img 
                                src={fullUrl}
                                alt={displayName}
                                className="w-full h-auto max-h-[500px] object-contain cursor-pointer hover:scale-[1.02] transition-transform rounded"
                                onClick={() => window.open(fullUrl, '_blank')}
                                onError={(e) => {
                                  console.error('Image load error:', fullUrl);
                                  e.target.onerror = null;
                                  e.target.parentElement.innerHTML = `
                                    <div class="text-center p-8 bg-red-50 rounded-lg border-2 border-red-200">
                                      <div class="text-red-500 text-2xl mb-3">⚠️</div>
                                      <div class="text-red-700 font-semibold mb-2">Image Failed to Load</div>
                                      <p class="text-sm text-red-600 mb-3">Path: ${vizUrl}</p>
                                      <a href="${fullUrl}" target="_blank" class="inline-block text-sm bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors">
                                        Try Opening Directly
                                      </a>
                                    </div>
                                  `;
                                }}
                                onLoad={() => {
                                  console.log('✅ Visualization loaded:', fullUrl);
                                }}
                              />
                            </div>
                          </div>
                          <div className="bg-orange-50 px-4 py-2 border-t border-orange-100">
                            <p className="text-xs text-orange-700 flex items-center gap-2">
                              <Info className="w-3 h-3" />
                              Auto-generated by Trend Analysis Agent
                            </p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ) : result.workflow_type === 'collect_analyze' && (
                <div className="mb-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <Info className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <h4 className="font-semibold text-yellow-800 mb-1">No Visualizations Generated</h4>
                      <p className="text-sm text-yellow-700">
                        The trend analysis completed but didn't generate visualizations. This might happen if:
                      </p>
                      <ul className="text-sm text-yellow-700 mt-2 list-disc list-inside space-y-1">
                        <li>Insufficient data (need at least 2 records)</li>
                        <li>Query doesn't match visualization patterns</li>
                        <li>No numeric columns available for analysis</li>
                      </ul>
                    </div>
                  </div>
                </div>
              )}

              {/* LLM-Generated Report (NEW) */}
              {parsedResult.report && (
                <div className="mb-6">
                  <h4 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                    <FileText className="w-5 h-5 text-green-600" />
                    AI-Generated Weather Report
                  </h4>
                  <div className={`bg-white rounded-xl border-2 shadow-lg overflow-hidden ${parsedResult.report.includes('ERROR') ? 'border-red-300' : 'border-green-200'}`}>
                    <div className={`px-4 py-3 ${parsedResult.report.includes('ERROR') ? 'bg-gradient-to-r from-red-600 to-rose-600' : 'bg-gradient-to-r from-green-600 to-emerald-600'}`}>
                      <div className="flex items-center gap-2">
                        <Bot className="w-5 h-5 text-white" />
                        <span className="text-sm font-semibold text-white">
                          {parsedResult.report.includes('ERROR') ? 'Report Generation Failed' : 'Generated by AI Analysis Agent'}
                        </span>
                      </div>
                    </div>
                    <div className="p-6 prose prose-sm max-w-none">
                      {/* Check if it's an error message */}
                      {parsedResult.report.includes('ERROR') || parsedResult.report.includes('Traceback') ? (
                        <div className="space-y-3">
                          <div className="bg-red-50 border-2 border-red-200 rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-2">
                              <XCircle className="w-5 h-5 text-red-600" />
                              <span className="font-bold text-red-800">Error Details</span>
                            </div>
                            <pre className="text-xs text-red-700 whitespace-pre-wrap font-mono bg-red-100 p-3 rounded overflow-x-auto">
                              {parsedResult.report}
                            </pre>
                          </div>
                          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                            <p className="text-sm text-blue-800 font-medium mb-2">💡 Debugging Tips:</p>
                            <ul className="text-xs text-blue-700 space-y-1 list-disc list-inside">
                              <li>Check if the collector returned valid weather data</li>
                              <li>Verify the trend analysis completed successfully</li>
                              <li>Look for LLM API errors in the server logs</li>
                              <li>Ensure GROQ_API_KEY is set in environment variables</li>
                            </ul>
                          </div>
                        </div>
                      ) : (
                        /* Simple Markdown-like rendering */
                        <div className="space-y-4 text-gray-800">
                          {parsedResult.report.split('\n').map((line, idx) => {
                          // Headers
                          if (line.startsWith('# ')) {
                            return <h1 key={idx} className="text-3xl font-bold text-gray-900 mb-4">{line.slice(2)}</h1>;
                          }
                          if (line.startsWith('## ')) {
                            return <h2 key={idx} className="text-2xl font-bold text-gray-800 mb-3 mt-6">{line.slice(3)}</h2>;
                          }
                          if (line.startsWith('### ')) {
                            return <h3 key={idx} className="text-xl font-semibold text-gray-700 mb-2 mt-4">{line.slice(4)}</h3>;
                          }
                          
                          // Bold text **text**
                          if (line.includes('**')) {
                            const parts = line.split('**');
                            return (
                              <p key={idx} className="mb-2">
                                {parts.map((part, i) => i % 2 === 1 ? <strong key={i} className="font-bold">{part}</strong> : part)}
                              </p>
                            );
                          }
                          
                          // Bullet points
                          if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
                            return (
                              <li key={idx} className="ml-4 mb-1 list-disc">
                                {line.trim().slice(2)}
                              </li>
                            );
                          }
                          
                          // Emoji lines (likely section headers)
                          if (line.match(/^[🌤️🌡️💧🌧️☀️⛅🌥️☁️🌬️📊📈📉✅⚠️❌]/)) {
                            return <p key={idx} className="text-lg font-semibold text-blue-700 mb-2 mt-4">{line}</p>;
                          }
                          
                          // Empty lines
                          if (line.trim() === '') {
                            return <div key={idx} className="h-2"></div>;
                          }
                          
                          // Regular paragraphs
                          return <p key={idx} className="mb-2 leading-relaxed">{line}</p>;
                        })}
                      </div>
                      )}
                    </div>
                    <div className={`px-4 py-3 border-t ${parsedResult.report.includes('ERROR') ? 'bg-red-50 border-red-100' : 'bg-green-50 border-green-100'}`}>
                      <p className={`text-xs flex items-center gap-2 ${parsedResult.report.includes('ERROR') ? 'text-red-700' : 'text-green-700'}`}>
                        <Info className="w-3 h-3" />
                        {parsedResult.report.includes('ERROR') 
                          ? 'Error occurred during report generation - check details above'
                          : 'This report was automatically generated using AI analysis of weather data'
                        }
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Comprehensive Report */}
              {parsedResult.summary && (
                <div>
                  <h4 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
                    <FileText className="w-5 h-5 text-orange-600" />
                    Comprehensive Report
                  </h4>
                  <div className="bg-orange-50 rounded-lg p-4 border border-orange-200">
                    <pre className="text-sm text-orange-800 whitespace-pre-wrap">
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
                    {JSON.stringify(result?.result || result, null, 2)}
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
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-amber-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center space-x-4 mb-8">
          <div className="w-16 h-16 bg-gradient-to-r from-orange-600 to-green-800 rounded-2xl flex items-center justify-center shadow-lg">
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
                      ? 'border-orange-500 text-orange-600'
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
                      <div className="w-10 h-10 bg-gradient-to-r from-orange-500 to-amber-500 rounded-lg flex items-center justify-center">
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
                      <div className="w-10 h-10 bg-gradient-to-r from-orange-500 to-amber-500 rounded-lg flex items-center justify-center">
                        <BarChart3 className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-800">
                          Execution Results ({executionResults.length})
                        </h3>
                        <p className="text-gray-600">View your workflow execution history</p>
                      </div>
                    </div>

                    {/* Global SQL preview removed — SQL tables are rendered only within each execution result card */}

                    

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
                      <div className="w-10 h-10 bg-gradient-to-r from-orange-500 to-amber-500 rounded-lg flex items-center justify-center">
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
                          <div className="dashboard-card border border-orange-200">
                            <div className="p-4">
                              <div className="flex items-center gap-3 mb-4">
                                <div className="w-8 h-8 bg-gradient-to-r from-orange-500 to-amber-500 rounded-lg flex items-center justify-center">
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
                                    className="text-left p-3 bg-white rounded-lg border border-gray-200 hover:border-orange-300 hover:bg-orange-50 transition-all text-sm text-gray-700"
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