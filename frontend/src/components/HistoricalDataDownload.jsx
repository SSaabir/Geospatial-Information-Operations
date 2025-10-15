import React, { useState } from 'react';
import { Download, Calendar, MapPin, AlertCircle, CheckCircle, Loader } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export default function HistoricalDataDownload() {
  const { user, apiCall } = useAuth();
  const [city, setCity] = useState('Colombo');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [accessInfo, setAccessInfo] = useState(null);

  // Available cities
  const cities = ['Colombo', 'Jaffna', 'Kandy', 'Matara', 'Trincomalee'];

  // Get tier info
  const tierInfo = {
    free: { days: 30, label: 'Last 30 days' },
    researcher: { days: 365, label: 'Last 1 year' },
    professional: { days: Infinity, label: 'Full archive (28 years)' }
  };

  const userTier = user?.tier || 'free';
  const tierLimit = tierInfo[userTier];

  // Calculate oldest accessible date
  const getOldestDate = () => {
    const today = new Date();
    if (tierLimit.days === Infinity) {
      return new Date('1997-01-31'); // Earliest data
    }
    const oldest = new Date(today);
    oldest.setDate(today.getDate() - tierLimit.days);
    return oldest;
  };

  const formatDate = (date) => {
    return date.toISOString().split('T')[0];
  };

  // Fetch access limits
  React.useEffect(() => {
    const fetchAccessLimits = async () => {
      try {
        const response = await apiCall('/historical/access-limits');
        setAccessInfo(response);
      } catch (err) {
        console.error('Failed to fetch access limits:', err);
      }
    };
    fetchAccessLimits();
  }, []);

  const handleDownload = async (format = 'csv') => {
    setError('');
    setSuccess('');

    // Validation
    if (!startDate || !endDate) {
      setError('Please select both start and end dates');
      return;
    }

    const start = new Date(startDate);
    const end = new Date(endDate);

    if (start > end) {
      setError('Start date must be before end date');
      return;
    }

    // Check if within tier limits
    const oldest = getOldestDate();
    if (start < oldest) {
      setError(`Your ${userTier} tier only allows access to data from ${formatDate(oldest)}. Please upgrade for more historical data.`);
      return;
    }

    setLoading(true);

    try {
      // Fetch historical data
      const response = await apiCall(
        `/historical/weather?city=${city}&start_date=${startDate}&end_date=${endDate}`
      );

      if (!response.success) {
        throw new Error(response.error || 'Failed to fetch data');
      }

      // Convert to CSV or JSON
      let content;
      let filename;
      let mimeType;

      if (format === 'csv') {
        // Convert to CSV
        const data = response.data;
        if (data.length === 0) {
          setError('No data available for the selected date range');
          return;
        }

        const headers = Object.keys(data[0]).join(',');
        const rows = data.map(row => Object.values(row).map(v => 
          typeof v === 'string' && v.includes(',') ? `"${v}"` : v
        ).join(','));
        
        content = [headers, ...rows].join('\n');
        filename = `weather_data_${city}_${startDate}_to_${endDate}.csv`;
        mimeType = 'text/csv';
      } else {
        // JSON format
        content = JSON.stringify(response, null, 2);
        filename = `weather_data_${city}_${startDate}_to_${endDate}.json`;
        mimeType = 'application/json';
      }

      // Create download link
      const blob = new Blob([content], { type: mimeType });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      setSuccess(`Successfully downloaded ${response.record_count} records!`);
    } catch (err) {
      console.error('Download error:', err);
      
      // Handle tier limit error
      if (err.response?.status === 403) {
        const detail = err.response.data.detail;
        if (typeof detail === 'object' && detail.message) {
          setError(detail.message + ' ' + (detail.upgrade_benefits || ''));
        } else {
          setError(detail || 'Access denied. Please upgrade your plan for more historical data.');
        }
      } else {
        setError(err.message || 'Failed to download data. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white/80 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-orange-100">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-gray-800 flex items-center">
          <Download className="w-5 h-5 mr-2 text-orange-600" />
          Download Historical Data
        </h3>
        <div className="text-sm text-gray-600 bg-orange-50 px-3 py-1 rounded-full">
          {tierLimit.label}
        </div>
      </div>

      {/* Access Info */}
      {accessInfo && (
        <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
          <p className="text-sm text-blue-800">
            <strong>Your Access:</strong> {accessInfo.historical_data_access.days}
            {' '}(from {accessInfo.historical_data_access.oldest_accessible_date})
          </p>
        </div>
      )}

      <div className="space-y-4">
        {/* City Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            <MapPin className="w-4 h-4 inline mr-1" />
            City
          </label>
          <select
            value={city}
            onChange={(e) => setCity(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
          >
            {cities.map(c => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>

        {/* Date Range */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Calendar className="w-4 h-4 inline mr-1" />
              Start Date
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              min={formatDate(getOldestDate())}
              max={formatDate(new Date())}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Calendar className="w-4 h-4 inline mr-1" />
              End Date
            </label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              min={startDate || formatDate(getOldestDate())}
              max={formatDate(new Date())}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Error/Success Messages */}
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg flex items-start">
            <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 mr-2 flex-shrink-0" />
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {success && (
          <div className="p-3 bg-green-50 border border-green-200 rounded-lg flex items-start">
            <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 mr-2 flex-shrink-0" />
            <p className="text-sm text-green-800">{success}</p>
          </div>
        )}

        {/* Download Buttons */}
        <div className="flex gap-3">
          <button
            onClick={() => handleDownload('csv')}
            disabled={loading}
            className="flex-1 px-4 py-3 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-lg font-medium hover:from-orange-600 hover:to-orange-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {loading ? (
              <>
                <Loader className="w-4 h-4 mr-2 animate-spin" />
                Downloading...
              </>
            ) : (
              <>
                <Download className="w-4 h-4 mr-2" />
                Download CSV
              </>
            )}
          </button>
          
          <button
            onClick={() => handleDownload('json')}
            disabled={loading}
            className="flex-1 px-4 py-3 bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-lg font-medium hover:from-purple-600 hover:to-purple-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {loading ? (
              <>
                <Loader className="w-4 h-4 mr-2 animate-spin" />
                Downloading...
              </>
            ) : (
              <>
                <Download className="w-4 h-4 mr-2" />
                Download JSON
              </>
            )}
          </button>
        </div>

        {/* Upgrade Link */}
        {userTier !== 'professional' && (
          <div className="text-center pt-2">
            <a
              href="/pricing"
              className="text-sm text-orange-600 hover:text-orange-700 font-medium"
            >
              Upgrade for more historical data →
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
