import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const AdminTest = () => {
  const { user, isAuthenticated, isLoading } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Admin Access Test Page</h1>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Authentication Status</h2>
          <div className="space-y-2">
            <p><strong>Is Authenticated:</strong> {String(isAuthenticated)}</p>
            <p><strong>Is Loading:</strong> {String(isLoading)}</p>
            <p><strong>User ID:</strong> {user?.id || 'N/A'}</p>
            <p><strong>Username:</strong> {user?.username || 'N/A'}</p>
            <p><strong>Email:</strong> {user?.email || 'N/A'}</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Admin Status Check</h2>
          <div className="space-y-2">
            <p><strong>user?.is_admin (raw):</strong> {String(user?.is_admin)}</p>
            <p><strong>Type:</strong> {typeof user?.is_admin}</p>
            <p><strong>Strict boolean check (=== true):</strong> {String(user?.is_admin === true)}</p>
            <p><strong>Loose check (== true):</strong> {String(user?.is_admin == true)}</p>
            <p><strong>Truthy check:</strong> {String(!!user?.is_admin)}</p>
            <p><strong>String "true" check:</strong> {String(user?.is_admin === 'true')}</p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Full User Object</h2>
          <pre className="bg-gray-100 p-4 rounded overflow-auto text-sm">
            {JSON.stringify(user, null, 2)}
          </pre>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Navigation Test</h2>
          <div className="space-y-3">
            <button
              onClick={() => navigate('/admin/dashboard')}
              className="w-full px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Navigate to /admin/dashboard
            </button>
            <button
              onClick={() => navigate('/dashboard')}
              className="w-full px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-600"
            >
              Navigate to /dashboard (regular)
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminTest;
