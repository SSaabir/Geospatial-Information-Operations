import React, { useState } from "react";

const ContactUs = () => {
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    organization: "",
    subject: "",
    message: "",
  });

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const validateForm = () => {
    let tempErrors = {};
    if (!formData.firstName) tempErrors.firstName = "Please enter your first name";
    if (!formData.lastName) tempErrors.lastName = "Please enter your last name";
    if (!formData.email) {
      tempErrors.email = "Please enter your email address";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      tempErrors.email = "Please enter a valid email address";
    }
    if (!formData.subject) tempErrors.subject = "Please select an inquiry type";
    if (!formData.message) tempErrors.message = "Please enter your message";

    setErrors(tempErrors);
    return Object.keys(tempErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setSuccess(true);
      setFormData({
        firstName: "",
        lastName: "",
        email: "",
        organization: "",
        subject: "",
        message: "",
      });
      setTimeout(() => setSuccess(false), 6000);
    }, 2500);
  };

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-[#F6F0FF] to-[#E3D9F3] text-gray-700">
      {/* Background pattern */}
      <div className="fixed inset-0 -z-10 opacity-5 bg-[radial-gradient(circle_at_25%_75%,#A896F5_0%,transparent_50%),radial-gradient(circle_at_75%_25%,#C8BBF6_0%,transparent_50%),radial-gradient(circle_at_50%_50%,#E3D9F3_0%,transparent_50%)] animate-[patternMove_20s_ease-in-out_infinite]" />

      <div className="max-w-6xl mx-auto p-5">
        <div className="grid md:grid-cols-2 gap-9 mb-9">
          {/* Contact Form */}
          <div className="relative bg-white rounded-3xl p-10 shadow-[0_15px_50px_rgba(168,150,245,0.15)] border-2 border-[#a896f51a] transition-all hover:-translate-y-1 hover:shadow-[0_25px_60px_rgba(168,150,245,0.2)]">
            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-[#A896F5] via-[#C8BBF6] to-[#E3D9F3]" />

            <h2 className="flex items-center gap-4 text-2xl font-bold mb-6 text-[#A896F5]">
              <div className="w-12 h-12 flex items-center justify-center rounded-xl shadow-md bg-gradient-to-br from-[#C8BBF6] to-[#A896F5] text-lg">
                📧
              </div>
              Get in Touch
            </h2>

            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Row 1 */}
              <div className="grid md:grid-cols-2 gap-5">
                <div className={`form-group ${errors.firstName ? "text-red-500" : ""}`}>
                  <label className="block font-semibold text-[#A896F5] mb-2">
                    First Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.firstName}
                    onChange={(e) => setFormData({ ...formData, firstName: e.target.value })}
                    placeholder="Your first name"
                    className="w-full p-4 rounded-lg border-2 border-[#a896f533] bg-gradient-to-br from-[#F6F0FF] to-[#e3d9f34d] focus:outline-none focus:ring-2 focus:ring-[#A896F5] focus:border-[#A896F5]"
                  />
                  {errors.firstName && <p className="text-sm mt-1">{errors.firstName}</p>}
                </div>

                <div>
                  <label className="block font-semibold text-[#A896F5] mb-2">
                    Last Name <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={formData.lastName}
                    onChange={(e) => setFormData({ ...formData, lastName: e.target.value })}
                    placeholder="Your last name"
                    className="w-full p-4 rounded-lg border-2 border-[#a896f533] bg-gradient-to-br from-[#F6F0FF] to-[#e3d9f34d] focus:outline-none focus:ring-2 focus:ring-[#A896F5] focus:border-[#A896F5]"
                  />
                  {errors.lastName && <p className="text-sm text-red-500 mt-1">{errors.lastName}</p>}
                </div>
              </div>

              {/* Email */}
              <div>
                <label className="block font-semibold text-[#A896F5] mb-2">
                  Email Address <span className="text-red-500">*</span>
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="your.email@university.edu"
                  className="w-full p-4 rounded-lg border-2 border-[#a896f533] bg-gradient-to-br from-[#F6F0FF] to-[#e3d9f34d] focus:outline-none focus:ring-2 focus:ring-[#A896F5] focus:border-[#A896F5]"
                />
                {errors.email && <p className="text-sm text-red-500 mt-1">{errors.email}</p>}
              </div>

              {/* Organization */}
              <div>
                <label className="block font-semibold text-[#A896F5] mb-2">Organization/Institution</label>
                <input
                  type="text"
                  value={formData.organization}
                  onChange={(e) => setFormData({ ...formData, organization: e.target.value })}
                  placeholder="University, Research Center, etc."
                  className="w-full p-4 rounded-lg border-2 border-[#a896f533] bg-gradient-to-br from-[#F6F0FF] to-[#e3d9f34d] focus:outline-none focus:ring-2 focus:ring-[#A896F5] focus:border-[#A896F5]"
                />
              </div>

              {/* Subject */}
              <div>
                <label className="block font-semibold text-[#A896F5] mb-2">
                  Inquiry Type <span className="text-red-500">*</span>
                </label>
                <select
                  value={formData.subject}
                  onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                  className="w-full p-4 rounded-lg border-2 border-[#a896f533] bg-gradient-to-br from-[#F6F0FF] to-[#e3d9f34d] focus:outline-none focus:ring-2 focus:ring-[#A896F5] focus:border-[#A896F5]"
                >
                  <option value="">Select inquiry type</option>
                  <option value="data-questions">Data Sources & Methodology</option>
                  <option value="technical-support">Technical Support</option>
                  <option value="research-collaboration">Research Collaboration</option>
                  <option value="api-access">API Access Request</option>
                  <option value="education-partnership">Educational Partnership</option>
                  <option value="bug-report">Bug Report</option>
                  <option value="feature-request">Feature Request</option>
                  <option value="general">General Question</option>
                </select>
                {errors.subject && <p className="text-sm text-red-500 mt-1">{errors.subject}</p>}
              </div>

              {/* Message */}
              <div>
                <label className="block font-semibold text-[#A896F5] mb-2">
                  Message <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={formData.message}
                  onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                  placeholder="Please describe your inquiry..."
                  className="w-full min-h-[130px] p-4 rounded-lg border-2 border-[#a896f533] bg-gradient-to-br from-[#F6F0FF] to-[#e3d9f34d] focus:outline-none focus:ring-2 focus:ring-[#A896F5] focus:border-[#A896F5]"
                />
                {errors.message && <p className="text-sm text-red-500 mt-1">{errors.message}</p>}
              </div>

              {/* Submit */}
              <button
                type="submit"
                disabled={loading}
                className="w-full py-4 rounded-xl font-semibold text-white bg-gradient-to-br from-[#A896F5] to-[#C8BBF6] shadow-md hover:-translate-y-1 hover:shadow-xl transition relative"
              >
                {loading ? "Sending Message..." : "Send Message"}
              </button>

              {success && (
                <div className="mt-4 p-4 rounded-xl text-white font-semibold text-center bg-gradient-to-br from-green-600 to-emerald-500 shadow-lg">
                  🌍 Thank you! Your message has been sent successfully. We'll respond within 48 hours.
                </div>
              )}
            </form>
          </div>

          {/* Contact Info */}
          <div className="relative rounded-3xl p-10 text-white shadow-[0_15px_50px_rgba(168,150,245,0.25)] bg-gradient-to-br from-[#A896F5] to-[#C8BBF6]">
            <h2 className="flex items-center gap-4 text-2xl font-bold mb-6">
              <div className="w-12 h-12 flex items-center justify-center rounded-xl bg-white/20">
                🌍
              </div>
              Climate Data Support
            </h2>

            {[
              { icon: "🔬", title: "Data & Methodology", email: "data@climateprediction.app", desc: "Questions about sources, validation, and scientific methods" },
              { icon: "🛠️", title: "Technical Support", email: "support@climateprediction.app", desc: "API issues, bugs, and technical assistance" },
              { icon: "🔒", title: "Privacy & Data", email: "privacy@climateprediction.app", desc: "Data handling, deletion requests, privacy concerns" },
              { icon: "🎓", title: "Research Partnerships", email: "research@climateprediction.app", desc: "Academic collaborations and institutional partnerships" },
            ].map((item, i) => (
              <div key={i} className="flex items-center gap-5 mb-7 p-5 bg-white/20 rounded-2xl backdrop-blur-sm hover:bg-white/30 transition">
                <div className="w-14 h-14 flex items-center justify-center rounded-xl bg-white/20 text-xl">{item.icon}</div>
                <div>
                  <h4 className="text-lg font-semibold">{item.title}</h4>
                  <p className="opacity-90 text-sm">
                    {item.email}
                    <br />
                    {item.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Climate Specialties */}
        <div className="bg-white rounded-3xl p-9 shadow-[0_15px_50px_rgba(168,150,245,0.12)] border-2 border-[#c8bbf633]">
          <h3 className="flex items-center gap-3 text-2xl font-bold mb-6 text-[#A896F5]">
            🌡️ Our Climate Data Expertise
          </h3>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { icon: "🌡️", title: "Temperature Analysis", desc: "Historical trends, anomaly detection, and future projections." },
              { icon: "🌧️", title: "Precipitation Patterns", desc: "Rainfall prediction, drought analysis, and forecasting." },
              { icon: "🌊", title: "Sea Level & Ocean Data", desc: "Coastal impacts, rise predictions, and ocean analysis." },
              { icon: "🌪️", title: "Extreme Weather", desc: "Hurricane tracking, severe storm prediction, risk assessment." },
              { icon: "📊", title: "Custom Climate Models", desc: "Tailored predictions for specific regions and research." },
              { icon: "🔬", title: "Research Support", desc: "Partnerships, validation, and methodology consultation." },
            ].map((item, i) => (
              <div
                key={i}
                className="relative p-6 rounded-xl bg-gradient-to-br from-[#F6F0FF] to-[#e3d9f380] border-l-4 border-[#C8BBF6] hover:-translate-y-1 hover:shadow-lg transition"
              >
                <strong className="block text-[#A896F5] mb-2">{item.title}</strong>
                <span className="text-sm">{item.desc}</span>
                <span className="absolute top-4 right-4 text-xl opacity-70">{item.icon}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContactUs;
