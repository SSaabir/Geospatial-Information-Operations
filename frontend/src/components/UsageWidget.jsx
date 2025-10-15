import React, { useState, useEffect } from 'react';
import { Activity, TrendingUp, AlertTriangle, CheckCircle, ArrowUpRight } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export default function UsageWidget() {
  const { user, apiCall } = useAuth();
  const [usage, setUsage] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUsage();
  }, []);

  const fetchUsage = async () => {
    try {
      const response = await apiCall('/analytics/usage');
      setUsage(response);
    } catch (error) {
      console.error('Failed to fetch usage:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6 border border-orange-100 animate-pulse">
        <div className="h-4 bg-orange-100 rounded w-1/2 mb-4"></div>
        <div className="h-8 bg-orange-100 rounded mb-2"></div>
        <div className="h-3 bg-orange-100 rounded w-3/4"></div>
      </div>
    );
  }

  if (!usage) return null;

  const { api_calls, limit, remaining, tier } = usage;
  const percentage = limit === 'unlimited' ? 0 : Math.round((api_calls / limit) * 100);
  const isUnlimited = limit === 'unlimited';
  
  // Determine status color based on usage
  const getStatusColor = () => {
    if (isUnlimited) return 'text-green-600';
    if (percentage >= 90) return 'text-red-600';
    if (percentage >= 75) return 'text-orange-600';
    if (percentage >= 50) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getStatusIcon = () => {
    if (isUnlimited) return <CheckCircle className="w-5 h-5 text-green-600" />;
    if (percentage >= 90) return <AlertTriangle className="w-5 h-5 text-red-600" />;
    if (percentage >= 75) return <AlertTriangle className="w-5 h-5 text-orange-600" />;
    return <Activity className="w-5 h-5 text-green-600" />;
  };

  const getProgressBarColor = () => {
    if (isUnlimited) return 'bg-green-500';
    if (percentage >= 90) return 'bg-red-500';
    if (percentage >= 75) return 'bg-orange-500';
    if (percentage >= 50) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 border border-orange-100 hover:shadow-xl transition-shadow duration-300">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          {getStatusIcon()}
          <h3 className="text-lg font-semibold text-gray-800">API Usage</h3>
        </div>
        <span className="text-xs px-2 py-1 rounded-full bg-orange-100 text-orange-700 font-medium">
          {tier.charAt(0).toUpperCase() + tier.slice(1)}
        </span>
      </div>

      {/* Usage Stats */}
      <div className="mb-4">
        <div className="flex items-end justify-between mb-2">
          <div>
            <p className={`text-3xl font-bold ${getStatusColor()}`}>
              {isUnlimited ? '∞' : api_calls.toLocaleString()}
            </p>
            <p className="text-sm text-gray-500">
              {isUnlimited ? 'Unlimited calls' : `of ${limit.toLocaleString()} calls`}
            </p>
          </div>
          {!isUnlimited && (
            <div className="text-right">
              <p className="text-lg font-semibold text-gray-700">
                {remaining.toLocaleString()}
              </p>
              <p className="text-xs text-gray-500">remaining</p>
            </div>
          )}
        </div>

        {/* Progress Bar */}
        {!isUnlimited && (
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className={`h-full ${getProgressBarColor()} transition-all duration-500 rounded-full`}
              style={{ width: `${Math.min(percentage, 100)}%` }}
            ></div>
          </div>
        )}
      </div>

      {/* Status Message */}
      <div className="flex items-start gap-2 p-3 bg-gradient-to-r from-orange-50 to-amber-50 rounded-lg">
        <TrendingUp className="w-4 h-4 text-orange-600 mt-0.5 flex-shrink-0" />
        <div className="flex-1 min-w-0">
          {isUnlimited ? (
            <p className="text-sm text-gray-700">
              <span className="font-semibold text-green-600">Unlimited access! </span>
              You're on the Professional plan with no API limits.
            </p>
          ) : percentage >= 90 ? (
            <p className="text-sm text-gray-700">
              <span className="font-semibold text-red-600">Quota almost reached! </span>
              Upgrade to continue using the service without interruption.
            </p>
          ) : percentage >= 75 ? (
            <p className="text-sm text-gray-700">
              <span className="font-semibold text-orange-600">High usage detected. </span>
              Consider upgrading to avoid hitting your limit.
            </p>
          ) : percentage >= 50 ? (
            <p className="text-sm text-gray-700">
              <span className="font-semibold text-yellow-600">Halfway there! </span>
              You've used {percentage}% of your monthly quota.
            </p>
          ) : (
            <p className="text-sm text-gray-700">
              <span className="font-semibold text-green-600">Looking good! </span>
              You have plenty of API calls remaining this month.
            </p>
          )}
        </div>
      </div>

      {/* Upgrade Button */}
      {!isUnlimited && percentage >= 75 && (
        <button
          onClick={() => window.location.href = '/pricing'}
          className="mt-4 w-full py-2 px-4 bg-gradient-to-r from-orange-600 to-green-800 text-white rounded-lg font-medium hover:from-orange-700 hover:to-green-900 transition-all duration-300 flex items-center justify-center gap-2 group"
        >
          Upgrade Plan
          <ArrowUpRight className="w-4 h-4 group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform duration-300" />
        </button>
      )}
    </div>
  );
}
