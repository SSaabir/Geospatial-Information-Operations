import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { CreditCard, Lock, ArrowLeft, Check } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const Checkout = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { user, apiCall, isLoading: authLoading } = useAuth();
  
  const planId = searchParams.get('plan') || 'researcher';
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Form state
  const [cardNumber, setCardNumber] = useState('');
  const [expMonth, setExpMonth] = useState('');
  const [expYear, setExpYear] = useState('');
  const [cvc, setCvc] = useState('');
  const [cardholderName, setCardholderName] = useState('');

  // Plan details
  const planDetails = {
    free: { name: 'Free', price: 0, features: ['24-hour forecast', 'Basic trends'] },
    researcher: { 
      name: 'Researcher', 
      price: 29, 
      features: ['7-day forecast + ML', 'Download datasets (5 years)', 'PDF/Excel reports', '5,000 API calls/mo'] 
    },
    professional: { 
      name: 'Professional', 
      price: 99, 
      features: ['Seasonal outlook', '20+ years data', 'Priority support', 'Unlimited API calls'] 
    }
  };

  const plan = planDetails[planId] || planDetails.researcher;

  useEffect(() => {
    // Wait for auth to finish loading before redirecting
    if (authLoading) {
      return;
    }
    
    if (!user) {
      navigate('/login?redirect=/checkout?plan=' + planId);
      return;
    }
    
    // Create checkout session
    const createSession = async () => {
      try {
        setLoading(true);
        const response = await apiCall('/payments/create-session', {
          method: 'POST',
          body: JSON.stringify({ plan: planId, recurring: true })
        });
        setSessionId(response.session_id);
      } catch (err) {
        setError(err.message || 'Failed to create checkout session');
      } finally {
        setLoading(false);
      }
    };

    createSession();
  }, [user, planId, authLoading, navigate, apiCall]);

  const formatCardNumber = (value) => {
    const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
    const matches = v.match(/\d{4,16}/g);
    const match = (matches && matches[0]) || '';
    const parts = [];
    
    for (let i = 0; i < match.length; i += 4) {
      parts.push(match.substring(i, i + 4));
    }
    
    return parts.length ? parts.join(' ') : value;
  };

  const handleCardNumberChange = (e) => {
    const formatted = formatCardNumber(e.target.value);
    setCardNumber(formatted);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!sessionId) {
      setError('Session not ready. Please wait...');
      return;
    }

    // Basic validation
    const cleanCardNumber = cardNumber.replace(/\s/g, '');
    if (cleanCardNumber.length < 13 || cleanCardNumber.length > 19) {
      setError('Please enter a valid card number');
      return;
    }

    if (!expMonth || !expYear) {
      setError('Please enter card expiry date');
      return;
    }

    if (!cvc || cvc.length < 3) {
      setError('Please enter a valid CVC');
      return;
    }

    try {
      setLoading(true);
      setError('');

      const response = await apiCall(`/payments/session/${sessionId}/pay`, {
        method: 'POST',
        body: JSON.stringify({
          card_number: cleanCardNumber,
          exp_month: parseInt(expMonth),
          exp_year: parseInt(expYear),
          cvc: cvc
        })
      });

      if (response.success) {
        // Redirect to success page
        navigate(`/payment-success?session=${sessionId}&plan=${planId}`);
      } else {
        setError('Payment failed. Please try again.');
      }
    } catch (err) {
      setError(err.message || 'Payment processing failed');
    } finally {
      setLoading(false);
    }
  };

  // Show loading while auth is being verified
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: '#F5EFFF' }}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 mx-auto mb-4" style={{ borderColor: '#A294F9' }}></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: '#F5EFFF' }}>
        <div className="text-center">
          <p className="text-gray-600 mb-4">Please log in to continue with checkout</p>
          <button 
            onClick={() => navigate('/login')}
            className="px-6 py-2 rounded-lg text-white"
            style={{ backgroundColor: '#A294F9' }}
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-12 px-4" style={{ backgroundColor: '#F5EFFF' }}>
      <div className="max-w-4xl mx-auto">
        {/* Back button */}
        <button
          onClick={() => navigate('/pricing')}
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-800 mb-8"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back to Pricing</span>
        </button>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Order Summary */}
          <div className="bg-white rounded-2xl shadow-xl p-8 border" style={{ borderColor: '#E5D9F2' }}>
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Order Summary</h2>
            
            <div className="mb-6 p-6 rounded-xl" style={{ backgroundColor: '#F5EFFF' }}>
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-semibold text-gray-800">{plan.name} Plan</h3>
                  <p className="text-sm text-gray-600">Monthly subscription</p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold" style={{ color: '#A294F9' }}>${plan.price}</p>
                  <p className="text-sm text-gray-600">/month</p>
                </div>
              </div>

              <div className="space-y-2 mb-4">
                {plan.features.map((feature, index) => (
                  <div key={index} className="flex items-center space-x-2 text-sm">
                    <Check className="w-4 h-4" style={{ color: '#A294F9' }} />
                    <span className="text-gray-600">{feature}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="border-t pt-4" style={{ borderColor: '#E5D9F2' }}>
              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-600">Subtotal</span>
                <span className="font-semibold">${plan.price}.00</span>
              </div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-600">Tax</span>
                <span className="font-semibold">$0.00</span>
              </div>
              <div className="flex justify-between items-center text-xl font-bold mt-4">
                <span>Total</span>
                <span style={{ color: '#A294F9' }}>${plan.price}.00</span>
              </div>
            </div>

            <div className="mt-6 p-4 rounded-lg" style={{ backgroundColor: '#E5D9F2' }}>
              <div className="flex items-start space-x-3">
                <Lock className="w-5 h-5 mt-0.5" style={{ color: '#A294F9' }} />
                <div className="flex-1">
                  <p className="text-sm font-semibold text-gray-800">Secure Payment</p>
                  <p className="text-xs text-gray-600">Your payment information is encrypted and secure</p>
                </div>
              </div>
            </div>
          </div>

          {/* Payment Form */}
          <div className="bg-white rounded-2xl shadow-xl p-8 border" style={{ borderColor: '#E5D9F2' }}>
            <h2 className="text-2xl font-bold mb-6 text-gray-800">Payment Details</h2>

            {error && (
              <div className="mb-6 p-4 rounded-lg bg-red-50 border border-red-200">
                <p className="text-red-600 text-sm">{error}</p>
              </div>
            )}

            <form onSubmit={handleSubmit}>
              {/* Cardholder Name */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cardholder Name
                </label>
                <input
                  type="text"
                  value={cardholderName}
                  onChange={(e) => setCardholderName(e.target.value)}
                  placeholder="John Doe"
                  required
                  className="w-full px-4 py-3 rounded-lg border focus:outline-none focus:ring-2"
                  style={{ borderColor: '#E5D9F2', focusRing: '#A294F9' }}
                />
              </div>

              {/* Card Number */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Card Number
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={cardNumber}
                    onChange={handleCardNumberChange}
                    placeholder="1234 5678 9012 3456"
                    maxLength="19"
                    required
                    className="w-full px-4 py-3 rounded-lg border focus:outline-none focus:ring-2"
                    style={{ borderColor: '#E5D9F2' }}
                  />
                  <CreditCard className="absolute right-3 top-3 w-6 h-6 text-gray-400" />
                </div>
                <p className="mt-2 text-xs text-gray-500">
                  Test card: 4532 0151 1416 6952 or any valid Luhn card
                </p>
              </div>

              {/* Expiry and CVC */}
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Month
                  </label>
                  <input
                    type="text"
                    value={expMonth}
                    onChange={(e) => setExpMonth(e.target.value.replace(/\D/g, '').slice(0, 2))}
                    placeholder="MM"
                    maxLength="2"
                    required
                    className="w-full px-4 py-3 rounded-lg border focus:outline-none focus:ring-2"
                    style={{ borderColor: '#E5D9F2' }}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Year
                  </label>
                  <input
                    type="text"
                    value={expYear}
                    onChange={(e) => setExpYear(e.target.value.replace(/\D/g, '').slice(0, 2))}
                    placeholder="YY"
                    maxLength="2"
                    required
                    className="w-full px-4 py-3 rounded-lg border focus:outline-none focus:ring-2"
                    style={{ borderColor: '#E5D9F2' }}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    CVC
                  </label>
                  <input
                    type="text"
                    value={cvc}
                    onChange={(e) => setCvc(e.target.value.replace(/\D/g, '').slice(0, 4))}
                    placeholder="123"
                    maxLength="4"
                    required
                    className="w-full px-4 py-3 rounded-lg border focus:outline-none focus:ring-2"
                    style={{ borderColor: '#E5D9F2' }}
                  />
                </div>
              </div>

              {/* Billing Address Note */}
              <div className="mb-6 p-4 rounded-lg" style={{ backgroundColor: '#F5EFFF' }}>
                <p className="text-sm text-gray-600">
                  <strong>Note:</strong> This is a demonstration payment system. 
                  Use any valid card number (e.g., 4532015114166952) for testing.
                </p>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading || !sessionId}
                className="w-full py-4 rounded-lg text-white font-semibold text-lg transition-all duration-200 hover:scale-105 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                style={{ backgroundColor: '#A294F9' }}
              >
                {loading ? 'Processing...' : `Pay $${plan.price}.00`}
              </button>

              <p className="text-xs text-center text-gray-500 mt-4">
                By completing this purchase, you agree to our Terms of Service
              </p>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Checkout;
