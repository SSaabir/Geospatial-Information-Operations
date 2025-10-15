import React, { useState, useEffect } from 'react';
import { Newspaper, Search, Filter, Calendar, ExternalLink, TrendingUp, AlertCircle, ChevronLeft, ChevronRight } from 'lucide-react';

export default function News() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalArticles, setTotalArticles] = useState(0);
  const pageSize = 12;

  useEffect(() => {
    fetchNews();
  }, [currentPage, categoryFilter]);

  const fetchNews = async () => {
    try {
      setLoading(true);
      
      let url = `http://localhost:8000/api/news/feed?page=${currentPage}&page_size=${pageSize}`;
      if (categoryFilter !== 'all') {
        url += `&category=${categoryFilter}`;
      }

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error('Failed to fetch news');
      }

      const data = await response.json();
      setArticles(data.articles);
      setTotalPages(Math.ceil(data.total / pageSize));
      setTotalArticles(data.total);
      setError(null);
    } catch (err) {
      console.error('Error fetching news:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getCategoryColor = (category) => {
    switch (category) {
      case 'weather':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'climate':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'environmental':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
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
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const filteredArticles = articles.filter(article => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      article.title.toLowerCase().includes(query) ||
      article.description?.toLowerCase().includes(query) ||
      article.source.toLowerCase().includes(query)
    );
  });

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setCurrentPage(newPage);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-amber-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <Newspaper className="w-10 h-10 text-green-800" />
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-green-800 to-blue-600 bg-clip-text text-transparent">
                Climate & Weather News
              </h1>
              <p className="text-gray-600 mt-1">
                Stay informed with the latest updates on climate change, weather patterns, and environmental news
              </p>
            </div>
          </div>

          {/* Stats */}
          <div className="flex items-center gap-4 text-sm text-gray-600">
            <span className="flex items-center gap-1">
              <Newspaper className="w-4 h-4" />
              {totalArticles} articles
            </span>
            <span className="flex items-center gap-1">
              <Calendar className="w-4 h-4" />
              Updated daily
            </span>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search articles by title, description, or source..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
              />
            </div>

            {/* Category Filter */}
            <div className="flex items-center gap-2">
              <Filter className="w-5 h-5 text-gray-500" />
              <select
                value={categoryFilter}
                onChange={(e) => {
                  setCategoryFilter(e.target.value);
                  setCurrentPage(1);
                }}
                className="px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500 bg-white"
              >
                <option value="all">All Categories</option>
                <option value="weather">🌤️ Weather</option>
                <option value="climate">🌡️ Climate</option>
                <option value="environmental">🌍 Environmental</option>
              </select>
            </div>
          </div>

          {/* Active Filters */}
          {(categoryFilter !== 'all' || searchQuery) && (
            <div className="mt-4 flex items-center gap-2 flex-wrap">
              <span className="text-sm text-gray-600">Active filters:</span>
              {categoryFilter !== 'all' && (
                <span className="px-3 py-1 bg-amber-100 text-green-900 rounded-full text-sm flex items-center gap-1">
                  {categoryFilter}
                  <button onClick={() => setCategoryFilter('all')} className="ml-1 hover:text-green-800-900">×</button>
                </span>
              )}
              {searchQuery && (
                <span className="px-3 py-1 bg-amber-100 text-green-900 rounded-full text-sm flex items-center gap-1">
                  "{searchQuery}"
                  <button onClick={() => setSearchQuery('')} className="ml-1 hover:text-green-800-900">×</button>
                </span>
              )}
              <button
                onClick={() => {
                  setCategoryFilter('all');
                  setSearchQuery('');
                }}
                className="text-sm text-green-800 hover:text-green-900 font-medium"
              >
                Clear all
              </button>
            </div>
          )}
        </div>

        {/* Loading State */}
        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map(i => (
              <div key={i} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                <div className="h-3 bg-gray-200 rounded w-full mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-5/6"></div>
              </div>
            ))}
          </div>
        )}

        {/* Error State */}
        {error && !loading && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 flex items-center gap-3">
            <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0" />
            <div>
              <h3 className="font-semibold text-red-900">Unable to load news</h3>
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        )}

        {/* Articles Grid */}
        {!loading && !error && (
          <>
            {filteredArticles.length === 0 ? (
              <div className="text-center py-12">
                <Newspaper className="w-16 h-16 mx-auto mb-4 text-gray-300" />
                <h3 className="text-xl font-semibold text-gray-700 mb-2">No articles found</h3>
                <p className="text-gray-500">Try adjusting your search or filters</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                {filteredArticles.map((article) => (
                  <div
                    key={article.id}
                    className="bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-lg transition-all duration-300 overflow-hidden group cursor-pointer"
                    onClick={() => window.open(article.url, '_blank')}
                  >
                    {/* Image */}
                    {article.image_url && (
                      <div className="relative h-48 overflow-hidden bg-gray-100">
                        <img
                          src={article.image_url}
                          alt={article.title}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                          onError={(e) => {
                            e.target.style.display = 'none';
                          }}
                        />
                        <div className="absolute top-3 right-3">
                          <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium border backdrop-blur-sm ${getCategoryColor(article.category)}`}>
                            <span>{getCategoryIcon(article.category)}</span>
                            {article.category}
                          </span>
                        </div>
                      </div>
                    )}

                    {/* Content */}
                    <div className="p-6">
                      {/* Category Badge (if no image) */}
                      {!article.image_url && (
                        <div className="mb-3">
                          <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium border ${getCategoryColor(article.category)}`}>
                            <span>{getCategoryIcon(article.category)}</span>
                            {article.category}
                          </span>
                        </div>
                      )}

                      {/* Relevance & Priority */}
                      <div className="flex items-center justify-between mb-3">
                        {article.relevance_score >= 80 && (
                          <span className="flex items-center gap-1 text-xs text-orange-600 font-medium">
                            <TrendingUp className="w-3 h-3" />
                            High Priority
                          </span>
                        )}
                        <span className="text-xs text-gray-500 ml-auto">{article.relevance_score}% relevant</span>
                      </div>

                      {/* Title */}
                      <h3 className="font-semibold text-gray-900 mb-3 group-hover:text-green-800 transition-colors line-clamp-2 text-lg">
                        {article.title}
                      </h3>

                      {/* Description */}
                      {article.description && (
                        <p className="text-sm text-gray-600 mb-4 line-clamp-3">
                          {article.description}
                        </p>
                      )}

                      {/* Keywords */}
                      {article.keywords && article.keywords.length > 0 && (
                        <div className="flex flex-wrap gap-1 mb-4">
                          {article.keywords.slice(0, 3).map((keyword, idx) => (
                            <span
                              key={idx}
                              className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs"
                            >
                              {keyword}
                            </span>
                          ))}
                        </div>
                      )}

                      {/* Footer */}
                      <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                        <div className="flex flex-col gap-1">
                          <span className="text-xs font-medium text-gray-700">{article.source}</span>
                          <span className="flex items-center gap-1 text-xs text-gray-500">
                            <Calendar className="w-3 h-3" />
                            {formatDate(article.published_at)}
                          </span>
                        </div>
                        <ExternalLink className="w-5 h-5 text-gray-400 group-hover:text-green-800 transition-colors" />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Pagination */}
            {filteredArticles.length > 0 && totalPages > 1 && (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-600">
                    Showing <span className="font-medium">{((currentPage - 1) * pageSize) + 1}</span> to{' '}
                    <span className="font-medium">{Math.min(currentPage * pageSize, totalArticles)}</span> of{' '}
                    <span className="font-medium">{totalArticles}</span> articles
                  </div>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handlePageChange(currentPage - 1)}
                      disabled={currentPage === 1}
                      className="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      <ChevronLeft className="w-5 h-5" />
                    </button>

                    {/* Page Numbers */}
                    <div className="flex items-center gap-1">
                      {[...Array(totalPages)].map((_, idx) => {
                        const pageNum = idx + 1;
                        // Show first, last, current, and adjacent pages
                        if (
                          pageNum === 1 ||
                          pageNum === totalPages ||
                          (pageNum >= currentPage - 1 && pageNum <= currentPage + 1)
                        ) {
                          return (
                            <button
                              key={pageNum}
                              onClick={() => handlePageChange(pageNum)}
                              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                                currentPage === pageNum
                                  ? 'bg-green-800 text-white'
                                  : 'border border-gray-300 hover:bg-gray-50'
                              }`}
                            >
                              {pageNum}
                            </button>
                          );
                        } else if (pageNum === currentPage - 2 || pageNum === currentPage + 2) {
                          return <span key={pageNum} className="px-2 text-gray-400">...</span>;
                        }
                        return null;
                      })}
                    </div>

                    <button
                      onClick={() => handlePageChange(currentPage + 1)}
                      disabled={currentPage === totalPages}
                      className="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      <ChevronRight className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
