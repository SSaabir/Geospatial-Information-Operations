import React, { useState, useEffect } from 'react';
import { Newspaper, AlertCircle, TrendingUp, Calendar, ExternalLink, Filter } from 'lucide-react';

export default function NewsAlerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, weather, climate, environmental
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchNewsAlerts();
  }, []);

  const fetchNewsAlerts = async () => {
    try {
      setLoading(true);
      const accessToken = localStorage.getItem('access_token');
      
      const response = await fetch('http://localhost:8000/api/news/alerts?threshold=70&limit=10', {
        headers: {
          'Authorization': `Bearer ${accessToken}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch news alerts');
      }

      const data = await response.json();
      setAlerts(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching news alerts:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getCategoryColor = (category) => {
    switch (category) {
      case 'weather':
        return 'bg-blue-100 text-blue-800';
      case 'climate':
        return 'bg-red-100 text-red-800';
      case 'environmental':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'weather':
        return '🌤️';
      case 'climate':
        return '🌡️';
      case 'environmental':
        return '🌍';
      default:
        return '📰';
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Recent';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffHours < 1) return 'Just now';
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const filteredAlerts = filter === 'all' 
    ? alerts 
    : alerts.filter(alert => alert.category === filter);

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center gap-3 mb-4">
          <Newspaper className="w-6 h-6 text-green-800" />
          <h2 className="text-xl font-bold text-gray-800">Latest News & Alerts</h2>
        </div>
        <div className="space-y-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center gap-3 mb-4">
          <Newspaper className="w-6 h-6 text-green-800" />
          <h2 className="text-xl font-bold text-gray-800">Latest News & Alerts</h2>
        </div>
        <div className="flex items-center gap-2 text-orange-600">
          <AlertCircle className="w-5 h-5" />
          <span className="text-sm">Unable to load news alerts</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Newspaper className="w-6 h-6 text-green-800" />
          <h2 className="text-xl font-bold text-gray-800">Latest News & Alerts</h2>
        </div>
        
        {/* Filter */}
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-500" />
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="text-sm border border-gray-300 rounded-lg px-3 py-1 focus:outline-none focus:ring-2 focus:ring-amber-500"
          >
            <option value="all">All Categories</option>
            <option value="weather">Weather</option>
            <option value="climate">Climate</option>
            <option value="environmental">Environmental</option>
          </select>
        </div>
      </div>

      {/* Alerts List */}
      {filteredAlerts.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <Newspaper className="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>No news alerts available</p>
          <p className="text-sm mt-1">Check back later for updates</p>
        </div>
      ) : (
        <div className="space-y-4 max-h-96 overflow-y-auto">
          {filteredAlerts.map((alert) => (
            <div
              key={alert.id}
              className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer group"
              onClick={() => window.open(alert.url, '_blank')}
            >
              {/* Category Badge & Relevance */}
              <div className="flex items-center justify-between mb-2">
                <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(alert.category)}`}>
                  <span>{getCategoryIcon(alert.category)}</span>
                  {alert.category}
                </span>
                
                <div className="flex items-center gap-2">
                  {alert.relevance_score >= 80 && (
                    <span className="flex items-center gap-1 text-xs text-orange-600 font-medium">
                      <TrendingUp className="w-3 h-3" />
                      High Priority
                    </span>
                  )}
                  <span className="text-xs text-gray-500">{alert.relevance_score}% relevant</span>
                </div>
              </div>

              {/* Title */}
              <h3 className="font-semibold text-gray-900 mb-2 group-hover:text-green-800 transition-colors line-clamp-2">
                {alert.title}
              </h3>

              {/* Description */}
              {alert.description && (
                <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                  {alert.description}
                </p>
              )}

              {/* Metadata */}
              <div className="flex items-center justify-between text-xs text-gray-500">
                <div className="flex items-center gap-3">
                  <span className="font-medium text-gray-700">{alert.source}</span>
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    {formatDate(alert.published_at)}
                  </span>
                </div>
                
                <ExternalLink className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>

              {/* Keywords */}
              {alert.keywords && alert.keywords.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {alert.keywords.slice(0, 3).map((keyword, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* View All Link */}
      {filteredAlerts.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200 text-center">
          <button
            onClick={() => window.location.href = '/news'}
            className="text-sm text-green-800 hover:text-green-900 font-medium"
          >
            View All News →
          </button>
        </div>
      )}
    </div>
  );
}
