import React, { useEffect, useState } from 'react';
import FeatureGate from '../components/FeatureGate';
import { BarChart3, FileText, Activity, Download } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export default function Analytics() {
  const { apiCall } = useAuth();
  const [metrics, setMetrics] = useState({ api_calls: 0, reports_generated: 0, data_downloads: 0, limit: 5, remaining: 5, tier: 'free' });

  useEffect(() => {
    let isMounted = true;
    (async () => {
      try {
        const data = await apiCall('/analytics/usage');
        if (isMounted) setMetrics(data);
      } catch (e) {
        // ignore
      }
    })();
    return () => { isMounted = false; };
  }, []);

  return (
    <div className="min-h-screen w-full p-6" style={{ background: 'linear-gradient(135deg, #F5EFFF 0%, #E5D9F2 50%, #CDC1FF 100%)' }}>
      <div className="w-full max-w-6xl mx-auto bg-white rounded-2xl shadow-xl p-6">
        <h1 className="text-3xl font-bold mb-6">Usage Analytics</h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="p-4 rounded-lg border" style={{ borderColor: '#E5D9F2' }}>
            <Activity className="w-5 h-5 inline-block mr-2" /> API Calls
            <div className="text-2xl font-bold mt-2">{metrics.api_calls}</div>
            <div className="text-sm text-gray-500 mt-1">
              {metrics.limit === Infinity ? 'Unlimited' : `${metrics.remaining} remaining of ${metrics.limit}`}
            </div>
            {metrics.remaining === 0 && metrics.limit !== Infinity && (
              <div className="text-xs text-red-500 mt-1">Limit reached - upgrade to continue</div>
            )}
          </div>
          <div className="p-4 rounded-lg border" style={{ borderColor: '#E5D9F2' }}>
            <FileText className="w-5 h-5 inline-block mr-2" /> Reports Generated
            <div className="text-2xl font-bold mt-2">{metrics.reports_generated}</div>
          </div>
          <div className="p-4 rounded-lg border" style={{ borderColor: '#E5D9F2' }}>
            <Download className="w-5 h-5 inline-block mr-2" /> Data Downloads
            <div className="text-2xl font-bold mt-2">{metrics.data_downloads}</div>
          </div>
        </div>

        <FeatureGate minTier="professional" fallback={<div className="p-4 rounded-lg border bg-gray-50 text-gray-600" style={{ borderColor: '#E5D9F2' }}>Upgrade to Professional for Market Earnings analytics.</div>}>
          <div className="p-4 rounded-lg border" style={{ borderColor: '#E5D9F2' }}>
            <h2 className="text-xl font-semibold mb-3">Market Earnings</h2>
            <div className="text-2xl font-bold">$1,245</div>
            <div className="text-gray-500">Last 30 days</div>
          </div>
        </FeatureGate>
      </div>
    </div>
  );
}



