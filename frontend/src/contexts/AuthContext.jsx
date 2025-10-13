import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

// API configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

console.log('API_BASE_URL:', API_BASE_URL); // Debug log

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [accessToken, setAccessToken] = useState(null);
  const [refreshToken, setRefreshToken] = useState(null);

  // API helper function
  const apiCall = async (endpoint, options = {}) => {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    // Add authorization header if access token exists
    if (accessToken && !config.headers.Authorization) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || `HTTP error! status: ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error('API call error:', error);
      throw error;
    }
  };

  // Check for existing login on app start
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const savedAccessToken = localStorage.getItem('access_token');
        const savedRefreshToken = localStorage.getItem('refresh_token');
        const savedUser = localStorage.getItem('user');

        if (savedAccessToken && savedUser) {
          setAccessToken(savedAccessToken);
          setRefreshToken(savedRefreshToken);
          
          try {
            const parsedUser = JSON.parse(savedUser);
            console.log('AuthContext - Loading user from localStorage:', parsedUser);
            console.log('AuthContext - is_admin value:', parsedUser.is_admin, 'type:', typeof parsedUser.is_admin);
            setUser(parsedUser);
            
            // Verify token is still valid
            await apiCall('/auth/verify-token', {
              headers: {
                Authorization: `Bearer ${savedAccessToken}`,
              },
            });
          } catch (error) {
            console.error('Token verification failed:', error);
            // Try to refresh token
            if (savedRefreshToken) {
              try {
                await refreshAccessToken(savedRefreshToken);
              } catch (refreshError) {
                console.error('Token refresh failed:', refreshError);
                clearAuthData();
              }
            } else {
              clearAuthData();
            }
          }
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
        clearAuthData();
      } finally {
        console.log('AuthContext - Finished initialization, setting isLoading to false');
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const clearAuthData = () => {
    // Clear state
    setUser(null);
    setAccessToken(null);
    setRefreshToken(null);
    
    // Clear all auth-related localStorage keys
    localStorage.removeItem('user');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('token'); // Legacy token key (used in some components)
    
    // Clear sessionStorage completely
    sessionStorage.clear();
    
    // Optional: Clear all localStorage for this app (uncomment if needed)
    // Note: This will clear ALL localStorage, including theme preferences, etc.
    // localStorage.clear();
  };

  const refreshAccessToken = async (refresh_token) => {
    try {
      const response = await apiCall('/auth/refresh', {
        method: 'POST',
        body: JSON.stringify({ refresh_token }),
      });

      setAccessToken(response.access_token);
      localStorage.setItem('access_token', response.access_token);
      
      return response.access_token;
    } catch (error) {
      console.error('Token refresh failed:', error);
      clearAuthData();
      throw error;
    }
  };

  const login = async (email, password) => {
    try {
      setIsLoading(true);
      
      const response = await apiCall('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });

      if (!response.access_token || !response.user) {
        throw new Error('Invalid response from server');
      }

      // Store tokens and user data
      setAccessToken(response.access_token);
      setRefreshToken(response.refresh_token);
      
      console.log('AuthContext - Login response user:', response.user);
      console.log('AuthContext - is_admin in response:', response.user.is_admin, 'type:', typeof response.user.is_admin);
      
      setUser(response.user);

      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      localStorage.setItem('user', JSON.stringify(response.user));

      setIsLoading(false);
      return response.user;
    } catch (error) {
      console.error('Login error:', error);
      setIsLoading(false);
      throw new Error(error.message || 'Login failed. Please try again.');
    }
  };

  const register = async (userData) => {
    try {
      setIsLoading(true);
      
      const response = await apiCall('/auth/register', {
        method: 'POST',
        body: JSON.stringify(userData),
      });

      return { success: true, user: response };
    } catch (error) {
      console.error('Registration error:', error);
      return { 
        success: false, 
        error: error.message || 'Registration failed. Please try again.' 
      };
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      // Call backend to blacklist token (if we have one)
      if (accessToken) {
        await apiCall('/auth/logout', {
          method: 'POST',
        });
      }
    } catch (error) {
      console.error('Logout API call failed:', error);
      // Continue with local logout even if API call fails
    } finally {
      // Always clear local data regardless of API call success
      clearAuthData();
      
      // Optional: Clear any other app-specific cache/data
      // You can add more cleanup here if needed
      console.log('User logged out - all data cleared from storage');
    }
  };

  const updateProfile = async (updateData) => {
    try {
      const response = await apiCall('/auth/me', {
        method: 'PUT',
        body: JSON.stringify(updateData),
      });

      setUser(response);
      localStorage.setItem('user', JSON.stringify(response));
      
      return { success: true, user: response };
    } catch (error) {
      console.error('Profile update error:', error);
      return { 
        success: false, 
        error: error.message || 'Profile update failed. Please try again.' 
      };
    }
  };

  const changePassword = async (passwordData) => {
    try {
      await apiCall('/auth/change-password', {
        method: 'POST',
        body: JSON.stringify(passwordData),
      });

      return { success: true };
    } catch (error) {
      console.error('Password change error:', error);
      return { 
        success: false, 
        error: error.message || 'Password change failed. Please try again.' 
      };
    }
  };

  const changeTier = async (newTier) => {
    try {
      const response = await apiCall('/auth/me/tier', {
        method: 'POST',
        body: JSON.stringify({ tier: newTier }),
      });

      setUser(response);
      localStorage.setItem('user', JSON.stringify(response));
      return { success: true, user: response };
    } catch (error) {
      console.error('Change tier error:', error);
      return {
        success: false,
        error: error.message || 'Failed to change plan. Please try again.'
      };
    }
  };

  const getTier = () => (user?.tier || 'free');
  const isAtLeast = (requiredTier) => {
    const order = ['free', 'researcher', 'professional'];
    return order.indexOf(getTier()) >= order.indexOf(requiredTier);
  };


  // Refresh user from backend and update context/localStorage
  const refreshUser = async () => {
    try {
      const response = await apiCall('/auth/me', {
        method: 'GET',
      });
      setUser(response);
      localStorage.setItem('user', JSON.stringify(response));
      return response;
    } catch (error) {
      console.error('Failed to refresh user:', error);
      clearAuthData();
      return null;
    }
  };

  const value = {
    user,
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    isLoading,
    isAuthenticated: !!user,
    accessToken,
    apiCall, // Expose apiCall for other components to use authenticated requests
    tier: getTier(),
    changeTier,
    isAtLeast,
    refreshUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};