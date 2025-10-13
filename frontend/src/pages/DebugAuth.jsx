import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

const DebugAuth = () => {
  const { user, refreshUser, logout } = useAuth();
  const [localStorageData, setLocalStorageData] = useState(null);
  const [refreshed, setRefreshed] = useState(false);

  const checkLocalStorage = () => {
    const data = {
      user: localStorage.getItem('user'),
      access_token: localStorage.getItem('access_token') ? 'exists' : 'missing',
      refresh_token: localStorage.getItem('refresh_token') ? 'exists' : 'missing'
    };
    setLocalStorageData(data);
  };

  const handleRefreshUser = async () => {
    await refreshUser();
    setRefreshed(true);
    setTimeout(() => setRefreshed(false), 2000);
  };

  const clearAndLogout = async () => {
    await logout();
    window.location.href = '/login';
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Auth Debug Page</h1>

        {/* Current User from Context */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Current User (Context)</h2>
          <pre className="bg-gray-100 p-4 rounded overflow-auto">
            {JSON.stringify(user, null, 2)}
          </pre>
          <div className="mt-4">
            <p className="font-semibold">Is Admin: <span className={user?.is_admin ? 'text-green-600' : 'text-red-600'}>{String(user?.is_admin)}</span></p>
          </div>
        </div>

        {/* LocalStorage Data */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">LocalStorage Data</h2>
          <button
            onClick={checkLocalStorage}
            className="mb-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Check LocalStorage
          </button>
          {localStorageData && (
            <div>
              <pre className="bg-gray-100 p-4 rounded overflow-auto mb-2">
                {localStorageData.user ? JSON.stringify(JSON.parse(localStorageData.user), null, 2) : 'No user data'}
              </pre>
              <p>Access Token: {localStorageData.access_token}</p>
              <p>Refresh Token: {localStorageData.refresh_token}</p>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Actions</h2>
          <div className="space-y-3">
            <button
              onClick={handleRefreshUser}
              className="w-full px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
            >
              {refreshed ? '✅ Refreshed!' : 'Refresh User from API'}
            </button>
            <button
              onClick={clearAndLogout}
              className="w-full px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
            >
              Clear All & Logout
            </button>
          </div>
        </div>

        {/* Instructions */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mt-6">
          <h3 className="font-semibold mb-2">🔧 Troubleshooting Steps:</h3>
          <ol className="list-decimal list-inside space-y-2">
            <li>Check if <code className="bg-yellow-100 px-1">is_admin</code> is present in Context user</li>
            <li>Click "Check LocalStorage" to see what's stored</li>
            <li>If <code className="bg-yellow-100 px-1">is_admin</code> is missing or <code className="bg-yellow-100 px-1">false</code>, click "Refresh User from API"</li>
            <li>If still not working, click "Clear All & Logout" and login again</li>
          </ol>
        </div>
      </div>
    </div>
  );
};

export default DebugAuth;
