import React, { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";

export default function Settings() {
  const { user, updateProfile, changeTier, changePassword, logout, apiCall, isLoading: authLoading } = useAuth();
  
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
        ? "bg-purple-200 text-purple-800"
        : tier === "researcher"
        ? "bg-purple-400 text-white"
        : "bg-purple-700 text-white"
    }`;
  };

  const enterEditMode = () => {
    setEditMode(true);
    setOriginalData({ ...userData });
    setCurrentAvatar(userData.avatar);
  };

  const cancelEdit = () => {
    setEditMode(false);
    setCurrentAvatar(userData.avatar);
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
                        className="px-8 py-3 bg-[#E0DCEF] text-purple-800 rounded-lg font-semibold hover:bg-[#C7BCE6] disabled:opacity-50"
                        disabled={isLoading}
                      >
                        ✖️ Cancel
                      </button>
                    </div>
                  </form>
                </div>

                {/* Tier Management Section */}
                <div className="border-t border-gray-300 pt-10">
                  <h3 className="text-xl font-semibold mb-6 flex items-center gap-2">🎯 Subscription Management</h3>

                  <div className="mb-6">
                    <label className="block text-gray-700 font-semibold mb-2">Select Your Tier</label>
                    <select
                      value={userData.tier}
                      onChange={handleTierChange}
                      className="w-full p-4 border-2 border-[#E0DCEF] rounded-lg bg-[#F0F0F7] focus:outline-none focus:border-[#9481E3] focus:bg-white disabled:opacity-50"
                      disabled={isLoading}
                    >
                      <option value="free">Free - Basic features for getting started</option>
                      <option value="researcher">Researcher - Advanced tools for research</option>
                      <option value="professional">Professional - Full access with premium support</option>
                    </select>
                    <div className="text-gray-500 text-sm italic mt-2">
                      {isLoading ? "Updating tier..." : "Choose the tier that best fits your needs"}
                    </div>
                  </div>
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
                          className="px-8 py-3 bg-[#E0DCEF] text-purple-800 rounded-lg font-semibold hover:bg-[#C7BCE6] disabled:opacity-50"
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
