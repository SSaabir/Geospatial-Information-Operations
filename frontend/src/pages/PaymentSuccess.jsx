import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { CheckCircle, Download, ArrowRight, TrendingUp, BarChart3 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const PaymentSuccess = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { user, refreshUser, isLoading: authLoading } = useAuth();
  
  const sessionId = searchParams.get('session');
  const planId = searchParams.get('plan') || 'researcher';
  const [sessionDetails, setSessionDetails] = useState(null);
  const [loading, setLoading] = useState(true);

  const planDetails = {
    researcher: { 
      name: 'Researcher', 
      price: 29,
      features: [
        '7-day forecast with ML predictions',
        'Download datasets (5 years history)',
        'Advanced visualizations',
        'PDF/Excel reports',
        '5,000 API calls per month'
      ]
    },
    professional: { 
      name: 'Professional', 
      price: 99,
      features: [
        'Seasonal outlook with AI analysis',
        '20+ years historical data access',
        'Priority support & consultation',
        'Enterprise analytics dashboard',
        'Unlimited API calls',
        'Custom reports & exports'
      ]
    }
  };

  const plan = planDetails[planId] || planDetails.researcher;

  useEffect(() => {
    const fetchSession = async () => {
      if (!sessionId) {
        setLoading(false);
        return;
      }

      try {
        const { apiCall } = useAuth.getState();
        const response = await apiCall(`/payments/session/${sessionId}`, {
          method: 'GET'
        });
        setSessionDetails(response);
      } catch (error) {
        console.error('Failed to fetch session:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSession();
    
    // Refresh user to get updated tier
    if (refreshUser) {
      refreshUser();
    }
  }, [sessionId, refreshUser]);

  const handleContinue = () => {
    navigate('/dashboard');
  };

  // Show loading while auth is being verified
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: '#F9F5F0' }}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 mx-auto mb-4" style={{ borderColor: '#F4991A' }}></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: '#F9F5F0' }}>
        <div className="text-center">
          <p className="text-gray-600 mb-4">Please log in to view this page</p>
          <button 
            onClick={() => navigate('/login')}
            className="px-6 py-2 rounded-lg text-white"
            style={{ backgroundColor: '#F4991A' }}
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-12 px-4" style={{ backgroundColor: '#F9F5F0' }}>
      <div className="max-w-4xl mx-auto">
        {/* Success Header */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8 text-center border" style={{ borderColor: '#F2EAD3' }}>
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full mb-6" style={{ backgroundColor: '#F2EAD3' }}>
            <CheckCircle className="w-12 h-12" style={{ color: '#F4991A' }} />
          </div>
          
          <h1 className="text-4xl font-bold mb-4 text-gray-800">Payment Successful!</h1>
          <p className="text-xl text-gray-600 mb-6">
            Welcome to the {plan.name} plan
          </p>

          {sessionDetails && sessionDetails.last4 && (
            <p className="text-sm text-gray-500">
              Charged to card ending in •••• {sessionDetails.last4}
            </p>
          )}

          <div className="inline-flex items-center space-x-2 mt-6 px-6 py-3 rounded-full" style={{ backgroundColor: '#F9F5F0' }}>
            <span className="text-sm font-semibold text-gray-700">Amount Paid:</span>
            <span className="text-2xl font-bold" style={{ color: '#F4991A' }}>${plan.price}/mo</span>
          </div>
        </div>

        {/* What's Next Section */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8 border" style={{ borderColor: '#F2EAD3' }}>
          <h2 className="text-2xl font-bold mb-6 text-gray-800">What's Included</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {plan.features.map((feature, index) => (
              <div key={index} className="flex items-start space-x-3 p-4 rounded-lg" style={{ backgroundColor: '#F9F5F0' }}>
                <CheckCircle className="w-5 h-5 mt-0.5 flex-shrink-0" style={{ color: '#F4991A' }} />
                <span className="text-gray-700">{feature}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Dashboard */}
          <button
            onClick={() => navigate('/dashboard')}
            className="bg-white rounded-xl p-6 border hover:shadow-xl transition-all duration-200 hover:scale-105 text-left"
            style={{ borderColor: '#F2EAD3' }}
          >
            <div className="w-12 h-12 rounded-lg flex items-center justify-center mb-4" style={{ backgroundColor: '#F9F5F0' }}>
              <BarChart3 className="w-6 h-6" style={{ color: '#F4991A' }} />
            </div>
            <h3 className="font-semibold text-gray-800 mb-2">Go to Dashboard</h3>
            <p className="text-sm text-gray-600">View your analytics and insights</p>
          </button>

          {/* Download Data */}
          <button
            onClick={() => navigate('/analytics')}
            className="bg-white rounded-xl p-6 border hover:shadow-xl transition-all duration-200 hover:scale-105 text-left"
            style={{ borderColor: '#F2EAD3' }}
          >
            <div className="w-12 h-12 rounded-lg flex items-center justify-center mb-4" style={{ backgroundColor: '#F2EAD3' }}>
              <Download className="w-6 h-6" style={{ color: '#F4991A' }} />
            </div>
            <h3 className="font-semibold text-gray-800 mb-2">Download Data</h3>
            <p className="text-sm text-gray-600">Access historical datasets</p>
          </button>

          {/* Workflow */}
          <button
            onClick={() => navigate('/workflow')}
            className="bg-white rounded-xl p-6 border hover:shadow-xl transition-all duration-200 hover:scale-105 text-left"
            style={{ borderColor: '#F2EAD3' }}
          >
            <div className="w-12 h-12 rounded-lg flex items-center justify-center mb-4" style={{ backgroundColor: '#F2EAD3' }}>
              <TrendingUp className="w-6 h-6" style={{ color: '#F4991A' }} />
            </div>
            <h3 className="font-semibold text-gray-800 mb-2">View Workflow</h3>
            <p className="text-sm text-gray-600">Explore AI predictions</p>
          </button>
        </div>

        {/* CTA Button */}
        <div className="text-center">
          <button
            onClick={handleContinue}
            className="inline-flex items-center space-x-2 px-8 py-4 rounded-xl text-white font-semibold text-lg transition-all duration-200 hover:scale-105 shadow-lg"
            style={{ backgroundColor: '#F4991A' }}
          >
            <span>Continue to Dashboard</span>
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>

        {/* Support Notice */}
        <div className="mt-8 p-6 rounded-xl border text-center" style={{ backgroundColor: 'white', borderColor: '#F2EAD3' }}>
          <p className="text-gray-600">
            Need help getting started? Check out our{' '}
            <button 
              onClick={() => navigate('/faq')}
              className="font-semibold hover:underline"
              style={{ color: '#F4991A' }}
            >
              FAQ
            </button>
            {' '}or{' '}
            <button 
              onClick={() => navigate('/contact')}
              className="font-semibold hover:underline"
              style={{ color: '#F4991A' }}
            >
              contact support
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default PaymentSuccess;
