import React, { useState, useEffect } from 'react';
import { ChevronDown, ChevronUp, Search, Cloud, TrendingUp, MessageSquare, FileText, Database, BarChart3, Brain, Shield, Clock, Users, Star, ArrowRight, HelpCircle, Zap, Globe, ChevronRight } from 'lucide-react';

const FaqPage = () => {
  const [activeCategory, setActiveCategory] = useState('general');
  const [expandedItem, setExpandedItem] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filteredFaqs, setFilteredFaqs] = useState([]);

  const categories = [
    { id: 'general', name: 'General', icon: HelpCircle, color: '#F4991A' },
    { id: 'data', name: 'Data & Analytics', icon: BarChart3, color: '#F2EAD3' },
    { id: 'features', name: 'Features', icon: Zap, color: '#F2EAD3' },
    { id: 'technical', name: 'Technical', icon: Database, color: '#F4991A' },
    { id: 'account', name: 'Account', icon: Users, color: '#F2EAD3' },
    { id: 'pricing', name: 'Pricing', icon: Star, color: '#F2EAD3' }
  ];

  const faqData = {
    general: [
      {
        id: 1,
        question: "What is the Climate Change Data Explorer?",
        answer: "The Climate Change Data Explorer is a comprehensive platform that provides access to decades of weather and climate data for Sri Lanka, specifically focusing on Colombo and surrounding regions. Our platform combines historical weather data with advanced analytics, AI-powered insights, and predictive modeling to help researchers, students, and climate enthusiasts understand weather patterns and climate trends.",
        tags: ["overview", "platform", "climate", "data"]
      },
      {
        id: 2,
        question: "What geographical areas does your data cover?",
        answer: "Currently, our primary focus is on Colombo, Western Province, Sri Lanka. Our dataset includes comprehensive weather data dating back to 1997, covering temperature, humidity, precipitation, wind patterns, solar radiation, UV index, and various weather conditions. We're continuously working to expand our coverage to other regions of Sri Lanka.",
        tags: ["location", "coverage", "sri lanka", "colombo"]
      },
      {
        id: 3,
        question: "How accurate and reliable is your climate data?",
        answer: "Our climate data is sourced from reliable meteorological stations and verified through multiple quality control processes. We maintain high standards of data integrity with regular validation checks, anomaly detection, and cross-referencing with official weather services. Our historical data spans over 25 years, providing a robust foundation for trend analysis.",
        tags: ["accuracy", "reliability", "quality", "verification"]
      },
      {
        id: 4,
        question: "Can I use this platform for academic research?",
        answer: "Absolutely! Our platform is designed to support academic research, student projects, and scientific studies. You can export data in various formats, generate detailed reports, and access our API for programmatic data retrieval. We also provide proper citation guidelines for academic use and offer educational discounts for students and institutions.",
        tags: ["academic", "research", "education", "citation"]
      }
    ],
    data: [
      {
        id: 5,
        question: "What types of climate data do you provide?",
        answer: "Our comprehensive dataset includes: Temperature (max, min, feels-like), Humidity levels, Precipitation data, Wind speed and direction, Solar radiation and energy, UV index, Atmospheric pressure, Weather conditions and descriptions, Sunrise/sunset times, Moon phases, and Severe weather risk assessments. All data is timestamped and includes quality indicators.",
        tags: ["temperature", "humidity", "precipitation", "weather", "solar"]
      },
      {
        id: 6,
        question: "How far back does your historical data go?",
        answer: "Our historical weather data begins from January 1997 and continues to the present day. This gives us over 25 years of continuous climate observations, which is sufficient for identifying long-term trends, seasonal patterns, and climate anomalies. We update our dataset daily with the latest weather observations.",
        tags: ["historical", "timeline", "1997", "continuous"]
      },
      {
        id: 7,
        question: "In what formats can I download the data?",
        answer: "We support multiple data export formats to suit different needs: CSV for spreadsheet analysis, JSON for web applications, Excel (.xlsx) for business users, PDF reports for presentations, XML for data exchange, and API access for real-time integration. You can also customize the date range, parameters, and aggregation levels for your exports.",
        tags: ["export", "csv", "json", "excel", "api"]
      },
      {
        id: 8,
        question: "How frequently is the data updated?",
        answer: "Our climate database is updated daily with the latest weather observations. Historical data remains static (as it represents past events), but we continuously add new daily records. Our trend analysis and predictive models are recalculated weekly to incorporate the latest data patterns and improve accuracy.",
        tags: ["updates", "daily", "frequency", "real-time"]
      }
    ],
    features: [
      {
        id: 9,
        question: "What can I do with the AI Chat feature?",
        answer: "Our AI Chat Assistant is powered by advanced natural language processing and can help you with: Interpreting climate data trends, Answering questions about weather patterns, Explaining statistical analyses, Providing insights about specific time periods, Suggesting research directions, Creating custom queries, and Generating summary reports. Simply ask questions in plain English!",
        tags: ["ai", "chat", "assistant", "analysis", "insights"]
      },
      {
        id: 10,
        question: "How does the prediction system work?",
        answer: "Our prediction system uses machine learning algorithms trained on historical climate data to forecast future weather patterns. It analyzes multiple variables including temperature trends, seasonal cycles, humidity patterns, and atmospheric conditions. You can generate predictions for various timeframes and receive confidence intervals for each forecast.",
        tags: ["prediction", "machine learning", "forecasting", "algorithms"]
      },
      {
        id: 11,
        question: "Can I create custom reports and visualizations?",
        answer: "Yes! Our platform offers extensive customization options: Interactive charts and graphs, Custom date range selections, Parameter-specific analyses, Comparative studies between different time periods, Trend analysis with statistical significance, Export options for presentations, and Automated report generation. You can save and share your custom reports with others.",
        tags: ["reports", "visualization", "charts", "custom", "export"]
      },
      {
        id: 12,
        question: "What trend analysis capabilities do you offer?",
        answer: "Our trend analyzer provides: Long-term climate trend identification, Seasonal pattern analysis, Anomaly detection, Statistical significance testing, Correlation analysis between variables, Climate change indicators, Extreme weather event tracking, and Comparative analysis across different years or decades.",
        tags: ["trends", "analysis", "patterns", "statistics", "anomalies"]
      }
    ],
    technical: [
      {
        id: 13,
        question: "Do you provide an API for developers?",
        answer: "Yes, we offer a comprehensive RESTful API that allows developers to integrate our climate data into their applications. The API supports various endpoints for historical data, real-time updates, trend analysis, and predictions. We provide detailed documentation, code examples in multiple programming languages, and SDKs for popular frameworks.",
        tags: ["api", "developers", "integration", "rest", "sdk"]
      },
      {
        id: 14,
        question: "What are the system requirements for using the platform?",
        answer: "Our web-based platform works on any modern browser (Chrome, Firefox, Safari, Edge) with JavaScript enabled. For optimal experience, we recommend: A stable internet connection (minimum 1 Mbps), Modern browser (released within last 2 years), Screen resolution of 1024x768 or higher, and JavaScript enabled. No additional software installation required.",
        tags: ["requirements", "browser", "system", "compatibility"]
      },
      {
        id: 15,
        question: "How do you ensure data security and privacy?",
        answer: "We take data security seriously with: SSL/TLS encryption for all data transmission, Secure user authentication and authorization, Regular security audits and updates, GDPR-compliant data handling, Secure cloud infrastructure, Data backup and recovery systems, and Limited access controls. We never share personal information with third parties.",
        tags: ["security", "privacy", "encryption", "gdpr", "protection"]
      },
      {
        id: 16,
        question: "Can I integrate your data with other tools and platforms?",
        answer: "Absolutely! Our platform supports integration with: Python/R for statistical analysis, Excel and Google Sheets via CSV export, Business intelligence tools (Tableau, Power BI), GIS software for mapping, Custom applications via our API, Jupyter notebooks for research, and Various database systems through our export options.",
        tags: ["integration", "python", "excel", "tableau", "gis"]
      }
    ],
    account: [
      {
        id: 17,
        question: "How do I create an account and get started?",
        answer: "Getting started is simple: Click the 'Login' button and select 'Create Account', Fill in your basic information (name, email, organization), Verify your email address, Choose your subscription plan, Complete your profile setup, and Start exploring! We also offer a free trial period so you can test all features before committing.",
        tags: ["account", "registration", "signup", "getting started"]
      },
      {
        id: 18,
        question: "What types of user accounts are available?",
        answer: "We offer several account types: Free Trial (30-day access to basic features), Individual Researcher (full access for personal use), Academic Institution (special pricing for schools/universities), Commercial License (for business applications), and Enterprise (custom solutions for large organizations). Each tier includes different data limits and features.",
        tags: ["account types", "pricing", "plans", "subscription"]
      },
      {
        id: 19,
        question: "Can I share my account or data with team members?",
        answer: "Yes, depending on your subscription plan: Individual accounts allow limited sharing via exported reports, Institutional accounts support multiple user access, Enterprise plans include team collaboration features, and You can share generated reports and visualizations with anyone. We also offer group discounts for multiple accounts from the same organization.",
        tags: ["sharing", "collaboration", "team", "multiple users"]
      },
      {
        id: 20,
        question: "How can I manage my subscription and billing?",
        answer: "Account management is easy through your user dashboard: View and modify subscription details, Update payment information, Download invoices and receipts, Monitor usage and data limits, Upgrade or downgrade plans, Set up automatic renewals, and Cancel subscription (with data export period). We accept major credit cards and institutional purchase orders.",
        tags: ["billing", "subscription", "payment", "management"]
      }
    ],
    pricing: [
      {
        id: 21,
        question: "Is there a free version available?",
        answer: "Yes! We offer a 30-day free trial that includes: Access to basic climate data, Limited data export (up to 1000 records), Basic visualization tools, Sample reports and analyses, AI chat with daily limits, and Access to our getting-started tutorials. No credit card required for the trial period.",
        tags: ["free", "trial", "basic", "limitations"]
      },
      {
        id: 22,
        question: "What are your subscription pricing plans?",
        answer: "Our pricing is designed to be accessible: Free Trial ($0/month - 30 days), Individual ($15/month - full access, unlimited exports), Academic ($8/month - 50% discount with .edu email), Commercial ($45/month - business features, priority support), Enterprise (custom pricing - dedicated support, custom integrations). All plans include regular updates and basic support.",
        tags: ["pricing", "cost", "subscription", "commercial", "academic"]
      },
      {
        id: 23,
        question: "Do you offer discounts for students and educational institutions?",
        answer: "Absolutely! We support education with: 50% student discount with valid student ID, Educational institution licenses at reduced rates, Free access for qualifying research projects, Bulk pricing for classroom use, Special pricing for developing countries, and Extended trial periods for academic evaluation. Contact us for custom educational pricing.",
        tags: ["student", "education", "discount", "academic", "institution"]
      },
      {
        id: 24,
        question: "What payment methods do you accept?",
        answer: "We accept various payment methods: All major credit cards (Visa, MasterCard, American Express), PayPal for individual subscriptions, Bank transfers for institutional accounts, Purchase orders from educational institutions, and Cryptocurrency payments (Bitcoin, Ethereum) for privacy-conscious users. All transactions are secure and encrypted.",
        tags: ["payment", "credit card", "paypal", "bank transfer", "crypto"]
      }
    ]
  };

  // Filter FAQs based on search query
  useEffect(() => {
    if (searchQuery.trim() === '') {
      setFilteredFaqs(faqData[activeCategory] || []);
    } else {
      const filtered = (faqData[activeCategory] || []).filter(faq =>
        faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
        faq.answer.toLowerCase().includes(searchQuery.toLowerCase()) ||
        faq.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
      );
      setFilteredFaqs(filtered);
    }
  }, [searchQuery, activeCategory]);

  const toggleExpanded = (id) => {
    setExpandedItem(expandedItem === id ? null : id);
  };

  const handleCategoryChange = (categoryId) => {
    setActiveCategory(categoryId);
    setExpandedItem(null);
    setSearchQuery('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-amber-50" style={{backgroundColor: '#F9F5F0'}}>
      {/* Hero Section */}
      <section className="py-20 px-4 text-center">
        <div className="max-w-4xl mx-auto">
          <div className="inline-flex items-center justify-center mb-6">
            <div className="p-4 rounded-full" style={{backgroundColor: '#F2EAD3'}}>
              <HelpCircle className="w-12 h-12" style={{color: '#F4991A'}} />
            </div>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-orange-600 to-green-800 bg-clip-text text-transparent">
            Frequently Asked Questions
          </h1>
          <p className="text-xl text-gray-600 mb-12 max-w-2xl mx-auto">
            Find answers to common questions about our Climate Data Explorer platform, features, and services.
          </p>

          {/* Search Bar */}
          <div className="relative max-w-2xl mx-auto">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search className="w-5 h-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search FAQs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-4 text-lg border-2 rounded-2xl focus:outline-none focus:ring-4 transition-all duration-200"
              style={{
                borderColor: '#F2EAD3',
                backgroundColor: 'white',
                focusRingColor: '#F2EAD3'
              }}
              onFocus={(e) => e.target.style.borderColor = '#F4991A'}
              onBlur={(e) => e.target.style.borderColor = '#F2EAD3'}
            />
          </div>
        </div>
      </section>

      {/* Main Content */}
      <section className="py-12 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col lg:flex-row gap-8">
            {/* Category Sidebar */}
            <div className="lg:w-1/4">
              <div className="bg-white rounded-2xl p-6 shadow-xl sticky top-6 border border-orange-100">
                <h3 className="text-lg font-semibold mb-6 text-gray-800">Categories</h3>
                <div className="space-y-2">
                  {categories.map((category) => {
                    const Icon = category.icon;
                    return (
                      <button
                        key={category.id}
                        onClick={() => handleCategoryChange(category.id)}
                        className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 text-left group ${
                          activeCategory === category.id
                            ? 'shadow-lg transform scale-105'
                            : 'hover:scale-102 hover:shadow-md'
                        }`}
                        style={{
                          backgroundColor: activeCategory === category.id ? category.color : '#F9FAFB',
                          color: activeCategory === category.id ? 'white' : '#374151'
                        }}
                      >
                        <Icon className={`w-5 h-5 ${activeCategory === category.id ? 'text-white' : 'text-gray-500'} group-hover:scale-110 transition-transform`} />
                        <span className="font-medium">{category.name}</span>
                        <ChevronRight className={`w-4 h-4 ml-auto ${activeCategory === category.id ? 'text-white' : 'text-gray-400'}`} />
                      </button>
                    );
                  })}
                </div>

                {/* Quick Stats */}
                <div className="mt-8 p-4 rounded-xl" style={{backgroundColor: '#F9F5F0'}}>
                  <h4 className="font-semibold text-gray-800 mb-3">Quick Stats</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Total FAQs</span>
                      <span className="font-semibold" style={{color: '#F4991A'}}>24</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Categories</span>
                      <span className="font-semibold" style={{color: '#F4991A'}}>6</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Updated</span>
                      <span className="font-semibold" style={{color: '#F4991A'}}>Today</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* FAQ Content */}
            <div className="lg:w-3/4">
              <div className="bg-white rounded-2xl shadow-xl border border-orange-100 overflow-hidden">
                {/* Category Header */}
                <div className="p-6 border-b border-orange-100" style={{backgroundColor: '#F9F5F0'}}>
                  <div className="flex items-center space-x-3">
                    {categories.find(cat => cat.id === activeCategory) && (
                      <>
                        {React.createElement(categories.find(cat => cat.id === activeCategory).icon, {
                          className: "w-6 h-6",
                          style: { color: categories.find(cat => cat.id === activeCategory).color }
                        })}
                        <h2 className="text-2xl font-bold text-gray-800">
                          {categories.find(cat => cat.id === activeCategory).name}
                        </h2>
                      </>
                    )}
                  </div>
                  {filteredFaqs.length > 0 && (
                    <p className="text-gray-600 mt-2">
                      {filteredFaqs.length} question{filteredFaqs.length !== 1 ? 's' : ''} 
                      {searchQuery && ` matching "${searchQuery}"`}
                    </p>
                  )}
                </div>

                {/* FAQ Items */}
                <div className="divide-y divide-orange-100">
                  {filteredFaqs.length > 0 ? (
                    filteredFaqs.map((faq, index) => (
                      <div key={faq.id} className="transition-all duration-200 hover:bg-gray-50">
                        <button
                          onClick={() => toggleExpanded(faq.id)}
                          className="w-full px-6 py-6 text-left flex items-center justify-between group"
                        >
                          <div className="flex-1 pr-4">
                            <h3 className="text-lg font-semibold text-gray-800 group-hover:text-orange-600 transition-colors">
                              {faq.question}
                            </h3>
                            <div className="flex flex-wrap gap-2 mt-2">
                              {faq.tags.slice(0, 3).map((tag) => (
                                <span
                                  key={tag}
                                  className="px-2 py-1 text-xs rounded-full"
                                  style={{backgroundColor: '#F2EAD3', color: '#6B46C1'}}
                                >
                                  {tag}
                                </span>
                              ))}
                            </div>
                          </div>
                          <div className={`p-2 rounded-full transition-all duration-200 ${expandedItem === faq.id ? 'rotate-180' : ''}`}
                               style={{backgroundColor: expandedItem === faq.id ? '#F4991A' : '#F3F4F6'}}>
                            <ChevronDown className={`w-5 h-5 ${expandedItem === faq.id ? 'text-white' : 'text-gray-600'}`} />
                          </div>
                        </button>
                        
                        {expandedItem === faq.id && (
                          <div className="px-6 pb-6 animate-in slide-in-from-top-2 duration-200">
                            <div className="p-6 rounded-xl" style={{backgroundColor: '#F9F5F0'}}>
                              <p className="text-gray-700 leading-relaxed text-base">
                                {faq.answer}
                              </p>
                              
                              {/* All Tags */}
                              <div className="flex flex-wrap gap-2 mt-4">
                                {faq.tags.map((tag) => (
                                  <span
                                    key={tag}
                                    className="px-3 py-1 text-sm rounded-full border transition-colors hover:shadow-md cursor-pointer"
                                    style={{
                                      backgroundColor: 'white',
                                      borderColor: '#F2EAD3',
                                      color: '#6B46C1'
                                    }}
                                  >
                                    #{tag}
                                  </span>
                                ))}
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    ))
                  ) : (
                    <div className="px-6 py-12 text-center">
                      <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-gray-700 mb-2">No FAQs found</h3>
                      <p className="text-gray-500">
                        {searchQuery 
                          ? `No questions match "${searchQuery}". Try different keywords.`
                          : "No questions available in this category yet."
                        }
                      </p>
                      {searchQuery && (
                        <button
                          onClick={() => setSearchQuery('')}
                          className="mt-4 px-4 py-2 rounded-lg text-white font-medium transition-all hover:scale-105"
                          style={{backgroundColor: '#F4991A'}}
                        >
                          Clear Search
                        </button>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Still Have Questions Section */}
      <section className="py-20 px-4" style={{backgroundColor: 'white'}}>
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-6 text-gray-800">Still Have Questions?</h2>
          <p className="text-lg text-gray-600 mb-8">
            Can't find what you're looking for? Our team is here to help you get the most out of our platform.
          </p>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 rounded-xl transition-all duration-300 hover:scale-105 hover:shadow-lg" style={{backgroundColor: '#F9F5F0'}}>
              <div className="w-12 h-12 rounded-full mx-auto mb-4 flex items-center justify-center" style={{backgroundColor: '#F4991A'}}>
                <MessageSquare className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold mb-2 text-gray-800">Live Chat</h3>
              <p className="text-gray-600 mb-4">Get instant help from our AI assistant or connect with our support team.</p>
              <button className="px-4 py-2 rounded-lg text-white font-medium transition-all hover:scale-105" style={{backgroundColor: '#F4991A'}}>
                Start Chat
              </button>
            </div>

            <div className="p-6 rounded-xl transition-all duration-300 hover:scale-105 hover:shadow-lg" style={{backgroundColor: '#F2EAD3'}}>
              <div className="w-12 h-12 rounded-full mx-auto mb-4 flex items-center justify-center" style={{backgroundColor: '#F2EAD3'}}>
                <Globe className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold mb-2 text-gray-800">Documentation</h3>
              <p className="text-gray-600 mb-4">Explore our comprehensive guides, tutorials, and API documentation.</p>
              <button className="px-4 py-2 rounded-lg font-medium transition-all hover:scale-105 border-2" 
                      style={{borderColor: '#F2EAD3', color: '#6B46C1', backgroundColor: 'white'}}>
                View Docs
              </button>
            </div>

            <div className="p-6 rounded-xl transition-all duration-300 hover:scale-105 hover:shadow-lg" style={{backgroundColor: '#F2EAD3'}}>
              <div className="w-12 h-12 rounded-full mx-auto mb-4 flex items-center justify-center" style={{backgroundColor: '#F4991A'}}>
                <Users className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold mb-2 text-gray-800">Contact Support</h3>
              <p className="text-gray-600 mb-4">Reach out to our support team for personalized assistance and guidance.</p>
              <button className="px-4 py-2 rounded-lg text-white font-medium transition-all hover:scale-105" style={{backgroundColor: '#F4991A'}}>
                Contact Us
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default FaqPage;