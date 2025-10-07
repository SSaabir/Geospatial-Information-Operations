import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export default function Checkout() {
  const { sessionId } = useParams();
  const navigate = useNavigate();
  const { apiCall } = useAuth();
  const [session, setSession] = useState(null);
  const [card, setCard] = useState({ card_number: '', exp_month: '', exp_year: '', cvc: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchSession = async () => {
      try {
        const resp = await apiCall(`/payments/session/${sessionId}`);
        setSession(resp);
      } catch (e) {
        console.error('Failed to fetch session', e);
        setError('Failed to load checkout session');
      }
    };
    fetchSession();
  }, [sessionId]);

  const handlePay = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const resp = await apiCall(`/payments/session/${sessionId}/pay`, {
        method: 'POST',
        body: JSON.stringify(card),
      });

      if (resp && resp.success) {
        // Payment recorded and user upgraded
        navigate('/dashboard');
      } else {
        setError('Payment failed');
      }
    } catch (e) {
      console.error('Payment error', e);
      setError(e.detail || e.message || 'Payment failed');
    } finally {
      setLoading(false);
    }
  };

  if (error) {
    return <div className="p-6">{error}</div>;
  }

  if (!session) return <div className="p-6">Loading session...</div>;

  return (
    <div className="min-h-screen flex items-center justify-center p-6">
      <div className="w-full max-w-md bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-xl font-bold mb-4">Checkout — {session.plan}</h2>
        <p className="mb-4">Amount: ${session.amount.toFixed(2)}</p>

        <form onSubmit={handlePay} className="space-y-4">
          <input
            value={card.card_number}
            onChange={(e) => setCard({ ...card, card_number: e.target.value })}
            placeholder="Card number (e.g. 4242424242424242)"
            className="w-full p-3 border rounded-lg"
            required
          />
          <div className="flex gap-2">
            <input
              value={card.exp_month}
              onChange={(e) => setCard({ ...card, exp_month: e.target.value })}
              placeholder="MM"
              className="w-1/3 p-3 border rounded-lg"
              required
            />
            <input
              value={card.exp_year}
              onChange={(e) => setCard({ ...card, exp_year: e.target.value })}
              placeholder="YY"
              className="w-1/3 p-3 border rounded-lg"
              required
            />
            <input
              value={card.cvc}
              onChange={(e) => setCard({ ...card, cvc: e.target.value })}
              placeholder="CVC"
              className="w-1/3 p-3 border rounded-lg"
              required
            />
          </div>

          <div className="flex items-center justify-between">
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg"
            >
              {loading ? 'Processing...' : 'Pay now'}
            </button>
            <button type="button" className="text-gray-600" onClick={() => navigate(-1)}>Cancel</button>
          </div>
        </form>
      </div>
    </div>
  );
}
