import React, { useEffect } from "react";
import "./Terms.css";

const Terms = () => {

  // Scroll progress indicator
  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = document.documentElement.scrollTop;
      const scrollHeight =
        document.documentElement.scrollHeight - window.innerHeight;
      const scrollProgress = (scrollTop / scrollHeight) * 100;
      document.getElementById("scrollProgress").style.width =
        scrollProgress + "%";
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });

    // Highlight sections for review
    document.querySelectorAll(".terms-section").forEach((section, index) => {
      setTimeout(() => {
        section.style.transform = "scale(1.02)";
        section.style.boxShadow = "0 20px 60px rgba(200, 187, 246, 0.25)";
        setTimeout(() => {
          section.style.transform = "scale(1)";
          section.style.boxShadow =
            "0 12px 48px rgba(168, 150, 245, 0.12)";
        }, 300);
      }, index * 150);
    });

    // Reset accept button
    const acceptBtn = document.querySelector(".btn-primary");
    if (acceptBtn.innerHTML.includes("✓")) {
      acceptBtn.innerHTML = "🌍 Accept & Explore Climate Data";
      acceptBtn.style.background =
        "linear-gradient(135deg, #A896F5, #C8BBF6)";
    }
  };

  const acceptTerms = (e) => {
    const button = e.target;
    button.style.transform = "scale(0.95)";
    button.innerHTML = "🔄 Processing...";

    setTimeout(() => {
      button.style.transform = "scale(1)";
      button.innerHTML = "✅ Terms Accepted - Redirecting...";
      button.style.background =
        "linear-gradient(135deg, #28a745, #20c997)";

      setTimeout(() => {
        window.location.href = "climate-dashboard.html"; // Change as needed
      }, 1500);
    }, 500);
  };

  // Entrance animations
  useEffect(() => {
    document.querySelectorAll(".terms-section").forEach((section, index) => {
      section.style.opacity = "0";
      section.style.transform = "translateY(30px)";
      setTimeout(() => {
        section.style.transition = "all 0.6s ease";
        section.style.opacity = "1";
        section.style.transform = "translateY(0)";
      }, index * 100);
    });
  }, []);

  return (
    <div>
      <div className="climate-pattern"></div>
      <div className="scroll-indicator">
        <div className="scroll-progress" id="scrollProgress"></div>
      </div>

      <div className="container">
        <div className="climate-banner">
          This application provides climate data analysis and predictive
          insights for educational and research purposes. All predictions are
          based on scientific models and historical data.
        </div>

        {/* Copy all sections from your HTML into here as JSX (unchanged except self-closing tags & className fixes). */}
      </div>

      <div className="action-buttons">
        <button className="btn btn-secondary" onClick={scrollToTop}>
          📖 Review Again
        </button>
        <button className="btn btn-primary" onClick={acceptTerms}>
          🌍 Accept & Explore Climate Data
        </button>
      </div>
    </div>
  );
};

export default Terms;
