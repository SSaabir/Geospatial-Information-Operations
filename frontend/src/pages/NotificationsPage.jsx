import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Bell, Check, Trash2, Filter, Info, AlertTriangle, CheckCircle, Clock, Archive, RefreshCw } from 'lucide-react';

export default function NotificationsPage() {
  const { apiCall } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');
  const [stats, setStats] = useState({ total: 0, unread: 0, info: 0, warning: 0, error: 0 });

  const fetchNotifications = async () => {
    setLoading(true);
    try {
      const response = await apiCall('/notifications/user?limit=100', 'GET');
      if (response.notifications) {
        setNotifications(response.notifications);
        
        // Calculate stats
        const unread = response.notifications.filter(n => !n.read).length;
        const info = response.notifications.filter(n => n.level === 'info').length;
        const warning = response.notifications.filter(n => n.level === 'warning').length;
        const error = response.notifications.filter(n => n.level === 'error' || n.level === 'critical').length;
        
        setStats({
          total: response.notifications.length,
          unread,
          info,
          warning,
          error
        });
      }
    } catch (error) {
      console.error('Failed to fetch notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  const markAsRead = async (notificationId, event) => {
    if (event) {
      event.stopPropagation();
      event.preventDefault();
    }
    
    try {
      // Check if notification was actually unread
      const wasUnread = notifications.find(n => n.id === notificationId)?.read === false;
      
      await apiCall(`/notifications/${notificationId}/read`, { method: 'PUT' });
      setNotifications(prev =>
        prev.map(n => n.id === notificationId ? { ...n, read: true } : n)
      );
      
      if (wasUnread) {
        setStats(prev => ({ ...prev, unread: Math.max(0, prev.unread - 1) }));
      }
    } catch (error) {
      console.error('Failed to mark as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      await apiCall('/notifications/read-all', { method: 'PUT' });
      setNotifications(prev => prev.map(n => ({ ...n, read: true })));
      setStats(prev => ({ ...prev, unread: 0 }));
    } catch (error) {
      console.error('Failed to mark all as read:', error);
    }
  };

  const deleteNotification = async (notificationId, event) => {
    if (event) {
      event.stopPropagation();
      event.preventDefault();
    }
    
    try {
      // Capture notification details BEFORE deleting
      const notification = notifications.find(n => n.id === notificationId);
      if (!notification) return;
      
      const wasUnread = notification.read === false;
      const level = notification.level;
      
      await apiCall(`/notifications/${notificationId}`, { method: 'DELETE' });
      
      // Update state
      setNotifications(prev => prev.filter(n => n.id !== notificationId));
      
      // Update stats correctly
      setStats(prev => ({
        total: prev.total - 1,
        unread: wasUnread ? Math.max(0, prev.unread - 1) : prev.unread,
        info: level === 'info' || level === 'success' ? Math.max(0, prev.info - 1) : prev.info,
        warning: level === 'warning' ? Math.max(0, prev.warning - 1) : prev.warning,
        error: (level === 'error' || level === 'critical') ? Math.max(0, prev.error - 1) : prev.error
      }));
    } catch (error) {
      console.error('Failed to delete notification:', error);
    }
  };

  const getNotificationIcon = (level) => {
    switch (level) {
      case 'error':
      case 'critical':
        return <AlertTriangle className="w-6 h-6 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="w-6 h-6 text-yellow-500" />;
      case 'success':
        return <CheckCircle className="w-6 h-6 text-green-500" />;
      default:
        return <Info className="w-6 h-6 text-blue-500" />;
    }
  };

  const getNotificationBg = (level) => {
    switch (level) {
      case 'error':
      case 'critical':
        return 'bg-red-50 border-red-200';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200';
      case 'success':
        return 'bg-green-50 border-green-200';
      default:
        return 'bg-blue-50 border-blue-200';
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
    return date.toLocaleString();
  };

  const filteredNotifications = notifications.filter(n => {
    if (filter === 'all') return true;
    if (filter === 'unread') return !n.read;
    return n.level === filter;
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-amber-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between mb-6">
            <div className="mb-4 lg:mb-0">
              <h1 className="text-3xl font-bold text-gray-800 flex items-center space-x-3">
                <div className="w-12 h-12 bg-gradient-to-r from-orange-600 to-green-800 rounded-xl flex items-center justify-center">
                  <Bell className="w-6 h-6 text-white" />
                </div>
                <span>Notifications</span>
              </h1>
              <p className="text-gray-600 mt-2">Stay updated with all your activity</p>
            </div>

            <div className="flex items-center space-x-3">
              <button
                onClick={fetchNotifications}
                className="flex items-center space-x-2 px-4 py-2 bg-white rounded-lg hover:bg-gray-50 transition-colors border border-gray-200"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                <span className="font-medium text-gray-700">Refresh</span>
              </button>
              {stats.unread > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="flex items-center space-x-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
                >
                  <Check className="w-4 h-4" />
                  <span className="font-medium">Mark All Read</span>
                </button>
              )}
            </div>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            <div className="bg-white rounded-xl p-4 border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total</p>
                  <p className="text-2xl font-bold text-gray-800">{stats.total}</p>
                </div>
                <Bell className="w-8 h-8 text-gray-400" />
              </div>
            </div>

            <div className="bg-orange-50 rounded-xl p-4 border border-orange-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-orange-600">Unread</p>
                  <p className="text-2xl font-bold text-orange-800">{stats.unread}</p>
                </div>
                <Archive className="w-8 h-8 text-orange-400" />
              </div>
            </div>

            <div className="bg-blue-50 rounded-xl p-4 border border-blue-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-blue-600">Info</p>
                  <p className="text-2xl font-bold text-blue-800">{stats.info}</p>
                </div>
                <Info className="w-8 h-8 text-blue-400" />
              </div>
            </div>

            <div className="bg-yellow-50 rounded-xl p-4 border border-yellow-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-yellow-600">Warnings</p>
                  <p className="text-2xl font-bold text-yellow-800">{stats.warning}</p>
                </div>
                <AlertTriangle className="w-8 h-8 text-yellow-400" />
              </div>
            </div>

            <div className="bg-red-50 rounded-xl p-4 border border-red-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-red-600">Errors</p>
                  <p className="text-2xl font-bold text-red-800">{stats.error}</p>
                </div>
                <AlertTriangle className="w-8 h-8 text-red-400" />
              </div>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl p-4 border border-gray-200 mb-6">
          <div className="flex items-center space-x-2 overflow-x-auto">
            <Filter className="w-5 h-5 text-gray-400 flex-shrink-0" />
            {[
              { id: 'all', label: 'All Notifications', count: stats.total },
              { id: 'unread', label: 'Unread', count: stats.unread },
              { id: 'info', label: 'Info', count: stats.info },
              { id: 'warning', label: 'Warnings', count: stats.warning },
              { id: 'error', label: 'Errors', count: stats.error }
            ].map((f) => (
              <button
                key={f.id}
                onClick={() => setFilter(f.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${
                  filter === f.id
                    ? 'bg-orange-100 text-orange-700'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {f.label} ({f.count})
              </button>
            ))}
          </div>
        </div>

        {/* Notifications List */}
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
          </div>
        ) : filteredNotifications.length === 0 ? (
          <div className="bg-white rounded-xl p-12 text-center border border-gray-200">
            <Bell className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-800 mb-2">No notifications</h3>
            <p className="text-gray-600">You're all caught up!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredNotifications.map((notification) => (
              <div
                key={notification.id}
                className={`bg-white rounded-xl p-6 border transition-all hover:shadow-lg ${
                  !notification.read ? 'border-orange-200 ring-2 ring-orange-100' : 'border-gray-200'
                }`}
              >
                <div className="flex items-start space-x-4">
                  {/* Icon */}
                  <div className="flex-shrink-0 mt-1">
                    {getNotificationIcon(notification.level)}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <h3 className={`text-lg font-semibold text-gray-800 flex items-center space-x-2 ${
                          !notification.read ? 'font-bold' : ''
                        }`}>
                          <span>{notification.subject}</span>
                          {!notification.read && (
                            <span className="w-2 h-2 bg-orange-600 rounded-full"></span>
                          )}
                        </h3>
                        <p className="text-gray-600 mt-1">{notification.message}</p>
                      </div>
                    </div>

                    {/* Metadata */}
                    {notification.metadata && Object.keys(notification.metadata).length > 0 && (
                      <div className="mt-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
                        <p className="text-xs font-semibold text-gray-500 uppercase mb-2">Details</p>
                        <div className="grid grid-cols-2 gap-2">
                          {Object.entries(notification.metadata).map(([key, value]) => (
                            <div key={key}>
                              <span className="text-xs text-gray-500">{key}: </span>
                              <span className="text-sm font-medium text-gray-700">
                                {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Footer */}
                    <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-100">
                      <div className="flex items-center space-x-2 text-sm text-gray-500">
                        <Clock className="w-4 h-4" />
                        <span>{formatTime(notification.timestamp)}</span>
                        <span className="px-2 py-1 bg-gray-100 rounded text-xs font-medium text-gray-600">
                          {notification.level}
                        </span>
                      </div>

                      <div className="flex items-center space-x-2">
                        {!notification.read && (
                          <button
                            onClick={(e) => markAsRead(notification.id, e)}
                            className="px-3 py-1 bg-orange-100 text-orange-700 rounded-lg hover:bg-orange-200 transition-colors text-sm font-medium flex items-center space-x-1"
                          >
                            <Check className="w-4 h-4" />
                            <span>Mark Read</span>
                          </button>
                        )}
                        <button
                          onClick={(e) => deleteNotification(notification.id, e)}
                          className="px-3 py-1 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors text-sm font-medium flex items-center space-x-1"
                        >
                          <Trash2 className="w-4 h-4" />
                          <span>Delete</span>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
