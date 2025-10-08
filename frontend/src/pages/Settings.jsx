import React, { useState, useEffect } from "react";

const API_BASE_URL = "http://localhost:8000"; // ← change if needed

export default function Settings() {
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

  // =======================
  // AUTH TOKEN
  // =======================
  const token = localStorage.getItem("token"); // adjust to your auth storage

  // =======================
  // FETCH PROFILE FROM BACKEND
  // =======================
  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/auth/me`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (!res.ok) throw new Error("Failed to fetch profile");
        const data = await res.json();

        setUserData({
          name: data.full_name,
          email: data.email,
          username: data.username || "",
          tier: data.tier,
          lastLogin: data.last_login || "",
          avatar: data.avatar_url || null,
        });

        setOriginalData({
          name: data.full_name,
          email: data.email,
          username: data.username || "",
          avatar: data.avatar_url || null,
        });
        setCurrentAvatar(data.avatar_url || null);
      } catch (err) {
        showToast(err.message, "error");
      }
    };

    fetchProfile();
  }, [token]);

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
    try {
      const res = await fetch(`${API_BASE_URL}/auth/me`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          full_name: userData.name,
          email: userData.email,
          username: userData.username,
          avatar_url: currentAvatar,
          tier: userData.tier,
        }),
      });

      if (!res.ok) throw new Error("Failed to update profile");
      const updated = await res.json();

      setUserData({
        ...userData,
        name: updated.full_name,
        email: updated.email,
        username: updated.username || "",
        avatar: updated.avatar_url || null,
        tier: updated.tier,
      });

      setOriginalData({
        name: updated.full_name,
        email: updated.email,
        username: updated.username || "",
        avatar: updated.avatar_url || null,
      });

      setEditMode(false);
      showToast("Profile updated successfully! ✅", "success");
    } catch (err) {
      showToast(err.message, "error");
    }
  };

  // =======================
  // CHANGE TIER ON BACKEND
  // =======================
  const handleTierChange = async (e) => {
    const newTier = e.target.value;
    try {
      const res = await fetch(`${API_BASE_URL}/auth/me`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          tier: newTier,
        }),
      });

      if (!res.ok) throw new Error("Failed to update tier");
      const updated = await res.json();

      setUserData((prev) => ({ ...prev, tier: updated.tier }));
      showToast(`Tier updated to ${updated.tier.toUpperCase()}! 🚀`, "success");
    } catch (err) {
      showToast(err.message, "error");
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

                <div className="flex gap-4">
                  <button
                    onClick={enterEditMode}
                    className="px-8 py-3 bg-gradient-to-br from-[#9481E3] to-[#C7BCE6] text-white rounded-lg font-semibold hover:shadow-lg transition-all"
                  >
                    ✏️ Edit Profile
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
                          !hasChanges && "opacity-50 cursor-not-allowed"
                        }`}
                        disabled={!hasChanges}
                      >
                        💾 Save Changes
                      </button>
                      <button
                        type="button"
                        onClick={cancelEdit}
                        className="px-8 py-3 bg-[#E0DCEF] text-purple-800 rounded-lg font-semibold hover:bg-[#C7BCE6]"
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
                      className="w-full p-4 border-2 border-[#E0DCEF] rounded-lg bg-[#F0F0F7] focus:outline-none focus:border-[#9481E3] focus:bg-white"
                    >
                      <option value="free">Free - Basic features for getting started</option>
                      <option value="researcher">Researcher - Advanced tools for research</option>
                      <option value="professional">Professional - Full access with premium support</option>
                    </select>
                    <div className="text-gray-500 text-sm italic mt-2">
                      Choose the tier that best fits your needs
                    </div>
                  </div>
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
