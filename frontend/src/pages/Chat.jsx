import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, Clock, MessageSquare, Smile, Paperclip, MoreVertical } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function Chat() {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: 'Hello! I\'m your weather analytics assistant. How can I help you today?',
      timestamp: new Date(Date.now() - 120000)
    },
    {
      id: 2,
      type: 'bot',
      content: 'I can help you with:\n• Weather forecasts and predictions\n• Climate data analysis and trends\n• Historical weather patterns\n• Data visualization insights\n• Geospatial weather mapping\n• Custom weather reports',
      timestamp: new Date(Date.now() - 100000)
    }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const { user, isAuthenticated } = useAuth();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!message.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const currentMessage = message;
    setMessage('');
    setIsTyping(true);

    try {
      // Get conversation history for context
      const conversationHistory = messages.map(msg => ({
        role: msg.type === 'user' ? 'user' : 'assistant',
        content: msg.content,
        timestamp: msg.timestamp
      }));

      // Call Groq-powered chat API
      const response = await fetch(`${API_BASE_URL}/chat/send`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          message: currentMessage,
          conversation_history: conversationHistory
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to get response');
      }

      const data = await response.json();

      const botMessage = {
        id: Date.now(),
        type: 'bot',
        content: data.response,
        timestamp: new Date(data.timestamp)
      };

      setIsTyping(false);
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      setIsTyping(false);
      
      // Show error message
      const errorMessage = {
        id: Date.now(),
        type: 'bot',
        content: error.message.includes('Professional tier') 
          ? '🔒 Chat feature requires Professional tier subscription. Please upgrade to access AI-powered weather analytics chat.'
          : '❌ Sorry, I encountered an error. Please try again or contact support if the issue persists.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return 'Today';
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 to-amber-50 flex items-center justify-center" style={{backgroundColor: '#F9F5F0'}}>
        <div className="text-center p-8">
          <MessageSquare className="w-16 h-16 text-orange-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Chat Access Restricted</h2>
          <p className="text-gray-600 mb-6">Please log in to access the weather assistant chat.</p>
          <a
            href="/login"
            className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-orange-600 to-green-800 text-white rounded-xl hover:from-orange-700 hover:to-green-900 transition-all duration-200"
          >
            Go to Login
          </a>
        </div>
      </div>
    );
  }

  // Check user tier
  const userTier = user?.tier || 'free';
  const hasProAccess = userTier === 'professional';

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-amber-50" style={{backgroundColor: '#F9F5F0'}}>
      <div className="container mx-auto px-4 py-8">
        {/* Tier Restriction Banner */}
        {!hasProAccess && (
          <div className="bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-2xl shadow-xl p-6 mb-6 border border-amber-300">
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-4">
                <div className="p-3 bg-white/20 rounded-xl backdrop-blur-sm">
                  <MessageSquare className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-xl font-bold mb-2">🔒 Professional Feature</h3>
                  <p className="text-white/90 mb-3">
                    AI-powered weather analytics chat is available exclusively for Professional tier subscribers. 
                    Upgrade now to unlock real-time AI insights, climate analysis, and personalized weather forecasting.
                  </p>
                  <div className="flex space-x-3">
                    <a
                      href="/pricing"
                      className="inline-flex items-center px-4 py-2 bg-white text-orange-600 rounded-lg font-semibold hover:bg-orange-50 transition-all"
                    >
                      ⭐ Upgrade to Professional
                    </a>
                    <span className="text-white/70 px-4 py-2">
                      Current tier: <strong className="capitalize">{userTier}</strong>
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Chat Header */}
        <div className="bg-white/80 backdrop-blur-md rounded-2xl shadow-xl border border-orange-100 mb-6">
          <div className="bg-gradient-to-r from-orange-600 to-green-800 text-white p-6 rounded-t-2xl">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="relative">
                  <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                    <Bot className="w-6 h-6" />
                  </div>
                  <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white"></div>
                </div>
                <div>
                  <h1 className="text-2xl font-bold">Weather Assistant</h1>
                  <p className="text-orange-100">AI-Powered Climate Analytics • Online</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button className="p-2 hover:bg-white/20 rounded-lg transition-colors">
                  <MoreVertical className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
          
          {/* User Info Bar */}
          {user && (
            <div className="p-4 border-b border-orange-100 bg-orange-50/50">
              <div className="flex items-center space-x-3">
                <img 
                  src={user.avatar} 
                  alt={user.name}
                  className="w-8 h-8 rounded-full"
                />
                <div>
                  <p className="text-sm font-medium text-gray-700">Chatting as {user.name}</p>
                  <p className="text-xs text-gray-500">Connected to Weather Analytics AI</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Chat Container */}
        <div className="bg-white/80 backdrop-blur-md rounded-2xl shadow-xl border border-orange-100 overflow-hidden">
          {/* Messages Area */}
          <div className="h-96 lg:h-[32rem] overflow-y-auto p-6 space-y-6 bg-gradient-to-b from-orange-50/30 to-white">
            {messages.map((msg, index) => {
              const showDate = index === 0 || formatDate(msg.timestamp) !== formatDate(messages[index - 1].timestamp);
              
              return (
                <div key={msg.id}>
                  {/* Date Separator */}
                  {showDate && (
                    <div className="flex justify-center mb-4">
                      <div className="bg-orange-100 text-orange-600 px-3 py-1 rounded-full text-xs font-medium">
                        {formatDate(msg.timestamp)}
                      </div>
                    </div>
                  )}
                  
                  {/* Message */}
                  <div className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-xs lg:max-w-md xl:max-w-lg px-4 py-3 rounded-2xl ${
                      msg.type === 'user' 
                        ? 'bg-gradient-to-r from-orange-600 to-green-800 text-white' 
                        : 'bg-white shadow-md border border-orange-100'
                    }`}>
                      <div className="flex items-start space-x-3">
                        {msg.type === 'bot' && (
                          <div className="w-8 h-8 bg-gradient-to-r from-orange-600 to-green-800 rounded-xl flex items-center justify-center flex-shrink-0">
                            <Sparkles className="w-4 h-4 text-white" />
                          </div>
                        )}
                        <div className="flex-1">
                          <p className={`text-sm whitespace-pre-line leading-relaxed ${
                            msg.type === 'user' ? 'text-white' : 'text-gray-800'
                          }`}>
                            {msg.content}
                          </p>
                          <div className={`flex items-center space-x-1 mt-2 ${
                            msg.type === 'user' ? 'justify-end' : 'justify-start'
                          }`}>
                            <Clock className={`w-3 h-3 ${
                              msg.type === 'user' ? 'text-orange-200' : 'text-gray-400'
                            }`} />
                            <span className={`text-xs ${
                              msg.type === 'user' ? 'text-orange-200' : 'text-gray-400'
                            }`}>
                              {formatTime(msg.timestamp)}
                            </span>
                          </div>
                        </div>
                        {msg.type === 'user' && user && (
                          <img 
                            src={user.avatar} 
                            alt="User" 
                            className="w-8 h-8 rounded-xl flex-shrink-0"
                          />
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}

            {/* Typing Indicator */}
            {isTyping && (
              <div className="flex justify-start">
                <div className="bg-white shadow-md border border-orange-100 px-4 py-3 rounded-2xl">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-gradient-to-r from-orange-600 to-green-800 rounded-xl flex items-center justify-center">
                      <Sparkles className="w-4 h-4 text-white" />
                    </div>
                    <div className="flex items-center space-x-1">
                      <div className="w-2 h-2 bg-orange-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-orange-400 rounded-full animate-bounce delay-100"></div>
                      <div className="w-2 h-2 bg-orange-400 rounded-full animate-bounce delay-200"></div>
                    </div>
                    <span className="text-xs text-gray-500">AI is thinking...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Message Input */}
          <div className="p-6 border-t border-orange-100 bg-white">
            <form onSubmit={handleSendMessage}>
              <div className="flex items-end space-x-3">
                <div className="flex-1">
                  <div className="relative">
                    <input
                      type="text"
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                      placeholder="Ask about weather patterns, climate data, forecasts..."
                      className="w-full px-4 py-3 pr-24 border border-orange-200 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all duration-200 bg-orange-50/30"
                      disabled={isTyping}
                    />
                    <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center space-x-1">
                      <button
                        type="button"
                        className="p-1.5 text-gray-400 hover:text-orange-600 transition-colors"
                      >
                        <Smile className="w-4 h-4" />
                      </button>
                      <button
                        type="button"
                        className="p-1.5 text-gray-400 hover:text-orange-600 transition-colors"
                      >
                        <Paperclip className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  <p className="text-xs text-gray-500 mt-1 px-1">
                    Ask about weather forecasts, climate trends, or data analysis
                  </p>
                </div>
                <button
                  type="submit"
                  disabled={!message.trim() || isTyping}
                  className="bg-gradient-to-r from-orange-600 to-green-800 text-white p-3 rounded-xl hover:from-orange-700 hover:to-green-900 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed group"
                >
                  <Send className="w-5 h-5 group-hover:translate-x-0.5 transition-transform" />
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}