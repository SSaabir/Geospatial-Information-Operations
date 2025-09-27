import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Search, Eye, BarChart3, FileText, Clock, CheckCircle, XCircle, Loader2 } from 'lucide-react';

const OrchestratorDashboard = () => {
  const { apiCall } = useAuth();
  const [query, setQuery] = useState('');
  const [workflowPreview, setWorkflowPreview] = useState(null);
  const [executionResults, setExecutionResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('query');

  // Workflow type icons and colors
  const workflowConfig = {
    data_view: {
      icon: Eye,
      color: 'bg-blue-500',
      lightColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      textColor: 'text-blue-700'
    },
    collect_analyze: {
      icon: BarChart3,
      color: 'bg-green-500',
      lightColor: 'bg-green-50',
      borderColor: 'border-green-200',
      textColor: 'text-green-700'
    },
    full_summary: {
      icon: FileText,
      color: 'bg-purple-500',
      lightColor: 'bg-purple-50',
      borderColor: 'border-purple-200',
      textColor: 'text-purple-700'
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
        return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
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
      <div className={`p-4 rounded-lg border-2 ${config.lightColor} ${config.borderColor} mb-4`}>
        <div className="flex items-center gap-3 mb-2">
          <div className={`p-2 rounded-full ${config.color}`}>
            <Icon className="w-4 h-4 text-white" />
          </div>
          <h3 className={`font-semibold ${config.textColor}`}>
            {workflowPreview.workflow_type.replace('_', ' ').toUpperCase()} Workflow
          </h3>
        </div>
        
        <p className="text-gray-600 mb-3">{workflowPreview.description}</p>
        
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="font-medium text-gray-700">Agents:</span>
            <div className="flex flex-wrap gap-1 mt-1">
              {workflowPreview.estimated_agents.map((agent, idx) => (
                <span key={idx} className="px-2 py-1 bg-gray-100 rounded text-xs">
                  {agent}
                </span>
              ))}
            </div>
          </div>
          <div>
            <span className="font-medium text-gray-700">Est. Duration:</span>
            <p className="text-gray-600 mt-1">{workflowPreview.estimated_duration}</p>
          </div>
        </div>
      </div>
    );
  };

  const renderExecutionResult = (result) => {
    const config = workflowConfig[result.workflow_type] || workflowConfig.data_view;
    const Icon = config.icon;

    return (
      <div key={result.request_id} className="border rounded-lg p-4 mb-4 bg-white shadow-sm">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-full ${config.color}`}>
              <Icon className="w-4 h-4 text-white" />
            </div>
            <div>
              <h4 className="font-medium text-gray-900">{result.query}</h4>
              <p className="text-sm text-gray-500">
                {new Date(result.timestamp).toLocaleString()}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            {getStatusIcon(result.status)}
            <span className="text-sm font-medium capitalize">{result.status}</span>
            {result.status === 'processing' && (
              <button
                onClick={() => checkAsyncStatus(result.request_id)}
                className="ml-2 px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
              >
                Refresh
              </button>
            )}
          </div>
        </div>

        {result.execution_time_ms && (
          <p className="text-sm text-gray-600 mb-2">
            Execution time: {result.execution_time_ms}ms
          </p>
        )}

        {result.error && (
          <div className="bg-red-50 border border-red-200 rounded p-3 mb-3">
            <p className="text-red-700 text-sm font-medium">Error:</p>
            <p className="text-red-600 text-sm">{result.error}</p>
          </div>
        )}

        {result.result && (
          <div className="bg-gray-50 rounded p-3">
            <p className="text-sm font-medium text-gray-700 mb-2">Results:</p>
            <pre className="text-xs text-gray-600 overflow-x-auto">
              {JSON.stringify(result.result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Orchestrator Dashboard
        </h1>
        <p className="text-gray-600">
          Submit natural language queries to analyze geospatial and climate data through intelligent agent workflows.
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="flex gap-8">
          {['query', 'results', 'samples'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-2 px-1 border-b-2 font-medium text-sm capitalize ${
                activeTab === tab
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab}
            </button>
          ))}
        </nav>
      </div>

      {/* Query Tab */}
      {activeTab === 'query' && (
        <div>
          <div className="bg-white rounded-lg border p-6 mb-6">
            <div className="flex items-center gap-2 mb-4">
              <Search className="w-5 h-5 text-gray-400" />
              <label className="text-sm font-medium text-gray-700">
                Enter your query
              </label>
            </div>
            
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask about climate data, trends, or request reports... (e.g., 'Show me temperature trends for the past month')"
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
              rows={3}
            />

            {renderWorkflowPreview()}

            <div className="flex gap-3">
              <button
                onClick={() => executeWorkflow(false)}
                disabled={!query.trim() || isLoading}
                className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
                Execute Now
              </button>
              
              <button
                onClick={() => executeWorkflow(true)}
                disabled={!query.trim() || isLoading}
                className="flex-1 border border-gray-300 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Execute Async
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Results Tab */}
      {activeTab === 'results' && (
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Execution Results ({executionResults.length})
          </h2>
          
          {executionResults.length === 0 ? (
            <div className="text-center py-12 bg-gray-50 rounded-lg">
              <Search className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No workflow executions yet.</p>
              <p className="text-sm text-gray-400">Submit a query to see results here.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {executionResults.map(renderExecutionResult)}
            </div>
          )}
        </div>
      )}

      {/* Sample Queries Tab */}
      {activeTab === 'samples' && (
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Sample Queries</h2>
          
          {Object.entries(sampleQueries).map(([workflowType, queries]) => {
            const config = workflowConfig[workflowType];
            const Icon = config.icon;
            
            return (
              <div key={workflowType} className={`p-4 rounded-lg ${config.lightColor} mb-6`}>
                <div className="flex items-center gap-3 mb-3">
                  <div className={`p-2 rounded-full ${config.color}`}>
                    <Icon className="w-4 h-4 text-white" />
                  </div>
                  <h3 className={`font-semibold ${config.textColor}`}>
                    {workflowType.replace('_', ' ').toUpperCase()} Workflow
                  </h3>
                </div>
                
                <div className="grid gap-2">
                  {queries.map((sampleQuery, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setQuery(sampleQuery);
                        setActiveTab('query');
                      }}
                      className="text-left p-3 bg-white rounded border hover:border-gray-300 transition-colors"
                    >
                      <p className="text-sm text-gray-800">{sampleQuery}</p>
                    </button>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default OrchestratorDashboard;