import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Upload, Download, Eye, DollarSign } from 'lucide-react';
import FeatureGate from '../components/FeatureGate';

export default function Marketplace() {
  const { tier } = useAuth();

  return (
    <div className="min-h-screen w-full p-6" style={{ background: 'linear-gradient(135deg, #F5EFFF 0%, #E5D9F2 50%, #CDC1FF 100%)' }}>
      <div className="w-full max-w-6xl mx-auto bg-white rounded-2xl shadow-xl p-6">
        <h1 className="text-3xl font-bold mb-6">Data Exchange Marketplace</h1>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="p-4 rounded-lg border" style={{ borderColor: '#E5D9F2' }}>
            <Eye className="w-5 h-5 inline-block mr-2" /> View Datasets (All tiers)
            <p className="text-gray-600 mt-2">Browse curated climate datasets.</p>
          </div>
          <div className="p-4 rounded-lg border" style={{ borderColor: '#E5D9F2' }}>
            <Download className="w-5 h-5 inline-block mr-2" /> Download (Researcher+)
            <p className="text-gray-600 mt-2">Access files for offline analysis.</p>
          </div>
          <div className="p-4 rounded-lg border" style={{ borderColor: '#E5D9F2' }}>
            <Upload className="w-5 h-5 inline-block mr-2" /> Upload + Sell (Professional)
            <p className="text-gray-600 mt-2">Monetize your datasets.</p>
          </div>
        </div>

        <div className="space-y-6">
          <div className="p-4 rounded-lg border" style={{ borderColor: '#E5D9F2' }}>
            <h2 className="text-xl font-semibold mb-3">Catalog</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[1,2,3,4].map((i) => (
                <div key={i} className="p-4 rounded-lg border flex items-center justify-between" style={{ borderColor: '#E5D9F2' }}>
                  <div>
                    <div className="font-medium">Dataset #{i}</div>
                    <div className="text-gray-500 text-sm">Region: Global • Size: ~120MB</div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <a href="#" className="px-3 py-2 rounded bg-gray-100">Preview</a>
                    <FeatureGate minTier="researcher" fallback={<button className="px-3 py-2 rounded bg-gray-100">Locked</button>}>
                      <a href="#" className="px-3 py-2 rounded text-white" style={{ background: 'linear-gradient(135deg, #A294F9 0%, #CDC1FF 100%)' }}>Download</a>
                    </FeatureGate>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="p-4 rounded-lg border" style={{ borderColor: '#E5D9F2' }}>
            <h2 className="text-xl font-semibold mb-3">Sell Your Data</h2>
            <FeatureGate minTier="professional" fallback={<div className="text-gray-600">Upgrade to Professional to upload and monetize datasets.</div>}>
              <div className="flex items-center space-x-3">
                <input type="file" className="border rounded p-2" />
                <button className="px-4 py-2 rounded text-white" style={{ background: 'linear-gradient(135deg, #A294F9 0%, #CDC1FF 100%)' }}>
                  <DollarSign className="w-4 h-4 inline-block mr-1" /> Upload & List
                </button>
              </div>
            </FeatureGate>
          </div>
        </div>
      </div>
    </div>
  );
}



