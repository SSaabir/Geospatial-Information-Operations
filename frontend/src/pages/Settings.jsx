import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export default function Settings() {
  const { user, updateProfile, changeTier, changePassword, logout, apiCall, refreshUser, isLoading: authLoading } = useAuth();
  const navigate = useNavigate();
  
  // =======================
  // USER DATA
  // =======================
  const [userData, setUserData] = useState({
    name: "",
    email: "",
    username: "",
    tier: "",
    lastLogin: "",
    avatar: null,
  });

  const [originalData, setOriginalData] = useState({});
  const [currentAvatar, setCurrentAvatar] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [toast, setToast] = useState({ message: "", type: "" });
  const [isLoading, setIsLoading] = useState(false);
  
  // Password change state
  const [passwordData, setPasswordData] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });
  const [showPasswordSection, setShowPasswordSection] = useState(false);

  // =======================
  // FETCH PROFILE FROM BACKEND
  // =======================
  useEffect(() => {
    if (user) {
      setUserData({
        name: user.full_name || "",
        email: user.email || "",
        username: user.username || "",
        tier: user.tier || "free",
        lastLogin: user.last_login || "",
        avatar: user.avatar_url || null,
      });

      setOriginalData({
        name: user.full_name || "",
        email: user.email || "",
        username: user.username || "",
        avatar: user.avatar_url || null,
      });
      setCurrentAvatar(user.avatar_url || null);
    }
  }, [user]);

  // =======================
  // HELPERS
  // =======================
  const getInitials = (name) =>
    name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .substring(0, 2);

  const updateTierBadge = (tier) => {
    return `inline-block px-4 py-1 rounded-full text-sm font-semibold uppercase ${
      tier === "free"
        ? "bg-orange-200 text-orange-800"
        : tier === "researcher"
        ? "bg-orange-400 text-white"
        : "bg-orange-700 text-white"
    }`;
  };

  const enterEditMode = () => {
    setEditMode(true);
    setOriginalData({ ...userData });
    setCurrentAvatar(userData.avatar);
  };

  const cancelEdit = () => {
    setEditMode(false);
    setUserData(originalData);
    setCurrentAvatar(originalData.avatar);
  };

  const handleProfileChange = (e) => {
    const { id, value } = e.target;
    setUserData((prev) => ({
      ...prev,
      [id === "nameInput" ? "name" : id === "emailInput" ? "email" : "username"]:
        value,
    }));
  };

  const handleAvatarUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (file.size > 5 * 1024 * 1024) {
      showToast("Image must be less than 5MB", "error");
      return;
    }
    const reader = new FileReader();
    reader.onload = (ev) => {
      setCurrentAvatar(ev.target.result);
    };
    reader.readAsDataURL(file);
  };

  // =======================
  // SAVE PROFILE TO BACKEND
  // =======================
  const handleProfileSave = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const result = await updateProfile({
        full_name: userData.name,
        email: userData.email,
        username: userData.username,
        avatar_url: currentAvatar,
      });

      if (result.success) {
        setUserData({
          ...userData,
          name: result.user.full_name,
          email: result.user.email,
          username: result.user.username || "",
          avatar: result.user.avatar_url || null,
          tier: result.user.tier,
        });

        setOriginalData({
          name: result.user.full_name,
          email: result.user.email,
          username: result.user.username || "",
          avatar: result.user.avatar_url || null,
        });

        setEditMode(false);
        showToast("Profile updated successfully! ✅", "success");
      } else {
        showToast(result.error, "error");
      }
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setIsLoading(false);
    }
  };

  // =======================
  // CHANGE TIER ON BACKEND
  // =======================
  const handleTierChange = async (e) => {
    const newTier = e.target.value;
    setIsLoading(true);
    try {
      const result = await changeTier(newTier);
      
      if (result.success) {
        setUserData((prev) => ({ ...prev, tier: result.user.tier }));
        
        // Refresh user data from backend to update context and localStorage
        await refreshUser();
        
        showToast(`Tier updated to ${result.user.tier.toUpperCase()}! 🚀`, "success");
      } else {
        showToast(result.error, "error");
      }
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setIsLoading(false);
    }
  };

  // =======================
  // CHANGE PASSWORD
  // =======================
  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      showToast("New passwords don't match!", "error");
      return;
    }
    
    if (passwordData.newPassword.length < 6) {
      showToast("New password must be at least 6 characters long!", "error");
      return;
    }
    
    setIsLoading(true);
    try {
      const result = await changePassword({
        current_password: passwordData.currentPassword,
        new_password: passwordData.newPassword,
      });
      
      if (result.success) {
        showToast("Password changed successfully! 🔒", "success");
        setPasswordData({
          currentPassword: "",
          newPassword: "",
          confirmPassword: "",
        });
        setShowPasswordSection(false);
      } else {
        showToast(result.error, "error");
      }
    } catch (err) {
      showToast(err.message, "error");
    } finally {
      setIsLoading(false);
    }
  };

  // =======================
  // TOAST
  // =======================
  const showToast = (message, type = "success") => {
    setToast({ message, type });
    setTimeout(() => setToast({ message: "", type: "" }), 3000);
  };

  // =======================
  // CHECK IF FORM CHANGED
  // =======================
  const hasChanges =
    userData.name !== originalData.name ||
    userData.email !== originalData.email ||
    userData.username !== originalData.username ||
    currentAvatar !== originalData.avatar;

  // Show loading state if auth is still loading
  if (authLoading) {
    return (
      <div className="min-h-screen p-10 bg-gradient-to-br from-[#F0F0F7] via-[#E0DCEF] to-[#9481E3] flex items-center justify-center">
        <div className="text-center text-white">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
          <p className="text-xl">Loading settings...</p>
        </div>
      </div>
    );
  }

  // Show message if no user data
  if (!user) {
    return (
      <div className="min-h-screen p-10 bg-gradient-to-br from-[#F0F0F7] via-[#E0DCEF] to-[#9481E3] flex items-center justify-center">
        <div className="text-center text-white">
          <h1 className="text-4xl font-semibold drop-shadow mb-4">⚙️ Settings</h1>
          <p className="text-xl">Please log in to access your settings.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-10 bg-gradient-to-br from-[#F0F0F7] via-[#E0DCEF] to-[#9481E3]">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-10 text-white">
          <h1 className="text-4xl font-semibold drop-shadow">⚙️ Settings</h1>
        </div>

        <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
          <div className="bg-gradient-to-br from-[#9481E3] to-[#C7BCE6] p-8 text-white">
            <h2 className="text-2xl font-medium">
              {editMode ? "Edit Profile" : "Profile Overview"}
            </h2>
          </div>

          <div className="p-10">
            {/* View Mode */}
            {!editMode && (
              <div>
                <div className="text-center mb-8 relative">
                  <div className="w-30 h-30 rounded-full bg-gradient-to-br from-[#C7BCE6] to-[#9481E3] flex items-center justify-center text-3xl font-bold text-white shadow-md mx-auto overflow-hidden">
                    {userData.avatar ? (
                      <img src={userData.avatar} alt="Avatar" className="w-full h-full object-cover" />
                    ) : (
                      <span>{getInitials(userData.name)}</span>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                  <div className="p-5 bg-[#F0F0F7] rounded-lg hover:bg-[#E0DCEF] transition-all">
                    <div className="text-xs font-semibold text-gray-500 uppercase mb-2">Full Name</div>
                    <div className="text-lg font-medium text-gray-800">{userData.name}</div>
                  </div>
                  <div className="p-5 bg-[#F0F0F7] rounded-lg hover:bg-[#E0DCEF] transition-all">
                    <div className="text-xs font-semibold text-gray-500 uppercase mb-2">Email</div>
                    <div className="text-lg font-medium text-gray-800">{userData.email}</div>
                  </div>
                  <div className="p-5 bg-[#F0F0F7] rounded-lg hover:bg-[#E0DCEF] transition-all">
                    <div className="text-xs font-semibold text-gray-500 uppercase mb-2">Username</div>
                    <div className="text-lg font-medium text-gray-800">{userData.username}</div>
                  </div>
                  <div className="p-5 bg-[#F0F0F7] rounded-lg hover:bg-[#E0DCEF] transition-all">
                    <div className="text-xs font-semibold text-gray-500 uppercase mb-2">Current Tier</div>
                    <div className="text-lg font-medium">
                      <span className={updateTierBadge(userData.tier)}>{userData.tier}</span>
                    </div>
                  </div>
                  <div className="p-5 bg-[#F0F0F7] rounded-lg hover:bg-[#E0DCEF] transition-all">
                    <div className="text-xs font-semibold text-gray-500 uppercase mb-2">Last Login</div>
                    <div className="text-lg font-medium text-gray-800">{userData.lastLogin}</div>
                  </div>
                </div>

                <div className="flex gap-4 flex-wrap">
                  <button
                    onClick={enterEditMode}
                    className="px-8 py-3 bg-gradient-to-br from-[#9481E3] to-[#C7BCE6] text-white rounded-lg font-semibold hover:shadow-lg transition-all"
                  >
                    ✏️ Edit Profile
                  </button>
                  <button
                    onClick={logout}
                    className="px-8 py-3 bg-red-500 text-white rounded-lg font-semibold hover:bg-red-600 transition-all"
                  >
                    🚪 Logout
                  </button>
                </div>
              </div>
            )}

            {/* Edit Mode */}
            {editMode && (
              <div>
                {/* Edit Profile Section */}
                <div className="mb-10">
                  <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">📝 Edit Profile Information</h3>

                  {/* Avatar Upload */}
                  <div className="text-center mb-6 relative">
                    <div className="relative inline-block">
                      <div className="w-30 h-30 rounded-full bg-gradient-to-br from-[#C7BCE6] to-[#9481E3] flex items-center justify-center text-3xl font-bold text-white shadow-md mx-auto overflow-hidden">
                        {currentAvatar ? (
                          <img src={currentAvatar} alt="Avatar" className="w-full h-full object-cover" />
                        ) : (
                          <span>{getInitials(userData.name)}</span>
                        )}
                      </div>
                      <label
                        htmlFor="avatarInput"
                        className="absolute bottom-0 right-0 w-10 h-10 bg-[#9481E3] border-2 border-white text-white text-center rounded-full flex items-center justify-center cursor-pointer hover:bg-[#7d6bc9] transition-transform"
                      >
                        📷
                      </label>
                      <input
                        type="file"
                        id="avatarInput"
                        className="hidden"
                        onChange={handleAvatarUpload}
                        accept="image/*"
                      />
                    </div>
                  </div>

                  <form onSubmit={handleProfileSave}>
                    <div className="mb-6">
                      <label className="block text-gray-700 font-semibold mb-2">Full Name *</label>
                      <input
                        type="text"
                        id="nameInput"
                        value={userData.name}
                        onChange={handleProfileChange}
                        className="w-full p-4 border-2 border-[#E0DCEF] rounded-lg bg-[#F0F0F7] focus:outline-none focus:border-[#9481E3] focus:bg-white"
                        required
                      />
                    </div>

                    <div className="mb-6">
                      <label className="block text-gray-700 font-semibold mb-2">Email Address *</label>
                      <input
                        type="email"
                        id="emailInput"
                        value={userData.email}
                        onChange={handleProfileChange}
                        className="w-full p-4 border-2 border-[#E0DCEF] rounded-lg bg-[#F0F0F7] focus:outline-none focus:border-[#9481E3] focus:bg-white"
                        required
                      />
                    </div>

                    <div className="mb-6">
                      <label className="block text-gray-700 font-semibold mb-2">Username</label>
                      <input
                        type="text"
                        id="usernameInput"
                        value={userData.username}
                        onChange={handleProfileChange}
                        className="w-full p-4 border-2 border-[#E0DCEF] rounded-lg bg-[#F0F0F7] focus:outline-none focus:border-[#9481E3] focus:bg-white"
                      />
                    </div>

                    <div className="flex gap-4 flex-wrap">
                      <button
                        type="submit"
                        className={`px-8 py-3 bg-gradient-to-br from-[#9481E3] to-[#C7BCE6] text-white rounded-lg font-semibold hover:shadow-lg transition-all ${
                          (!hasChanges || isLoading) && "opacity-50 cursor-not-allowed"
                        }`}
                        disabled={!hasChanges || isLoading}
                      >
                        {isLoading ? (
                          <>
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                            Saving...
                          </>
                        ) : (
                          "💾 Save Changes"
                        )}
                      </button>
                      <button
                        type="button"
                        onClick={cancelEdit}
                        className="px-8 py-3 bg-[#E0DCEF] text-orange-800 rounded-lg font-semibold hover:bg-[#C7BCE6] disabled:opacity-50"
                        disabled={isLoading}
                      >
                        ✖️ Cancel
                      </button>
                    </div>
                  </form>
                </div>

                {/* Subscription Management Section */}
                <div className="border-t border-gray-300 pt-10">
                  <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">🎯 Subscription Management</h3>

                  <div className="mb-6 p-6 bg-[#F0F0F7] rounded-lg">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-sm font-semibold text-gray-500 uppercase mb-2">Current Plan</div>
                        <div className="text-2xl font-bold">
                          <span className={updateTierBadge(userData.tier)}>{userData.tier.toUpperCase()}</span>
                        </div>
                        <p className="text-gray-600 mt-2">
                          {userData.tier === 'free' && 'Basic features for getting started'}
                          {userData.tier === 'researcher' && 'Advanced tools for research'}
                          {userData.tier === 'professional' && 'Full access with premium support'}
                        </p>
                      </div>
                      <div>
                        <button
                          onClick={() => navigate('/pricing')}
                          className="px-6 py-3 bg-gradient-to-br from-[#9481E3] to-[#C7BCE6] text-white rounded-lg font-semibold hover:shadow-lg transition-all"
                        >
                          {userData.tier === 'free' ? '⬆️ Upgrade Plan' : '🔄 Change Plan'}
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Subscription Cancellation Section */}
                  {userData.tier !== 'free' && (
                    <div className="mb-6">
                      <h4 className="text-lg font-semibold mb-3 flex items-center gap-2 text-red-600">
                        ❌ Cancel Subscription
                      </h4>
                      <div className="bg-red-50 border-2 border-red-200 rounded-lg p-6">
                        <p className="text-gray-700 mb-4">
                          You are currently on the <strong className={updateTierBadge(userData.tier)}>{userData.tier.toUpperCase()}</strong> plan. 
                          Cancelling your subscription will downgrade your account to the <strong>Free</strong> tier. 
                          You'll lose access to premium features including:
                        </p>
                        <ul className="list-disc list-inside text-gray-600 mb-4 space-y-1">
                          <li>Extended historical data access ({userData.tier === 'researcher' ? '1 year' : 'unlimited'})</li>
                          <li>Higher API rate limits</li>
                          <li>Advanced analytics and reports</li>
                          <li>Priority support</li>
                        </ul>
                        <button
                          onClick={async () => {
                            if (window.confirm('Are you sure you want to cancel your subscription? This action will downgrade you to the free tier immediately.')) {
                              setIsLoading(true);
                              try {
                                console.log('Attempting to cancel subscription...');
                                
                                // Use the billing API endpoint for cancellation
                                const response = await apiCall('/billing/cancel-subscription', {
                                  method: 'POST',
                                  headers: {
                                    'Content-Type': 'application/json'
                                  }
                                });
                                
                                console.log('Cancel subscription response:', response);
                                
                                if (response && (response.success || response.message)) {
                                  // Update local user data
                                  setUserData(prev => ({ ...prev, tier: 'free' }));
                                  
                                  // Refresh user data from backend to update context
                                  await refreshUser();
                                  
                                  showToast(response.message || 'Subscription cancelled successfully. You are now on the Free tier.', 'success');
                                  
                                  // Optional: Reload to ensure all components reflect the change
                                  setTimeout(() => {
                                    window.location.reload();
                                  }, 1500);
                                } else {
                                  showToast(response?.detail || response?.error || 'Failed to cancel subscription', 'error');
                                }
                              } catch (error) {
                                console.error('Cancel subscription error:', error);
                                const errorMessage = error.response?.data?.detail || error.message || 'Unknown error occurred';
                                showToast('Failed to cancel subscription: ' + errorMessage, 'error');
                              } finally {
                                setIsLoading(false);
                              }
                            }
                          }}
                          disabled={isLoading}
                          className="px-8 py-3 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {isLoading ? '⏳ Cancelling...' : '🚫 Cancel My Subscription'}
                        </button>
                      </div>
                    </div>
                  )}
                </div>

                {/* Password Change Section */}
                <div className="border-t border-gray-300 pt-10">
                  <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">🔒 Security Settings</h3>
                  
                  {!showPasswordSection ? (
                    <div className="text-center">
                      <button
                        onClick={() => setShowPasswordSection(true)}
                        className="px-8 py-3 bg-gradient-to-br from-[#9481E3] to-[#C7BCE6] text-white rounded-lg font-semibold hover:shadow-lg transition-all"
                      >
                        🔑 Change Password
                      </button>
                    </div>
                  ) : (
                    <form onSubmit={handlePasswordSubmit} className="space-y-6">
                      <div>
                        <label className="block text-gray-700 font-semibold mb-2">Current Password *</label>
                        <input
                          type="password"
                          name="currentPassword"
                          value={passwordData.currentPassword}
                          onChange={handlePasswordChange}
                          className="w-full p-4 border-2 border-[#E0DCEF] rounded-lg bg-[#F0F0F7] focus:outline-none focus:border-[#9481E3] focus:bg-white"
                          required
                        />
                      </div>

                      <div>
                        <label className="block text-gray-700 font-semibold mb-2">New Password *</label>
                        <input
                          type="password"
                          name="newPassword"
                          value={passwordData.newPassword}
                          onChange={handlePasswordChange}
                          className="w-full p-4 border-2 border-[#E0DCEF] rounded-lg bg-[#F0F0F7] focus:outline-none focus:border-[#9481E3] focus:bg-white"
                          required
                          minLength={6}
                        />
                        <div className="text-gray-500 text-sm italic mt-1">
                          Password must be at least 6 characters long
                        </div>
                      </div>

                      <div>
                        <label className="block text-gray-700 font-semibold mb-2">Confirm New Password *</label>
                        <input
                          type="password"
                          name="confirmPassword"
                          value={passwordData.confirmPassword}
                          onChange={handlePasswordChange}
                          className="w-full p-4 border-2 border-[#E0DCEF] rounded-lg bg-[#F0F0F7] focus:outline-none focus:border-[#9481E3] focus:bg-white"
                          required
                        />
                      </div>

                      <div className="flex gap-4 flex-wrap">
                        <button
                          type="submit"
                          className={`px-8 py-3 bg-gradient-to-br from-[#9481E3] to-[#C7BCE6] text-white rounded-lg font-semibold hover:shadow-lg transition-all ${
                            isLoading && "opacity-50 cursor-not-allowed"
                          }`}
                          disabled={isLoading}
                        >
                          {isLoading ? (
                            <>
                              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                              Updating...
                            </>
                          ) : (
                            "🔒 Update Password"
                          )}
                        </button>
                        <button
                          type="button"
                          onClick={() => {
                            setShowPasswordSection(false);
                            setPasswordData({
                              currentPassword: "",
                              newPassword: "",
                              confirmPassword: "",
                            });
                          }}
                          className="px-8 py-3 bg-[#E0DCEF] text-orange-800 rounded-lg font-semibold hover:bg-[#C7BCE6] disabled:opacity-50"
                          disabled={isLoading}
                        >
                          ✖️ Cancel
                        </button>
                      </div>
                    </form>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Toast Notification */}
      {toast.message && (
        <div
          className={`fixed bottom-10 right-10 px-6 py-4 rounded-lg text-white font-semibold shadow-lg transition-all ${
            toast.type === "success" ? "bg-green-500" : "bg-red-500"
          }`}
        >
          {toast.message}
        </div>
      )}
    </div>
  );
}
