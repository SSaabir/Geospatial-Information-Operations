import React, { useState, useEffect } from 'react';
import { UserPlus, X, Search, Shield, Check, AlertCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export default function AddAdminPanel() {
  const { apiCall } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [users, setUsers] = useState([]);
  const [filteredUsers, setFilteredUsers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    if (isOpen) {
      fetchUsers();
    }
  }, [isOpen]);

  useEffect(() => {
    if (searchTerm) {
      const filtered = users.filter(user => 
        user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.full_name?.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredUsers(filtered);
    } else {
      setFilteredUsers(users);
    }
  }, [searchTerm, users]);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const response = await apiCall('/auth/admin/users');
      setUsers(response);
      setFilteredUsers(response);
    } catch (error) {
      console.error('Failed to fetch users:', error);
      setMessage({ type: 'error', text: 'Failed to load users' });
    } finally {
      setLoading(false);
    }
  };

  const promoteToAdmin = async (userId, username) => {
    try {
      await apiCall(`/auth/admin/users/${userId}/promote`, {
        method: 'PUT'
      });
      setMessage({ type: 'success', text: `${username} promoted to admin!` });
      fetchUsers(); // Refresh list
      setTimeout(() => setMessage({ type: '', text: '' }), 3000);
    } catch (error) {
      console.error('Failed to promote user:', error);
      setMessage({ type: 'error', text: 'Failed to promote user' });
      setTimeout(() => setMessage({ type: '', text: '' }), 3000);
    }
  };

  const demoteFromAdmin = async (userId, username) => {
    if (!confirm(`Are you sure you want to remove admin privileges from ${username}?`)) {
      return;
    }
    
    try {
      await apiCall(`/auth/admin/users/${userId}/demote`, {
        method: 'PUT'
      });
      setMessage({ type: 'success', text: `${username} demoted from admin` });
      fetchUsers(); // Refresh list
      setTimeout(() => setMessage({ type: '', text: '' }), 3000);
    } catch (error) {
      console.error('Failed to demote user:', error);
      setMessage({ type: 'error', text: error.message || 'Failed to demote user' });
      setTimeout(() => setMessage({ type: '', text: '' }), 3000);
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="inline-flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-orange-600 to-green-800 text-white rounded-xl hover:from-orange-700 hover:to-green-900 transition-all duration-200 shadow-lg"
      >
        <UserPlus className="w-4 h-4" />
        <span>Manage Admins</span>
      </button>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-xl border border-orange-200 p-6 mb-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-r from-orange-600 to-green-800 rounded-xl flex items-center justify-center">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-800">Admin Management</h2>
            <p className="text-sm text-gray-600">Promote or demote users</p>
          </div>
        </div>
        <button
          onClick={() => {
            setIsOpen(false);
            setSearchTerm('');
            setMessage({ type: '', text: '' });
          }}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <X className="w-5 h-5 text-gray-500" />
        </button>
      </div>

      {/* Message Alert */}
      {message.text && (
        <div className={`mb-4 p-4 rounded-xl flex items-center space-x-2 ${
          message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
        }`}>
          {message.type === 'success' ? (
            <Check className="w-5 h-5" />
          ) : (
            <AlertCircle className="w-5 h-5" />
          )}
          <span className="font-medium">{message.text}</span>
        </div>
      )}

      {/* Search Bar */}
      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          placeholder="Search users by name, email, or username..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-orange-500 focus:border-transparent"
        />
      </div>

      {/* Users List */}
      {loading ? (
        <div className="text-center py-8">
          <div className="w-8 h-8 border-4 border-orange-200 border-t-orange-600 rounded-full animate-spin mx-auto"></div>
          <p className="text-gray-600 mt-2">Loading users...</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {filteredUsers.length === 0 ? (
            <p className="text-center text-gray-500 py-8">No users found</p>
          ) : (
            filteredUsers.map((user) => (
              <div
                key={user.id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center space-x-4">
                  <img
                    src={user.avatar_url || `https://api.dicebear.com/7.x/avataaars/svg?seed=${user.username}`}
                    alt={user.username}
                    className="w-12 h-12 rounded-full"
                  />
                  <div>
                    <div className="flex items-center space-x-2">
                      <p className="font-semibold text-gray-800">{user.username}</p>
                      {user.is_admin && (
                        <span className="px-2 py-0.5 bg-orange-100 text-orange-700 text-xs font-medium rounded-full">
                          Admin
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600">{user.email}</p>
                    <p className="text-xs text-gray-500">Tier: {user.tier}</p>
                  </div>
                </div>
                <div>
                  {user.is_admin ? (
                    <button
                      onClick={() => demoteFromAdmin(user.id, user.username)}
                      className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors text-sm font-medium"
                    >
                      Remove Admin
                    </button>
                  ) : (
                    <button
                      onClick={() => promoteToAdmin(user.id, user.username)}
                      className="px-4 py-2 bg-orange-100 text-orange-700 rounded-lg hover:bg-orange-200 transition-colors text-sm font-medium"
                    >
                      Make Admin
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
