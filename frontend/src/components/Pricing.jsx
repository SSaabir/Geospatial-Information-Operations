import React, { useState } from 'react';
import { Check, Lock, Zap, Brain, BarChart3, FileText, Database, Cloud } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const plans = [
  {
    id: 'free',
    name: 'Free',
    price: '$0',
    period: '/mo',
    features: [
      'Current weather data & trends',
      'Last 30 days historical data',
      'Basic map view',
      'Interactive map view',
      '5 AI operations/mo',
    ],
  },
  {
    id: 'researcher',
    name: 'Researcher',
    price: '$29',
    period: '/mo',
    features: [
      'Last 1 year historical data (365 days)',
      'Weather prediction available',
      'Interactive map with details',
      'Advanced visualization',
      'PDF/Excel report export',
      '5,000 AI operations/mo',
    ],
  },
  {
    id: 'professional',
    name: 'Professional',
    price: '$99',
    period: '/mo',
    features: [
      'Full 28-year archive (1997-2025)',
      'Weather prediction available',
      'Advanced map layers (Satellite, Terrain)',
      'Priority support',
      'Enterprise analytics',
      'Custom report templates',
      'Unlimited AI operations',
    ],
  },
];

export default function Pricing() {
  const { user, tier, changeTier, apiCall } = useAuth();
  const [hoveredRow, setHoveredRow] = useState(null);

  const handleSelect = async (planId) => {
    if (!user) {
      window.alert('Please login to change your plan.');
      return;
    }
    if (tier === planId) return;
    if (planId === 'free') {
      const result = await changeTier(planId);
      if (!result.success) {
        window.alert(result.error || 'Failed to change plan');
      }
      return;
    }
    // Navigate to checkout page with plan parameter
    window.location.href = `/checkout?plan=${planId}`;
  };

  return (
    <div className="min-h-screen w-full p-6" style={{ background: 'linear-gradient(135deg, #F9F5F0 0%, #F2EAD3 50%, #F2EAD3 100%)' }}>
      <div className="w-full max-w-6xl mx-auto">
        <div className="text-center mb-10">
          <h1 className="text-5xl font-bold text-gray-800 mb-3">Commercialization Plans</h1>
          <p className="text-gray-600">Choose the plan that unlocks the AI forecasting power you need</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {plans.map((plan) => (
            <div key={plan.id} className="bg-white rounded-2xl shadow-xl p-6 border" style={{ borderColor: '#F2EAD3' }}>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold">{plan.name}</h2>
                {tier === plan.id ? (
                  <span className="text-xs px-2 py-1 rounded bg-green-100 text-green-700">Current</span>
                ) : null}
              </div>
              <div className="mb-6">
                <span className="text-4xl font-extrabold">{plan.price}</span>
                <span className="text-gray-500">{plan.period}</span>
              </div>
              <ul className="space-y-3 mb-6">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-center space-x-3">
                    <Check className="w-4 h-4 text-orange-600" />
                    <span>{f}</span>
                  </li>
                ))}
              </ul>
              <button
                onClick={() => handleSelect(plan.id)}
                className="w-full py-3 rounded-lg font-semibold text-white transition-all duration-300 hover:transform hover:-translate-y-0.5"
                style={{ background: 'linear-gradient(135deg, #F4991A 0%, #F2EAD3 100%)' }}
              >
                {tier === plan.id ? 'Selected' : 'Choose Plan'}
              </button>
            </div>
          ))}
        </div>

        <div className="mt-12 bg-white rounded-2xl shadow-xl p-6 border" style={{ borderColor: '#F2EAD3' }}>
          <div className="flex items-start justify-between flex-wrap gap-3 mb-3">
            <h3 className="text-2xl font-bold">Feature Matrix</h3>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <span className="inline-flex items-center gap-1"><span className="w-2 h-2 rounded-full" style={{ backgroundColor: '#F2EAD3' }}></span> Current Plan</span>
              <span className="inline-flex items-center gap-1"><Check className="w-3 h-3 text-orange-600" /> Included</span>
            </div>
          </div>

          <div className="overflow-x-auto rounded-lg border shadow-xl shadow-orange-100/60" style={{ borderColor: '#F2EAD3', perspective: '1000px' }}>
            <table className="w-full text-left">
              <thead className="sticky top-0 bg-white/80 backdrop-blur">
                <tr className="border-b shadow-sm" style={{ borderColor: '#F2EAD3', transformStyle: 'preserve-3d' }}>
                  <th className="p-3">Feature</th>
                  <th className={`p-3 ${tier === 'free' ? 'bg-orange-50' : ''}`}>Free</th>
                  <th className={`p-3 ${tier === 'researcher' ? 'bg-orange-50' : ''}`}>Researcher</th>
                  <th className={`p-3 ${tier === 'professional' ? 'bg-orange-50' : ''}`}>Professional</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ['Historical Data Access', 'Last 30 days', 'Last 1 year (365 days)', 'Full archive (28 years)'],
                  ['Weather Prediction', 'Available', 'Available', 'Available'],
                  ['Trends & Graphs', 'Basic', 'Advanced visualization', 'Enterprise analytics'],
                  ['Reports', 'View only', 'PDF/Excel export', 'Custom templates'],
                  ['Map View', 'Basic', 'Interactive', 'Advanced layers'],
                  ['AI Operations / Month', '5', '5,000', 'Unlimited'],
                  ['Support', 'Community', 'Email support', 'Priority support'],
                ].map(([feature, free, res, pro], idx) => (
                  <tr
                    key={feature}
                    className={`border-t transition-all duration-300 ${idx % 2 === 0 ? 'bg-white' : ''}`}
                    style={{
                      borderColor: '#F2EAD3',
                      transformStyle: 'preserve-3d',
                      transform:
                        hoveredRow === idx
                          ? 'translateZ(8px) rotateX(0.6deg)'
                          : 'translateZ(0px) rotateX(0deg)',
                      boxShadow:
                        hoveredRow === idx
                          ? '0 18px 30px -12px rgba(162,148,249,0.35), 0 6px 12px -6px rgba(0,0,0,0.08)'
                          : '0 1px 0 rgba(0,0,0,0.02)'
                    }}
                    onMouseEnter={() => setHoveredRow(idx)}
                    onMouseLeave={() => setHoveredRow(null)}
                  >
                    <td className="p-3 font-medium text-gray-800">{feature}</td>
                    {[free, res, pro].map((val, i) => (
                      <td key={i} className={`p-3 align-middle ${[ 'free','researcher','professional' ][i] === tier ? 'bg-orange-50' : ''}`}>
                        <span className="inline-block px-2 py-1 rounded-full text-xs font-medium shadow-sm" style={{ backgroundColor: '#F9F5F0', color: '#6B5CC8' }} title={String(val)}>
                          {typeof val === 'string' ? val : String(val)}
                        </span>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}



