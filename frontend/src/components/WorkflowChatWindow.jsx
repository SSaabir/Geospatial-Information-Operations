import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Bot, User, X, Minimize2, Maximize2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const WorkflowChatWindow = ({ isOpen, onClose, onMinimize, isMinimized }) => {
  const { apiCall, user } = useAuth();
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hi! I\'m your AI workflow assistant. Ask me to analyze weather data, generate reports, or run predictions. For example: "Show me temperature trends for the last 7 days" or "Predict tomorrow\'s weather".',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && !isMinimized && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen, isMinimized]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Call the orchestrator API
      const response = await apiCall('/orchestrator/workflow', 'POST', {
        query: userMessage.content
      });

      // Extract the main response
      const assistantMessage = {
        role: 'assistant',
        content: response.final_answer || response.message || 'Task completed successfully!',
        data: response.data || null,
        visualization_url: response.visualization_url || null,
        workflow_type: response.workflow_type || null,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Workflow error:', error);
      const errorMessage = {
        role: 'assistant',
        content: `I encountered an error: ${error.message || 'Unable to process your request. Please try again.'}`,
        isError: true,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (!isOpen) return null;

  if (isMinimized) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <button
          onClick={onMinimize}
          className="bg-gradient-to-r from-blue-600 to-orange-600 text-white px-4 py-3 rounded-full shadow-lg hover:shadow-xl transition-all flex items-center gap-2"
        >
          <Bot className="w-5 h-5" />
          <span className="font-medium">AI Assistant</span>
          {messages.length > 1 && (
            <span className="bg-white text-blue-600 px-2 py-0.5 rounded-full text-xs font-bold">
              {messages.length - 1}
            </span>
          )}
        </button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 w-96 h-[600px] bg-white rounded-2xl shadow-2xl flex flex-col overflow-hidden border border-gray-200">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-orange-600 text-white p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="bg-white/20 p-2 rounded-lg">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-semibold">AI Workflow Assistant</h3>
            <p className="text-xs text-white/80">
              {user?.tier === 'free' ? '5 queries/mo' : user?.tier === 'researcher' ? '5,000 queries/mo' : 'Unlimited'}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={onMinimize}
            className="hover:bg-white/20 p-1.5 rounded-lg transition-colors"
            title="Minimize"
          >
            <Minimize2 className="w-4 h-4" />
          </button>
          <button
            onClick={onClose}
            className="hover:bg-white/20 p-1.5 rounded-lg transition-colors"
            title="Close"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
          >
            {/* Avatar */}
            <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
              message.role === 'user'
                ? 'bg-gradient-to-r from-blue-500 to-blue-600'
                : message.isError
                ? 'bg-red-500'
                : 'bg-gradient-to-r from-orange-500 to-orange-600'
            }`}>
              {message.role === 'user' ? (
                <User className="w-4 h-4 text-white" />
              ) : (
                <Bot className="w-4 h-4 text-white" />
              )}
            </div>

            {/* Message Content */}
            <div className={`flex-1 ${message.role === 'user' ? 'text-right' : 'text-left'}`}>
              <div className={`inline-block max-w-[85%] rounded-2xl px-4 py-2 ${
                message.role === 'user'
                  ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white'
                  : message.isError
                  ? 'bg-red-50 text-red-900 border border-red-200'
                  : 'bg-white text-gray-800 border border-gray-200'
              }`}>
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                
                {/* Visualization */}
                {message.visualization_url && (
                  <div className="mt-3">
                    <img
                      src={message.visualization_url}
                      alt="Visualization"
                      className="w-full rounded-lg border border-gray-200"
                    />
                  </div>
                )}

                {/* Data Preview */}
                {message.data && (
                  <div className="mt-3 bg-gray-50 rounded-lg p-3 text-xs">
                    <div className="font-mono text-gray-600 max-h-32 overflow-auto">
                      {JSON.stringify(message.data, null, 2)}
                    </div>
                  </div>
                )}

                {/* Workflow Type Badge */}
                {message.workflow_type && (
                  <div className="mt-2">
                    <span className="inline-block px-2 py-1 bg-orange-100 text-orange-700 text-xs rounded-full">
                      {message.workflow_type.replace('_', ' ')}
                    </span>
                  </div>
                )}
              </div>
              
              {/* Timestamp */}
              <p className="text-xs text-gray-400 mt-1 px-1">
                {formatTime(message.timestamp)}
              </p>
            </div>
          </div>
        ))}

        {/* Loading indicator */}
        {isLoading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-r from-orange-500 to-orange-600 flex items-center justify-center">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div className="flex-1">
              <div className="inline-block bg-white border border-gray-200 rounded-2xl px-4 py-3">
                <div className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin text-orange-600" />
                  <span className="text-sm text-gray-600">Thinking...</span>
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 bg-white border-t border-gray-200">
        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask me anything about weather data..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="bg-gradient-to-r from-blue-600 to-orange-600 text-white p-2 rounded-xl hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        
        {/* Quick Actions */}
        <div className="mt-3 flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => setInput('Show temperature trends for last 7 days')}
            className="text-xs px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700 transition-colors"
          >
            📊 Temperature Trends
          </button>
          <button
            type="button"
            onClick={() => setInput('Predict tomorrow\'s weather')}
            className="text-xs px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700 transition-colors"
          >
            🔮 Predict Weather
          </button>
          <button
            type="button"
            onClick={() => setInput('Generate weather report')}
            className="text-xs px-3 py-1.5 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-700 transition-colors"
          >
            📄 Generate Report
          </button>
        </div>
      </form>
    </div>
  );
};

export default WorkflowChatWindow;
