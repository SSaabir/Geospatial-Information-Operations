import React from 'react';
import { useAuth } from '../contexts/AuthContext';

/**
 * FeatureGate
 * Props:
 *  - feature: string (optional) feature flag name
 *  - minTier: string (optional) one of 'free'|'researcher'|'professional'
 *  - isEnabled: boolean (optional) explicit override
 *  - featureFlags: object (optional) map of flags
 *  - user: object (optional) user override
 *  - fallback: ReactNode shown when disabled
 *  - children: ReactNode shown when enabled
 */
export default function FeatureGate({
  feature,
  minTier,
  isEnabled,
  featureFlags,
  user,
  fallback = null,
  children = null,
}) {
  const auth = useAuth();

  // Resolve user context: prefer explicit user prop, then auth.user
  const currentUser = user || auth.user || null;

  // 1) explicit boolean override
  if (typeof isEnabled === 'boolean') {
    return isEnabled ? <>{children}</> : <>{fallback}</>;
  }

  // 2) tier gating
  if (minTier) {
    try {
      const allowed = auth.isAtLeast(minTier);
      if (!allowed) return <>{fallback}</>;
    } catch (err) {
      // If auth isn't available for some reason, fall through to other checks
      console.warn('FeatureGate: isAtLeast check failed', err);
    }
  }

  // 3) feature flag maps (prop then window global)
  if (feature) {
    if (featureFlags && typeof featureFlags === 'object') {
      if (!featureFlags[feature]) return <>{fallback}</>;
    } else if (typeof window !== 'undefined' && window.__FEATURE_FLAGS__) {
      if (!window.__FEATURE_FLAGS__[feature]) return <>{fallback}</>;
    }
  }

  // 4) user-level features (array)
  if (currentUser && Array.isArray(currentUser.features)) {
    if (feature && !currentUser.features.includes(feature)) return <>{fallback}</>;
  }

  return <>{children}</>;
}

export function useFeatureEnabled(feature, options = {}) {
  const { featureFlags, user, isEnabled, minTier } = options;
  const auth = useAuth();

  if (typeof isEnabled === 'boolean') return isEnabled;
  if (minTier) {
    try {
      if (!auth.isAtLeast(minTier)) return false;
    } catch (err) {
      console.warn('useFeatureEnabled: isAtLeast check failed', err);
    }
  }

  if (featureFlags && typeof featureFlags === 'object') {
    return !!featureFlags[feature];
  }

  if (typeof window !== 'undefined' && window.__FEATURE_FLAGS__) {
    return !!window.__FEATURE_FLAGS__[feature];
  }

  const currentUser = user || auth.user || null;
  if (currentUser && Array.isArray(currentUser.features)) {
    return currentUser.features.includes(feature);
  }

  return true; // default to enabled unless gated above
}
