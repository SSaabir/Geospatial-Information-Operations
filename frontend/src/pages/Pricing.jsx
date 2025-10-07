import React, { useState } from 'react';
import { Check, Lock, Zap, Brain, BarChart3, FileText, Database, Cloud } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const plans = [
  {
    id: 'free',
    name: 'Free',
    price: '$0',
    period: '/mo',
    features: [
      '24-hour forecast',
      'Basic 1-day temp trend (Linear Regression)',
      'View-only Data Exchange',
      'Basic trends & graphs',
    ],
  },
  {
    id: 'researcher',
    name: 'Researcher',
    price: '$29',
    period: '/mo',
    features: [
      '7-day forecast + ML prediction',
      'Confidence intervals (75-95%)',
      'Download datasets (5 years history)',
      'Advanced visualization',
      'PDF/Excel reports',
      '5,000 API calls/mo',
    ],
  },
  {
    id: 'professional',
    name: 'Professional',
    price: '$99',
    period: '/mo',
    features: [
      'Seasonal outlook + risk analysis (Ensemble AI)',
      '20+ years historical data',
      'Upload + sell datasets',
      'Enterprise analytics',
      'Full + custom reports',
      'Unlimited API calls',
    ],
  },
];

export default function Pricing() {
  const { user, tier, changeTier, apiCall } = useAuth();
  const navigate = useNavigate();
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
    // For paid plans, create a checkout session and navigate to the checkout
    // UI where the user can enter card details. The checkout page will call
    // the `POST /payments/session/{id}/pay` endpoint to record payment.
    try {
      const resp = await apiCall('/payments/create-session', {
        method: 'POST',
        body: JSON.stringify({ plan: planId, recurring: false }),
      });

      if (!resp || !resp.session_id) {
        window.alert('Failed to create checkout session');
        return;
      }

      // Navigate to checkout page within the app
      navigate(`/payments/checkout/${resp.session_id}`);
    } catch (e) {
      console.error('Create session failed', e);
      window.alert(e.message || 'Failed to initiate checkout');
    }
  };

  return (
    <div className="min-h-screen w-full p-6" style={{ background: 'linear-gradient(135deg, #F5EFFF 0%, #E5D9F2 50%, #CDC1FF 100%)' }}>
      <div className="w-full max-w-6xl mx-auto">
        <div className="text-center mb-10">
          <h1 className="text-5xl font-bold text-gray-800 mb-3">Commercialization Plans</h1>
          <p className="text-gray-600">Choose the plan that unlocks the AI forecasting power you need</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {plans.map((plan) => (
            <div key={plan.id} className="bg-white rounded-2xl shadow-xl p-6 border" style={{ borderColor: '#E5D9F2' }}>
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
                    <Check className="w-4 h-4 text-purple-600" />
                    <span>{f}</span>
                  </li>
                ))}
              </ul>
              <button
                onClick={() => handleSelect(plan.id)}
                className="w-full py-3 rounded-lg font-semibold text-white transition-all duration-300 hover:transform hover:-translate-y-0.5"
                style={{ background: 'linear-gradient(135deg, #A294F9 0%, #CDC1FF 100%)' }}
              >
                {tier === plan.id ? 'Selected' : 'Choose Plan'}
              </button>
            </div>
          ))}
        </div>

        <div className="mt-12 bg-white rounded-2xl shadow-xl p-6 border" style={{ borderColor: '#E5D9F2' }}>
          <div className="flex items-start justify-between flex-wrap gap-3 mb-3">
            <h3 className="text-2xl font-bold">Feature Matrix</h3>
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <span className="inline-flex items-center gap-1"><span className="w-2 h-2 rounded-full" style={{ backgroundColor: '#E5D9F2' }}></span> Current Plan</span>
              <span className="inline-flex items-center gap-1"><Check className="w-3 h-3 text-purple-600" /> Included</span>
            </div>
          </div>

          <div className="overflow-x-auto rounded-lg border shadow-xl shadow-purple-100/60" style={{ borderColor: '#E5D9F2', perspective: '1000px' }}>
            <table className="w-full text-left">
              <thead className="sticky top-0 bg-white/80 backdrop-blur">
                <tr className="border-b shadow-sm" style={{ borderColor: '#E5D9F2', transformStyle: 'preserve-3d' }}>
                  <th className="p-3">Feature</th>
                  <th className={`p-3 ${tier === 'free' ? 'bg-purple-50' : ''}`}>Free</th>
                  <th className={`p-3 ${tier === 'researcher' ? 'bg-purple-50' : ''}`}>Researcher</th>
                  <th className={`p-3 ${tier === 'professional' ? 'bg-purple-50' : ''}`}>Professional</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ['Forecast Data', '24 hrs only', '7-day forecast', 'Full + Seasonal outlook'],
                  ['Trends & Graphs', 'Basic', 'Advanced visualization', 'Enterprise analytics'],
                  ['Reports', 'None', 'PDF/Excel summary', 'Full + Custom reports'],
                  ['Historical Data', 'No', 'Limited (5 years)', 'Full (20+ years)'],
                  ['API Calls / Month', '5', '5,000', 'Unlimited'],
                  ['Data Exchange Market', 'View only', 'Download', 'Upload + Sell data'],
                  ['Prediction (AI/ML)', 'Basic model (1-day temp trend)', 'ML prediction (7-day + CI)', 'Advanced AI (seasonal + risk)'],
                ].map(([feature, free, res, pro], idx) => (
                  <tr
                    key={feature}
                    className={`border-t transition-all duration-300 ${idx % 2 === 0 ? 'bg-white' : ''}`}
                    style={{
                      borderColor: '#E5D9F2',
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
                      <td key={i} className={`p-3 align-middle ${[ 'free','researcher','professional' ][i] === tier ? 'bg-purple-50' : ''}`}>
                        <span className="inline-block px-2 py-1 rounded-full text-xs font-medium shadow-sm" style={{ backgroundColor: '#F5EFFF', color: '#6B5CC8' }} title={String(val)}>
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



