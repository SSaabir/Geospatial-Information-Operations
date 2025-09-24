import { useEffect, useState } from "react";

export default function TermsAndConditions() {
  const [scrollProgress, setScrollProgress] = useState(0);
  const [accepting, setAccepting] = useState(false);
  const [accepted, setAccepted] = useState(false);

  // Scroll progress bar
  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = document.documentElement.scrollTop;
      const scrollHeight =
        document.documentElement.scrollHeight - window.innerHeight;
      const progress = (scrollTop / scrollHeight) * 100;
      setScrollProgress(progress);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Scroll to top + bounce sections
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  // Accept terms
  const acceptTerms = () => {
    setAccepting(true);
    setTimeout(() => {
      setAccepting(false);
      setAccepted(true);
      setTimeout(() => {
        window.location.href = "/climate-dashboard"; // change route
      }, 1500);
    }, 500);
  };

  return (
    <div className="relative min-h-screen font-sans bg-gradient-to-br from-[#F6F0FF] to-[#E3D9F3] text-gray-700">
      {/* Background pattern */}
      <div className="fixed inset-0 opacity-5 pointer-events-none z-[-1] bg-[radial-gradient(circle_at_20%_80%,#A896F5_0%,transparent_50%),radial-gradient(circle_at_80%_20%,#C8BBF6_0%,transparent_50%),radial-gradient(circle_at_40%_40%,#E3D9F3_0%,transparent_50%)]"></div>

      {/* Scroll progress */}
      <div className="fixed top-0 left-0 w-full h-1 bg-purple-200 z-50">
        <div
          className="h-full bg-gradient-to-r from-[#A896F5] to-[#C8BBF6] transition-all duration-150"
          style={{ width: `${scrollProgress}%` }}
        ></div>
      </div>

      <div className="max-w-5xl mx-auto p-6">
        {/* Banner */}
        <div className="relative mb-8 text-center text-white font-semibold text-lg rounded-2xl shadow-xl overflow-hidden bg-gradient-to-br from-[#A896F5] to-[#C8BBF6] p-6">
          <span className="inline-block animate-spin mr-3">🌍</span>
          This application provides climate data analysis and predictive
          insights for educational and research purposes. All predictions are
          based on scientific models and historical data.
        </div>

        {/* Sections */}
        <Section icon="📚" title="Introduction">
          <ul className="terms-list space-y-4">
            <ListItem>
              The <strong>Climate Data Explorer</strong> is a web-based
              application that provides climate data analysis, visualization,
              and predictive modeling using machine learning algorithms.
            </ListItem>
            <ListItem>
              This application is designed for{" "}
              <strong>
                educational institutions, researchers, students, and climate
                enthusiasts
              </strong>{" "}
              to explore historical climate patterns and future projections.
            </ListItem>
            <ListItem>
              By using this application, you acknowledge that climate
              predictions are{" "}
              <strong>
                scientific estimates based on available data
              </strong>{" "}
              and should be interpreted accordingly.
            </ListItem>
          </ul>
        </Section>

        <Section icon="📋" title="Acceptable Use">
          <ul className="space-y-4">
            <ListItem>
              This application is free to use for{" "}
              <strong>educational, research, and non-commercial purposes</strong>
              .
            </ListItem>
            <ListItem>
              Users must provide{" "}
              <strong>accurate location and time parameters</strong> for
              meaningful climate analysis.
            </ListItem>
            <ListItem>
              When publishing research using this application, please{" "}
              <strong>cite the application and underlying datasets</strong>{" "}
              appropriately.
            </ListItem>
            <ListItem>
              Do not attempt to{" "}
              <strong>reverse engineer, copy, or redistribute</strong> the
              application's code or algorithms.
            </ListItem>
          </ul>
        </Section>

        {/* Example: you would repeat Section for Data Sources, Limitations, etc. */}

        {/* Buttons */}
        <div className="flex flex-wrap justify-center gap-6 mt-12">
          <button
            onClick={scrollToTop}
            className="px-8 py-4 rounded-xl border-2 border-[#A896F5] text-[#A896F5] font-semibold text-lg flex items-center gap-2 hover:bg-[#A896F5] hover:text-white transition-all"
          >
            📖 Review Again
          </button>
          <button
            onClick={acceptTerms}
            className={`px-8 py-4 rounded-xl text-white font-semibold text-lg flex items-center gap-2 transition-all shadow-lg ${
              accepted
                ? "bg-gradient-to-r from-green-600 to-emerald-400"
                : "bg-gradient-to-br from-[#A896F5] to-[#C8BBF6]"
            }`}
          >
            {accepting
              ? "🔄 Processing..."
              : accepted
              ? "✅ Terms Accepted - Redirecting..."
              : "🌍 Accept & Explore Climate Data"}
          </button>
        </div>
      </div>
    </div>
  );
}

// Section wrapper
function Section({ icon, title, children }) {
  return (
    <div className="relative bg-white rounded-3xl p-10 mb-6 shadow-xl border-2 border-[#A896F533] hover:-translate-y-1 hover:shadow-2xl transition-all">
      <h2 className="flex items-center gap-4 text-[#A896F5] text-2xl font-bold mb-6">
        <div className="w-12 h-12 flex items-center justify-center rounded-xl text-xl shadow-md bg-gradient-to-br from-[#C8BBF6] to-[#A896F5]">
          {icon}
        </div>
        {title}
      </h2>
      <div className="text-gray-700">{children}</div>
    </div>
  );
}

// List item wrapper
function ListItem({ children }) {
  return (
    <li className="relative bg-gradient-to-br from-[#F6F0FF] to-[#E3D9F3] border-l-4 border-[#A896F5] rounded-xl p-5 shadow-md hover:translate-x-2 hover:shadow-xl hover:from-[#E3D9F3] hover:to-[#C8BBF6] transition-all">
      {children}
    </li>
  );
}
