import React from 'react';
import { useAuth } from '../contexts/AuthContext';

/**
 * FeatureGate component that conditionally renders content based on user's subscription tier
 * @param {Object} props
 * @param {string} props.requiredTier - Minimum tier required to access the feature ('free', 'researcher', 'professional')
 * @param {React.ReactNode} props.children - Content to render if user meets the tier requirement
 * @param {React.ReactNode} props.fallback - Optional content to render if user doesn't meet the requirement
 */
const FeatureGate = ({ requiredTier, children, fallback = null }) => {
  const { isAuthenticated, isAtLeast } = useAuth();

  // If user is not authenticated, show fallback
  if (!isAuthenticated) {
    return fallback;
  }

  // Check if user's tier meets the requirement
  return isAtLeast(requiredTier) ? children : fallback;
};

export default FeatureGate;
