import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Bot, User, Plus, Trash2, Edit2, Check, X, Menu, Clock, Download, Share2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

function WorkflowChat() {
  const { apiCall, user } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [editingConvId, setEditingConvId] = useState(null);
  const [editingTitle, setEditingTitle] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Load conversations from localStorage on mount
  useEffect(() => {
    loadConversations();
    // Clean up old localStorage entries
    cleanupOldStorage();
  }, [user]);

  const cleanupOldStorage = () => {
    if (!user) return;
    
    try {
      // Remove any oversized conversation data
      const storageKey = `conversations_${user.id}`;
      const data = localStorage.getItem(storageKey);
      
      if (data && data.length > 5000000) { // 5MB limit
        console.warn('Conversation data too large, clearing...');
        localStorage.removeItem(storageKey);
      }
      
      // Clean up any other old conversation keys
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith('conversations_') && key !== storageKey) {
          // Remove conversations from other users or old format
          localStorage.removeItem(key);
        }
      }
    } catch (error) {
      console.error('Error cleaning up storage:', error);
    }
  };

  // Save conversations to localStorage whenever they change (with size management)
  useEffect(() => {
    if (user && conversations.length > 0) {
      try {
        // Create a lightweight version of conversations for storage
        const lightConversations = conversations.map(conv => ({
          id: conv.id,
          title: conv.title,
          createdAt: conv.createdAt,
          updatedAt: conv.updatedAt,
          // Only keep last 20 messages per conversation to save space
          messages: (conv.messages || []).slice(-20).map(msg => ({
            role: msg.role,
            content: msg.content.slice(0, 5000), // Limit content to 5000 chars
            isError: msg.isError,
            isQuotaError: msg.isQuotaError,
            workflow_type: msg.workflow_type,
            timestamp: msg.timestamp
            // Remove large data objects, visualizations
          }))
        }));
        
        // Keep only last 10 conversations
        const recentConversations = lightConversations.slice(-10);
        
        localStorage.setItem(`conversations_${user.id}`, JSON.stringify(recentConversations));
      } catch (error) {
        if (error.name === 'QuotaExceededError') {
          console.warn('localStorage quota exceeded, clearing old conversations');
          // Clear old conversations and try again with just the current one
          try {
            const currentConv = conversations.find(c => c.id === currentConversationId);
            if (currentConv) {
              const minimal = [{
                id: currentConv.id,
                title: currentConv.title,
                createdAt: currentConv.createdAt,
                updatedAt: currentConv.updatedAt,
                messages: (currentConv.messages || []).slice(-10).map(msg => ({
                  role: msg.role,
                  content: msg.content.slice(0, 2000),
                  timestamp: msg.timestamp
                }))
              }];
              localStorage.setItem(`conversations_${user.id}`, JSON.stringify(minimal));
              // Update conversations to only keep current
              setConversations(minimal);
            }
          } catch (e) {
            console.error('Failed to save even minimal conversation data:', e);
            // Last resort: clear all conversation data
            localStorage.removeItem(`conversations_${user.id}`);
          }
        } else {
          console.error('Failed to save conversations:', error);
        }
      }
    }
  }, [conversations, user, currentConversationId]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Focus input when conversation changes
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, [currentConversationId]);

  const loadConversations = () => {
    if (!user) return;
    
    const saved = localStorage.getItem(`conversations_${user.id}`);
    if (saved) {
      const parsed = JSON.parse(saved);
      setConversations(parsed);
      
      // Load the most recent conversation
      if (parsed.length > 0) {
        const latest = parsed[0];
        setCurrentConversationId(latest.id);
        setMessages(latest.messages || []);
      } else {
        createNewConversation();
      }
    } else {
      createNewConversation();
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const createNewConversation = () => {
    const newConv = {
      id: Date.now().toString(),
      title: 'New Chat',
      messages: [{
        role: 'assistant',
        content: `Hi! I'm your AI workflow assistant. I can help you with weather data in different formats:

📊 **Data View** - Get tabular data (e.g., "Show me the latest weather data")
📈 **Analysis** - Get charts and visualizations (e.g., "Analyze temperature trends")
📄 **Reports** - Get comprehensive reports with download options (e.g., "Generate summary report")
🔮 **Predictions** - Forecast future weather (e.g., "Predict tomorrow's weather")

Try clicking the quick action buttons below or type your own query!`,
        timestamp: new Date().toISOString()
      }],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    setConversations(prev => [newConv, ...prev]);
    setCurrentConversationId(newConv.id);
    setMessages(newConv.messages);
  };

  const deleteConversation = (convId) => {
    setConversations(prev => prev.filter(c => c.id !== convId));
    
    if (convId === currentConversationId) {
      const remaining = conversations.filter(c => c.id !== convId);
      if (remaining.length > 0) {
        setCurrentConversationId(remaining[0].id);
        setMessages(remaining[0].messages);
      } else {
        createNewConversation();
      }
    }
  };

  const clearAllConversations = () => {
    if (window.confirm('⚠️ Clear all conversations? This will free up storage space but cannot be undone.')) {
      setConversations([]);
      setMessages([]);
      setCurrentConversationId(null);
      if (user) {
        localStorage.removeItem(`conversations_${user.id}`);
      }
      // Create a fresh conversation
      setTimeout(() => createNewConversation(), 100);
    }
  };

  const updateConversationTitle = (convId, newTitle) => {
    setConversations(prev => 
      prev.map(c => c.id === convId ? { ...c, title: newTitle } : c)
    );
    setEditingConvId(null);
  };

  const switchConversation = (convId) => {
    const conv = conversations.find(c => c.id === convId);
    if (conv) {
      setCurrentConversationId(convId);
      setMessages(conv.messages);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date().toISOString()
    };

    // Add user message immediately
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput('');
    setIsLoading(true);

    // Update conversation title if it's the first user message
    const currentConv = conversations.find(c => c.id === currentConversationId);
    if (currentConv && currentConv.title === 'New Chat') {
      const title = userMessage.content.slice(0, 50) + (userMessage.content.length > 50 ? '...' : '');
      setConversations(prev =>
        prev.map(c => c.id === currentConversationId ? { ...c, title } : c)
      );
    }

    try {
      // Call the orchestrator API
      const response = await apiCall('/orchestrator/execute', {
        method: 'POST',
        body: JSON.stringify({
          query: userMessage.content,
          async_execution: false,
          include_visualizations: true
        })
      });

      // Extract the response - API returns: result, visualizations, workflow_type, execution_time_ms
      const resultText = response.result?.workflow_output || response.result?.summary || response.result?.message || 'Analysis complete! See details below.';
      
      const assistantMessage = {
        role: 'assistant',
        content: resultText || 'Task completed successfully!',
        data: response.result || null,
        visualizations: response.visualizations || [],
        workflow_type: response.workflow_type || null,
        execution_time: response.execution_time_ms ? (response.execution_time_ms / 1000).toFixed(2) : null,
        timestamp: new Date().toISOString()
      };

      const finalMessages = [...updatedMessages, assistantMessage];
      setMessages(finalMessages);

      // Update conversation with new messages
      setConversations(prev =>
        prev.map(c =>
          c.id === currentConversationId
            ? { ...c, messages: finalMessages, updatedAt: new Date().toISOString() }
            : c
        )
      );

    } catch (error) {
      console.error('Workflow error:', error);
      
      // Check if it's a quota exceeded error (429 status)
      let errorContent = '';
      let isQuotaError = false;
      
      if (error.status === 429 || error.message?.includes('quota') || error.message?.includes('Quota') || error.message?.includes('limit exceeded')) {
        isQuotaError = true;
        errorContent = `🚫 **API Quota Exceeded**

You've reached your monthly API limit. Your current plan has limited API calls per month.

**What you can do:**
- ⬆️ Upgrade to a higher tier plan for more API calls
- 📊 Check your usage in Settings
- ⏰ Wait for your quota to reset next month

Visit our [Pricing Page](/pricing) to upgrade your plan and continue using the service.`;
      } else {
        errorContent = error.message || 'Unable to process your request. Please try again.';
      }
      
      const errorMessage = {
        role: 'assistant',
        content: errorContent,
        isError: true,
        isQuotaError: isQuotaError,
        timestamp: new Date().toISOString()
      };

      const finalMessages = [...updatedMessages, errorMessage];
      setMessages(finalMessages);

      setConversations(prev =>
        prev.map(c =>
          c.id === currentConversationId
            ? { ...c, messages: finalMessages, updatedAt: new Date().toISOString() }
            : c
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const currentConv = conversations.find(c => c.id === currentConversationId);

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div
        className={`${
          isSidebarOpen ? 'w-80' : 'w-0'
        } bg-gray-900 text-white transition-all duration-300 overflow-hidden flex flex-col`}
      >
        {/* Sidebar Header */}
        <div className="p-4 border-b border-gray-700 space-y-2">
          <button
            onClick={createNewConversation}
            className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-blue-600 to-orange-600 hover:from-blue-700 hover:to-orange-700 text-white px-4 py-3 rounded-lg transition-all font-medium"
          >
            <Plus className="w-5 h-5" />
            New Chat
          </button>
          
          {/* Clear All Button */}
          {conversations.length > 1 && (
            <button
              onClick={clearAllConversations}
              className="w-full flex items-center justify-center gap-2 bg-red-600/20 hover:bg-red-600/30 text-red-400 px-3 py-2 rounded-lg transition-all text-sm border border-red-600/30"
              title="Clear all conversations to free up storage"
            >
              <Trash2 className="w-4 h-4" />
              Clear All ({conversations.length})
            </button>
          )}
        </div>

        {/* Conversations List */}
        <div className="flex-1 overflow-y-auto p-2">
          {conversations.map((conv) => (
            <div
              key={conv.id}
              className={`group relative mb-1 rounded-lg transition-colors ${
                conv.id === currentConversationId
                  ? 'bg-gray-800'
                  : 'hover:bg-gray-800/50'
              }`}
            >
              {editingConvId === conv.id ? (
                <div className="flex items-center gap-2 p-3">
                  <input
                    type="text"
                    value={editingTitle}
                    onChange={(e) => setEditingTitle(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') updateConversationTitle(conv.id, editingTitle);
                      if (e.key === 'Escape') setEditingConvId(null);
                    }}
                    className="flex-1 bg-gray-700 text-white px-2 py-1 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                    autoFocus
                  />
                  <button
                    onClick={() => updateConversationTitle(conv.id, editingTitle)}
                    className="p-1 hover:bg-gray-700 rounded"
                  >
                    <Check className="w-4 h-4 text-green-400" />
                  </button>
                  <button
                    onClick={() => setEditingConvId(null)}
                    className="p-1 hover:bg-gray-700 rounded"
                  >
                    <X className="w-4 h-4 text-red-400" />
                  </button>
                </div>
              ) : (
                <div className="w-full text-left p-3 flex items-start justify-between gap-2 cursor-pointer"
                  onClick={() => switchConversation(conv.id)}
                >
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{conv.title}</p>
                    <p className="text-xs text-gray-400 mt-0.5">
                      {formatTime(conv.updatedAt)}
                    </p>
                  </div>
                  <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setEditingConvId(conv.id);
                        setEditingTitle(conv.title);
                      }}
                      className="p-1 hover:bg-gray-700 rounded"
                      title="Rename"
                    >
                      <Edit2 className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        if (confirm('Delete this conversation?')) {
                          deleteConversation(conv.id);
                        }
                      }}
                      className="p-1 hover:bg-gray-700 rounded"
                      title="Delete"
                    >
                      <Trash2 className="w-3.5 h-3.5 text-red-400" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* User Info */}
        <div className="p-4 border-t border-gray-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-orange-500 flex items-center justify-center">
              <User className="w-5 h-5" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user?.username || user?.email}</p>
              <p className="text-xs text-gray-400 capitalize">{user?.tier || 'free'} Plan</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <Menu className="w-5 h-5 text-gray-600" />
            </button>
            <div>
              <h1 className="text-xl font-bold text-gray-900">AI Workflow Assistant</h1>
              <p className="text-sm text-gray-500">
                {user?.tier === 'free' ? '5 queries/month' : user?.tier === 'researcher' ? '5,000 queries/month' : 'Unlimited queries'}
              </p>
            </div>
          </div>
          
          {currentConv && (
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-500">
                {currentConv.messages.length - 1} messages
              </span>
            </div>
          )}
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-4 py-6">
          <div className="max-w-3xl mx-auto space-y-6">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {/* Avatar for Assistant */}
                {message.role === 'assistant' && (
                  <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                    message.isQuotaError ? 'bg-orange-500' : message.isError ? 'bg-red-500' : 'bg-gradient-to-r from-orange-500 to-orange-600'
                  }`}>
                    {message.isQuotaError ? (
                      <span className="text-white text-lg">🚫</span>
                    ) : (
                      <Bot className="w-5 h-5 text-white" />
                    )}
                  </div>
                )}

                {/* Message Content */}
                <div className={`flex-1 max-w-2xl ${message.role === 'user' ? 'text-right' : 'text-left'}`}>
                  <div className={`inline-block rounded-2xl px-6 py-4 ${
                    message.role === 'user'
                      ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white'
                      : message.isQuotaError
                      ? 'bg-orange-50 text-orange-900 border-2 border-orange-300'
                      : message.isError
                      ? 'bg-red-50 text-red-900 border border-red-200'
                      : 'bg-white text-gray-800 border border-gray-200 shadow-sm'
                  }`}>
                    <p className="text-sm whitespace-pre-wrap leading-relaxed">{message.content}</p>
                    
                    {/* Add upgrade button for quota errors */}
                    {message.isQuotaError && (
                      <div className="mt-4 pt-4 border-t border-orange-200">
                        <a
                          href="/pricing"
                          className="inline-block px-6 py-2 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-lg font-semibold hover:from-orange-600 hover:to-orange-700 transition-all"
                        >
                          ⬆️ Upgrade Plan
                        </a>
                      </div>
                    )}
                    
                    {/* Render based on workflow type */}
                    {message.role === 'assistant' && !message.isError && (() => {
                      // Extract table data from nested structure
                      let tableData = null;
                      
                      if (message.workflow_type === 'data_view' && message.data) {
                        // Try different possible data locations
                        if (message.data.collector_data) {
                          try {
                            const collectorData = typeof message.data.collector_data === 'string' 
                              ? JSON.parse(message.data.collector_data)
                              : message.data.collector_data;
                            tableData = collectorData.data?.rows || collectorData.rows;
                          } catch (e) {
                            console.error('Failed to parse collector_data:', e);
                          }
                        } else if (message.data.data?.rows) {
                          tableData = message.data.data.rows;
                        } else if (Array.isArray(message.data.data)) {
                          tableData = message.data.data;
                        } else if (Array.isArray(message.data)) {
                          tableData = message.data;
                        }
                      }

                      return (
                        <>
                          {/* TABLE VIEW - For data_view workflow */}
                          {message.workflow_type === 'data_view' && tableData && Array.isArray(tableData) && tableData.length > 0 && (
                            <div className="mt-4 overflow-x-auto">
                              <div className="inline-block min-w-full align-middle">
                                <div className="overflow-hidden border border-gray-200 rounded-lg shadow-sm">
                                  <table className="min-w-full divide-y divide-gray-200">
                                    <thead className="bg-gradient-to-r from-gray-50 to-gray-100">
                                      <tr>
                                        {Object.keys(tableData[0] || {}).map((header) => (
                                          <th
                                            key={header}
                                            className="px-4 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider border-r border-gray-200 last:border-r-0"
                                          >
                                            {header.replace(/_/g, ' ')}
                                          </th>
                                        ))}
                                      </tr>
                                    </thead>
                                    <tbody className="bg-white divide-y divide-gray-200">
                                      {tableData.slice(0, 10).map((row, rowIdx) => (
                                        <tr key={rowIdx} className="hover:bg-blue-50 transition-colors">
                                          {Object.values(row).map((cell, cellIdx) => (
                                            <td key={cellIdx} className="px-4 py-3 text-sm text-gray-900 border-r border-gray-100 last:border-r-0">
                                              {cell !== null && cell !== undefined 
                                                ? typeof cell === 'boolean' 
                                                  ? (cell ? '✓' : '✗')
                                                  : String(cell)
                                                : '-'}
                                            </td>
                                          ))}
                                        </tr>
                                      ))}
                                    </tbody>
                                  </table>
                                  {tableData.length > 10 && (
                                    <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-4 py-3 border-t border-gray-200 text-xs text-gray-600 font-medium">
                                      📊 Showing 10 of {tableData.length} records
                                    </div>
                                  )}
                                </div>
                              </div>
                            </div>
                          )}

                        {/* TREND ANALYSIS VIEW - For analyze_trends workflow */}
                        {message.workflow_type === 'analyze_trends' && message.data && (
                          <div className="mt-4 space-y-4">
                            {/* Trend Statistics */}
                            {message.data.trend_analysis && (() => {
                              try {
                                let trendData;
                                if (typeof message.data.trend_analysis === 'string') {
                                  // Try to parse as JSON (handle Python dict format with single quotes)
                                  try {
                                    trendData = JSON.parse(message.data.trend_analysis.replace(/'/g, '"'));
                                  } catch (parseError) {
                                    console.warn('Failed to parse trend_analysis, data may be truncated:', parseError);
                                    // Return null to skip rendering this section
                                    return null;
                                  }
                                } else {
                                  trendData = message.data.trend_analysis;
                                }
                                
                                return (
                                  <div className="bg-gradient-to-r from-orange-50 to-pink-50 rounded-lg p-4 border border-orange-200">
                                    <h3 className="text-sm font-bold text-gray-900 mb-3 flex items-center gap-2">
                                      <span className="w-1 h-4 bg-orange-600 rounded"></span>
                                      Trend Analysis Summary
                                    </h3>
                                    
                                    {trendData.date_range && (
                                      <div className="mb-3 text-xs text-gray-600">
                                        📅 <strong>Period:</strong> {trendData.date_range.start} to {trendData.date_range.end} ({trendData.data_points} data points)
                                      </div>
                                    )}
                                    
                                    <div className="grid grid-cols-2 gap-3">
                                      {Object.entries(trendData).filter(([key]) => 
                                        !['date_range', 'data_points'].includes(key)
                                      ).map(([key, stats]) => (
                                        <div key={key} className="bg-white rounded-lg p-3 border border-gray-200">
                                          <p className="text-xs font-bold text-orange-700 uppercase mb-2">
                                            {key.replace(/_/g, ' ')}
                                          </p>
                                          {typeof stats === 'object' && stats !== null && (
                                            <div className="space-y-1 text-xs">
                                              {stats.mean !== undefined && (
                                                <div className="flex justify-between">
                                                  <span className="text-gray-600">Mean:</span>
                                                  <span className="font-semibold text-gray-900">{Number(stats.mean).toFixed(2)}</span>
                                                </div>
                                              )}
                                              {stats.min !== undefined && stats.max !== undefined && (
                                                <div className="flex justify-between">
                                                  <span className="text-gray-600">Range:</span>
                                                  <span className="font-semibold text-gray-900">
                                                    {Number(stats.min).toFixed(2)} - {Number(stats.max).toFixed(2)}
                                                  </span>
                                                </div>
                                              )}
                                              {stats.std !== undefined && stats.std > 0 && (
                                                <div className="flex justify-between">
                                                  <span className="text-gray-600">Std Dev:</span>
                                                  <span className="font-semibold text-gray-900">{Number(stats.std).toFixed(2)}</span>
                                                </div>
                                              )}
                                            </div>
                                          )}
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                );
                              } catch (e) {
                                console.error('Failed to parse trend_analysis:', e);
                                return null;
                              }
                            })()}

                            {/* Data Table */}
                            {(() => {
                              let trendTableData = null;
                              if (message.data.collector_data) {
                                try {
                                  const collectorData = typeof message.data.collector_data === 'string'
                                    ? JSON.parse(message.data.collector_data)
                                    : message.data.collector_data;
                                  trendTableData = collectorData.data?.rows || collectorData;
                                } catch (e) {
                                  console.error('Failed to parse collector_data:', e);
                                }
                              }

                              return trendTableData && typeof trendTableData === 'object' && !Array.isArray(trendTableData) && (
                                <div className="bg-white rounded-lg border-2 border-gray-200 overflow-hidden">
                                  <div className="bg-gradient-to-r from-orange-100 to-pink-100 px-4 py-3 border-b-2 border-orange-300">
                                    <h4 className="text-sm font-bold text-gray-900">📊 Source Data Point</h4>
                                  </div>
                                  <div className="p-4">
                                    <div className="grid grid-cols-2 gap-3">
                                      {Object.entries(trendTableData).map(([key, value]) => (
                                        <div key={key} className="bg-gray-50 rounded p-3 border border-gray-200">
                                          <p className="text-xs font-semibold text-orange-700 uppercase mb-1">
                                            {key.replace(/_/g, ' ')}
                                          </p>
                                          <p className="text-sm text-gray-900 font-medium">
                                            {value !== null && value !== undefined
                                              ? typeof value === 'boolean'
                                                ? (value ? '✓ Yes' : '✗ No')
                                                : String(value)
                                              : '-'}
                                          </p>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                </div>
                              );
                            })()}

                            {/* Visualizations */}
                            {message.data.visualizations && (() => {
                              const vizObj = typeof message.data.visualizations === 'string'
                                ? JSON.parse(message.data.visualizations)
                                : message.data.visualizations;
                              
                              const vizUrls = Object.values(vizObj).filter(v => typeof v === 'string');
                              
                              return vizUrls.length > 0 && (
                                <div className="space-y-3">
                                  <div className="flex items-center gap-2 text-xs font-semibold text-gray-700 uppercase tracking-wider">
                                    <span className="w-2 h-2 bg-orange-500 rounded-full"></span>
                                    Analysis Charts
                                  </div>
                                  {vizUrls.map((vizUrl, idx) => (
                                    <div key={idx} className="bg-white rounded-lg border-2 border-orange-200 p-3 shadow-md">
                                      <img
                                        src={`http://localhost:8000/${vizUrl}`}
                                        alt={`Analysis Chart ${idx + 1}`}
                                        className="w-full rounded"
                                        onError={(e) => {
                                          console.error('Failed to load visualization:', vizUrl);
                                          e.target.style.display = 'none';
                                        }}
                                      />
                                    </div>
                                  ))}
                                </div>
                              );
                            })()}
                          </div>
                        )}

                        {/* IMAGE/VISUALIZATION VIEW - For collect_analyze workflow */}
                        {message.workflow_type === 'collect_analyze' && message.visualizations && message.visualizations.length > 0 && (
                          <div className="mt-4 space-y-4">
                            <div className="flex items-center gap-2 text-xs font-semibold text-gray-700 uppercase tracking-wider">
                              <span className="w-2 h-2 bg-orange-500 rounded-full"></span>
                              Analysis Results
                            </div>
                            {message.visualizations.map((vizUrl, idx) => (
                              <div key={idx} className="bg-white rounded-lg border border-gray-200 p-2">
                                <img
                                  src={`http://localhost:8000${vizUrl}`}
                                  alt={`Analysis ${idx + 1}`}
                                  className="w-full rounded"
                                  onError={(e) => {
                                    console.error('Failed to load visualization:', vizUrl);
                                    e.target.style.display = 'none';
                                  }}
                                />
                              </div>
                            ))}
                          </div>
                        )}

                        {/* COMPREHENSIVE REPORT FORMAT - For generate_report workflow */}
                        {message.workflow_type === 'generate_report' && message.data && (
                          <div className="mt-4 space-y-4">
                            {/* Report Header */}
                            <div className="bg-gradient-to-r from-blue-600 to-orange-600 text-white rounded-t-lg p-4">
                              <h2 className="text-lg font-bold flex items-center gap-2">
                                📊 Weather Analysis Report
                              </h2>
                              <p className="text-sm mt-1 opacity-90">
                                Generated: {message.data.generated_at ? new Date(message.data.generated_at).toLocaleString() : 'Now'}
                              </p>
                            </div>

                            {/* Report Content - Formatted Text */}
                            {message.data.report_content && (
                              <div className="bg-white rounded-lg border-2 border-gray-200 p-6 space-y-4">
                                {message.data.report_content.split('\n').map((line, idx) => {
                                  // Headers (lines with ====)
                                  if (line.includes('====')) return null;
                                  
                                  // Main section headers (📊, 📋, 🔍, 📈, 💡)
                                  if (line.match(/^[📊📋🔍📈💡🎯📅]/)) {
                                    return (
                                      <h3 key={idx} className="text-base font-bold text-gray-900 mt-6 mb-3 pb-2 border-b-2 border-blue-600">
                                        {line}
                                      </h3>
                                    );
                                  }
                                  
                                  // Bullet points
                                  if (line.trim().startsWith('*')) {
                                    return (
                                      <li key={idx} className="ml-4 text-sm text-gray-700 leading-relaxed list-disc list-inside">
                                        {line.trim().substring(1).trim()}
                                      </li>
                                    );
                                  }
                                  
                                  // Bold subheadings (**text:**)
                                  if (line.includes('**') && line.includes(':')) {
                                    const boldText = line.match(/\*\*(.*?)\*\*/)?.[1] || '';
                                    const restText = line.split('**').pop() || '';
                                    return (
                                      <p key={idx} className="text-sm mt-4 mb-2">
                                        <span className="font-bold text-orange-700">{boldText}:</span>
                                        <span className="text-gray-700">{restText}</span>
                                      </p>
                                    );
                                  }
                                  
                                  // Separator lines (---)
                                  if (line.trim() === '---') {
                                    return <hr key={idx} className="my-4 border-gray-300" />;
                                  }
                                  
                                  // Empty lines
                                  if (line.trim() === '') return <div key={idx} className="h-2" />;
                                  
                                  // Regular paragraphs
                                  return (
                                    <p key={idx} className="text-sm text-gray-700 leading-relaxed">
                                      {line}
                                    </p>
                                  );
                                })}
                              </div>
                            )}

                            {/* Data Table */}
                            {(() => {
                              let reportTableData = null;
                              if (message.data.collector_data) {
                                try {
                                  const collectorData = typeof message.data.collector_data === 'string'
                                    ? JSON.parse(message.data.collector_data)
                                    : message.data.collector_data;
                                  reportTableData = collectorData.data?.rows;
                                } catch (e) {
                                  console.error('Failed to parse collector_data:', e);
                                }
                              }

                              return reportTableData && Array.isArray(reportTableData) && reportTableData.length > 0 && (
                                <div className="bg-white rounded-lg border-2 border-gray-200 overflow-hidden">
                                  <div className="bg-gradient-to-r from-gray-100 to-gray-50 px-4 py-3 border-b-2 border-gray-300">
                                    <h4 className="text-sm font-bold text-gray-900">📊 Data Summary</h4>
                                  </div>
                                  <div className="overflow-x-auto">
                                    <table className="min-w-full divide-y divide-gray-200">
                                      <thead className="bg-gray-50">
                                        <tr>
                                          {Object.keys(reportTableData[0] || {}).map((header) => (
                                            <th
                                              key={header}
                                              className="px-4 py-3 text-left text-xs font-bold text-gray-700 uppercase tracking-wider"
                                            >
                                              {header.replace(/_/g, ' ')}
                                            </th>
                                          ))}
                                        </tr>
                                      </thead>
                                      <tbody className="bg-white divide-y divide-gray-200">
                                        {reportTableData.map((row, rowIdx) => (
                                          <tr key={rowIdx} className="hover:bg-blue-50">
                                            {Object.values(row).map((cell, cellIdx) => (
                                              <td key={cellIdx} className="px-4 py-3 text-sm text-gray-900">
                                                {cell !== null && cell !== undefined ? String(cell) : '-'}
                                              </td>
                                            ))}
                                          </tr>
                                        ))}
                                      </tbody>
                                    </table>
                                  </div>
                                </div>
                              );
                            })()}

                            {/* Visualizations */}
                            {message.data.visualizations && (() => {
                              const vizObj = typeof message.data.visualizations === 'string'
                                ? JSON.parse(message.data.visualizations)
                                : message.data.visualizations;
                              const vizUrls = Object.values(vizObj).filter(v => typeof v === 'string');

                              return vizUrls.length > 0 && (
                                <div className="bg-white rounded-lg border-2 border-gray-200 overflow-hidden">
                                  <div className="bg-gradient-to-r from-gray-100 to-gray-50 px-4 py-3 border-b-2 border-gray-300">
                                    <h4 className="text-sm font-bold text-gray-900">📈 Visual Analysis</h4>
                                  </div>
                                  <div className="p-4 space-y-4">
                                    {vizUrls.map((vizUrl, idx) => (
                                      <img
                                        key={idx}
                                        src={`http://localhost:8000/${vizUrl}`}
                                        alt={`Report Chart ${idx + 1}`}
                                        className="w-full rounded-lg shadow-md"
                                        onError={(e) => {
                                          console.error('Failed to load visualization:', vizUrl);
                                          e.target.style.display = 'none';
                                        }}
                                      />
                                    ))}
                                  </div>
                                </div>
                              );
                            })()}

                            {/* Report Footer */}
                            <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-b-lg p-4 border-t-2 border-gray-300">
                              <div className="flex items-center justify-between text-xs text-gray-600">
                                <span>Session: {message.data.session_id || 'N/A'}</span>
                                <span className="flex items-center gap-2">
                                  <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                                  Status: {message.data.compliance_status || 'Complete'}
                                </span>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* REPORT FORMAT - For full_summary workflow */}
                        {message.workflow_type === 'full_summary' && message.data && (
                          <div className="mt-4 space-y-4">
                            <div className="bg-gradient-to-r from-orange-50 to-blue-50 rounded-lg p-4 border border-orange-200">
                              <h3 className="text-sm font-bold text-gray-900 mb-3 flex items-center gap-2">
                                <span className="w-1 h-4 bg-orange-600 rounded"></span>
                                Executive Summary
                              </h3>
                              
                              {/* Summary sections */}
                              {message.data.summary && (
                                <div className="space-y-3">
                                  {Object.entries(message.data.summary).map(([key, value]) => (
                                    <div key={key} className="bg-white rounded p-3 border border-gray-200">
                                      <p className="text-xs font-semibold text-orange-700 uppercase mb-1">
                                        {key.replace(/_/g, ' ')}
                                      </p>
                                      <p className="text-sm text-gray-800">
                                        {typeof value === 'object' && value !== null
                                          ? Object.entries(value).map(([k, v]) => `${k}: ${v}`).join(', ')
                                          : String(value)}
                                      </p>
                                    </div>
                                  ))}
                                </div>
                              )}

                              {/* Visualizations in report */}
                              {message.visualizations && message.visualizations.length > 0 && (
                                <div className="mt-4 grid grid-cols-2 gap-3">
                                  {message.visualizations.map((vizUrl, idx) => (
                                    <div key={idx} className="bg-white rounded border border-gray-200 p-2">
                                      <img
                                        src={`http://localhost:8000${vizUrl}`}
                                        alt={`Chart ${idx + 1}`}
                                        className="w-full rounded"
                                        onError={(e) => {
                                          e.target.style.display = 'none';
                                        }}
                                      />
                                    </div>
                                  ))}
                                </div>
                              )}
                            </div>
                          </div>
                        )}

                        {/* DOCUMENT DOWNLOAD - For all workflows with exportable data */}
                        {message.data && (message.workflow_type === 'full_summary' || message.workflow_type === 'collect_analyze' || message.workflow_type === 'analyze_trends' || message.workflow_type === 'generate_report') && (
                          <div className="mt-4 flex gap-2">
                            <button
                              onClick={() => {
                                const dataStr = JSON.stringify(message.data, null, 2);
                                const dataBlob = new Blob([dataStr], { type: 'application/json' });
                                const url = URL.createObjectURL(dataBlob);
                                const link = document.createElement('a');
                                link.href = url;
                                link.download = `report-${new Date().toISOString().slice(0, 10)}.json`;
                                document.body.appendChild(link);
                                link.click();
                                document.body.removeChild(link);
                                URL.revokeObjectURL(url);
                              }}
                              className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-orange-600 text-white text-xs font-medium rounded-lg hover:from-blue-700 hover:to-orange-700 transition-all shadow-sm"
                            >
                              <Download className="w-4 h-4" />
                              Download Report (JSON)
                            </button>
                            
                            {/* PDF Export via API */}
                            {user?.tier !== 'free' && (
                              <button
                                onClick={async () => {
                                  try {
                                    const accessToken = localStorage.getItem('access_token');
                                    
                                    // Prepare data from current message
                                    const exportData = {
                                      workflow_type: message.workflow_type,
                                      report_content: message.data?.report_content || message.content,
                                      collector_data: message.data?.collector_data,
                                      trend_analysis: message.data?.trend_analysis,
                                      visualizations: message.data?.visualizations,
                                      session_id: message.data?.session_id,
                                      generated_at: message.data?.generated_at || new Date().toISOString()
                                    };
                                    
                                    // Fetch PDF as blob
                                    const response = await fetch('http://localhost:8000/api/reports/export', {
                                      method: 'POST',
                                      headers: {
                                        'Content-Type': 'application/json',
                                        'Authorization': `Bearer ${accessToken}`
                                      },
                                      body: JSON.stringify({
                                        report_type: message.workflow_type || 'custom_report',
                                        format: 'pdf',
                                        workflow_data: exportData,
                                        include_charts: true
                                      })
                                    });

                                    if (!response.ok) {
                                      const errorData = await response.json();
                                      throw new Error(errorData.detail || 'Failed to generate PDF');
                                    }

                                    // Get the blob
                                    const blob = await response.blob();
                                    
                                    // Create download link
                                    const url = window.URL.createObjectURL(blob);
                                    const link = document.createElement('a');
                                    link.href = url;
                                    link.download = `weather_report_${new Date().toISOString().slice(0, 10)}.pdf`;
                                    document.body.appendChild(link);
                                    link.click();
                                    document.body.removeChild(link);
                                    window.URL.revokeObjectURL(url);
                                  } catch (error) {
                                    console.error('PDF export error:', error);
                                    alert(`Failed to generate PDF: ${error.message}`);
                                  }
                                }}
                                className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white text-xs font-medium rounded-lg hover:bg-red-700 transition-all shadow-sm"
                              >
                                <Download className="w-4 h-4" />
                                Export PDF
                              </button>
                            )}
                          </div>
                        )}
                        </>
                      );
                    })()}

                    {/* Metadata */}
                    {(message.workflow_type || message.execution_time) && (
                      <div className="mt-3 flex flex-wrap gap-2">
                        {message.workflow_type && (
                          <span className="inline-block px-3 py-1 bg-orange-100 text-orange-700 text-xs rounded-full font-medium">
                            {message.workflow_type.replace('_', ' ')}
                          </span>
                        )}
                        {message.execution_time && (
                          <span className="inline-flex items-center gap-1 px-3 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                            <Clock className="w-3 h-3" />
                            {message.execution_time}s
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                  
                  {/* Timestamp */}
                  <p className="text-xs text-gray-400 mt-2 px-2">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </p>
                </div>

                {/* Avatar for User */}
                {message.role === 'user' && (
                  <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-blue-600 flex items-center justify-center">
                    <User className="w-5 h-5 text-white" />
                  </div>
                )}
              </div>
            ))}

            {/* Loading indicator */}
            {isLoading && (
              <div className="flex gap-4">
                <div className="w-10 h-10 rounded-full bg-gradient-to-r from-orange-500 to-orange-600 flex items-center justify-center">
                  <Bot className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1">
                  <div className="inline-block bg-white border border-gray-200 shadow-sm rounded-2xl px-6 py-4">
                    <div className="flex items-center gap-3">
                      <Loader2 className="w-5 h-5 animate-spin text-orange-600" />
                      <span className="text-sm text-gray-600">Analyzing your request...</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="bg-white border-t border-gray-200 p-4">
          <div className="max-w-3xl mx-auto">
            <form onSubmit={handleSubmit} className="flex flex-col gap-3">
              <div className="flex gap-3">
                <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask me anything about weather data..."
                  className="flex-1 px-5 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                  disabled={isLoading}
                />
                <button
                  type="submit"
                  disabled={isLoading || !input.trim()}
                  className="bg-gradient-to-r from-blue-600 to-orange-600 text-white px-6 py-3 rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  <Send className="w-5 h-5" />
                  <span className="font-medium">Send</span>
                </button>
              </div>
              
              {/* Quick Actions */}
              <div className="flex flex-wrap gap-2">
                <button
                  type="button"
                  onClick={() => setInput('Show me the latest weather data')}
                  className="text-xs px-4 py-2 bg-gradient-to-r from-green-50 to-emerald-50 hover:from-green-100 hover:to-emerald-100 rounded-full text-gray-700 transition-all border border-green-200"
                  title="Returns tabular data view"
                >
                  📊 View Data (Table)
                </button>
                <button
                  type="button"
                  onClick={() => setInput('Analyze temperature trends for the last 7 days')}
                  className="text-xs px-4 py-2 bg-gradient-to-r from-orange-50 to-pink-50 hover:from-orange-100 hover:to-pink-100 rounded-full text-gray-700 transition-all border border-orange-200"
                  title="Returns analysis with visualizations"
                >
                  � Analyze Trends (Charts)
                </button>
                <button
                  type="button"
                  onClick={() => setInput('Generate a comprehensive weather summary report')}
                  className="text-xs px-4 py-2 bg-gradient-to-r from-blue-50 to-cyan-50 hover:from-blue-100 hover:to-cyan-100 rounded-full text-gray-700 transition-all border border-blue-200"
                  title="Returns full report with download"
                >
                  📄 Full Report (Download)
                </button>
                <button
                  type="button"
                  onClick={() => setInput('Predict weather for tomorrow')}
                  className="text-xs px-4 py-2 bg-gradient-to-r from-amber-50 to-orange-50 hover:from-amber-100 hover:to-orange-100 rounded-full text-gray-700 transition-all border border-amber-200"
                >
                  � Predict Weather
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkflowChat;
