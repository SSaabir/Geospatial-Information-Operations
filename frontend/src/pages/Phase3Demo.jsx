import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Shield,
  Brain,
  Activity,
  BarChart3,
  AlertTriangle,
  CheckCircle,
  Eye,
  Lock,
  Target,
  TrendingUp,
  Award,
  Users,
  Clock,
  MapPin,
  FileText,
  RefreshCw,
  ArrowRight,
  Play,
  Pause
} from 'lucide-react';

const Phase3Demo = () => {
  const navigate = useNavigate();
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentDemo, setCurrentDemo] = useState('overview');
  const [demoStep, setDemoStep] = useState(0);

  const demoSections = [
    {
      id: 'overview',
      title: 'Phase 3 Overview',
      icon: Award,
      description: 'Advanced Intelligence with Security & AI Ethics',
      color: 'purple'
    },
    {
      id: 'security',
      title: 'Security Framework',
      icon: Shield,
      description: 'Real-time threat detection and incident management',
      color: 'blue'
    },
    {
      id: 'ai-ethics',
      title: 'AI Ethics Framework',
      icon: Brain,
      description: 'Responsible AI with bias detection and fairness monitoring',
      color: 'green'
    },
    {
      id: 'integration',
      title: 'Enhanced Orchestrator',
      icon: Activity,
      description: 'Multi-agent coordination with security and ethics oversight',
      color: 'indigo'
    }
  ];

  const demoSteps = [
    {
      title: "Welcome to Phase 3 Advanced Intelligence",
      content: "Comprehensive security monitoring and AI ethics framework for weather operations",
      highlight: "Enterprise-grade security and responsible AI"
    },
    {
      title: "Security Agent Validation",
      content: "Real-time data validation with threat detection and risk scoring",
      highlight: "SQL injection detection, anomaly analysis, encryption"
    },
    {
      title: "Responsible AI Framework",
      content: "Bias detection, fairness metrics, and ethics assessment for all AI models",
      highlight: "Geographical bias, temporal bias, demographic fairness"
    },
    {
      title: "Enhanced Orchestrator",
      content: "Multi-agent workflow with integrated security and ethics oversight",
      highlight: "Security validation at every step, ethics compliance monitoring"
    },
    {
      title: "Production Ready",
      content: "All components tested and ready for enterprise deployment",
      highlight: "Complete audit trails, compliance monitoring, real-time alerts"
    }
  ];

  useEffect(() => {
    let interval;
    if (isPlaying) {
      interval = setInterval(() => {
        setDemoStep((prev) => (prev + 1) % demoSteps.length);
      }, 4000);
    }
    return () => clearInterval(interval);
  }, [isPlaying, demoSteps.length]);

  const SecurityPreview = () => (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
        <Shield className="h-6 w-6 text-blue-500 mr-2" />
        Security Dashboard Preview
      </h3>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-blue-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-blue-600 font-medium">24h Incidents</p>
              <p className="text-2xl font-bold text-blue-900">12</p>
            </div>
            <AlertTriangle className="h-8 w-8 text-blue-500" />
          </div>
        </div>
        
        <div className="bg-red-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-red-600 font-medium">Critical Threats</p>
              <p className="text-2xl font-bold text-red-900">2</p>
            </div>
            <Lock className="h-8 w-8 text-red-500" />
          </div>
        </div>
        
        <div className="bg-green-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-green-600 font-medium">System Health</p>
              <p className="text-lg font-bold text-green-900">Healthy</p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-500" />
          </div>
        </div>
      </div>

      <div className="space-y-3">
        <div className="border border-gray-200 rounded-lg p-3">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium text-gray-900">Unusual API Access Pattern</h4>
              <p className="text-sm text-gray-600">High volume requests from 192.168.1.100</p>
            </div>
            <span className="px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded-full">MEDIUM</span>
          </div>
        </div>
        
        <div className="border border-gray-200 rounded-lg p-3">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium text-gray-900">Failed Authentication Attempts</h4>
              <p className="text-sm text-gray-600">Multiple login failures detected</p>
            </div>
            <span className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">HIGH</span>
          </div>
        </div>
      </div>

      <button
        onClick={() => navigate('/security')}
        className="mt-4 w-full flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        View Full Security Dashboard
        <ArrowRight className="h-4 w-4 ml-2" />
      </button>
    </div>
  );

  const AIEthicsPreview = () => (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
        <Brain className="h-6 w-6 text-purple-500 mr-2" />
        AI Ethics Dashboard Preview
      </h3>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-purple-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-purple-600 font-medium">Ethics Score</p>
              <p className="text-2xl font-bold text-purple-900">8.7/10</p>
            </div>
            <Award className="h-8 w-8 text-purple-500" />
          </div>
        </div>
        
        <div className="bg-green-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-green-600 font-medium">Fairness Compliance</p>
              <p className="text-2xl font-bold text-green-900">94.2%</p>
            </div>
            <Target className="h-8 w-8 text-green-500" />
          </div>
        </div>
        
        <div className="bg-indigo-50 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-indigo-600 font-medium">Transparency</p>
              <p className="text-2xl font-bold text-indigo-900">9.1/10</p>
            </div>
            <Eye className="h-8 w-8 text-indigo-500" />
          </div>
        </div>
      </div>

      <div className="space-y-3">
        <div className="border border-gray-200 rounded-lg p-3">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium text-gray-900">WeatherPredictor_v2.1</h4>
              <p className="text-sm text-gray-600">Ethics Score: 8.9/10 - Compliant</p>
            </div>
            <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">COMPLIANT</span>
          </div>
        </div>
        
        <div className="border border-gray-200 rounded-lg p-3">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium text-gray-900">TrendAnalyzer_v1.5</h4>
              <p className="text-sm text-gray-600">Temporal bias detected in night predictions</p>
            </div>
            <span className="px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded-full">REVIEW NEEDED</span>
          </div>
        </div>
      </div>

      <button
        onClick={() => navigate('/ai-ethics')}
        className="mt-4 w-full flex items-center justify-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
      >
        View Full AI Ethics Dashboard
        <ArrowRight className="h-4 w-4 ml-2" />
      </button>
    </div>
  );

  const IntegrationPreview = () => (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
        <Activity className="h-6 w-6 text-indigo-500 mr-2" />
        Enhanced Orchestrator Preview
      </h3>
      
      <div className="space-y-4">
        <div className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
          <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
            <CheckCircle className="h-4 w-4 text-white" />
          </div>
          <div className="flex-1">
            <h4 className="font-medium text-gray-900">Security Validation</h4>
            <p className="text-sm text-gray-600">Data validated with 0.0 risk score</p>
          </div>
          <span className="text-xs text-green-600 bg-green-100 px-2 py-1 rounded">PASSED</span>
        </div>
        
        <div className="flex items-center space-x-4 p-3 bg-gray-50 rounded-lg">
          <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
            <CheckCircle className="h-4 w-4 text-white" />
          </div>
          <div className="flex-1">
            <h4 className="font-medium text-gray-900">Ethics Assessment</h4>
            <p className="text-sm text-gray-600">AI ethics compliance verified</p>
          </div>
          <span className="text-xs text-green-600 bg-green-100 px-2 py-1 rounded">COMPLIANT</span>
        </div>
        
        <div className="flex items-center space-x-4 p-3 bg-blue-50 rounded-lg">
          <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
            <Activity className="h-4 w-4 text-white" />
          </div>
          <div className="flex-1">
            <h4 className="font-medium text-gray-900">Multi-Agent Workflow</h4>
            <p className="text-sm text-gray-600">Weather prediction with oversight</p>
          </div>
          <span className="text-xs text-blue-600 bg-blue-100 px-2 py-1 rounded">ACTIVE</span>
        </div>
      </div>

      <div className="mt-4 p-3 bg-yellow-50 rounded-lg">
        <h4 className="font-medium text-yellow-800 mb-2">Workflow Summary</h4>
        <ul className="text-sm text-yellow-700 space-y-1">
          <li>• Security validation integrated at each step</li>
          <li>• Ethics compliance monitoring active</li>
          <li>• Complete audit trail generated</li>
          <li>• Real-time compliance status tracking</li>
        </ul>
      </div>

      <button
        onClick={() => navigate('/workflow')}
        className="mt-4 w-full flex items-center justify-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
      >
        View Enhanced Workflow
        <ArrowRight className="h-4 w-4 ml-2" />
      </button>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <div className="w-16 h-16 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl flex items-center justify-center mr-4">
              <Award className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                Phase 3: Advanced Intelligence
              </h1>
              <p className="text-gray-600 text-lg">Security Framework & AI Ethics Implementation</p>
            </div>
          </div>

          {/* Demo Controls */}
          <div className="flex items-center justify-center space-x-4 mb-8">
            <button
              onClick={() => setIsPlaying(!isPlaying)}
              className={`flex items-center px-6 py-3 rounded-lg font-medium transition-colors ${
                isPlaying 
                  ? 'bg-red-600 text-white hover:bg-red-700' 
                  : 'bg-green-600 text-white hover:bg-green-700'
              }`}
            >
              {isPlaying ? <Pause className="h-4 w-4 mr-2" /> : <Play className="h-4 w-4 mr-2" />}
              {isPlaying ? 'Pause Demo' : 'Start Demo'}
            </button>
            
            <div className="text-sm text-gray-600">
              Step {demoStep + 1} of {demoSteps.length}
            </div>
          </div>

          {/* Demo Progress */}
          <div className="max-w-4xl mx-auto mb-8">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-3">
                {demoSteps[demoStep].title}
              </h2>
              <p className="text-gray-700 text-lg mb-4">
                {demoSteps[demoStep].content}
              </p>
              <div className="bg-gradient-to-r from-purple-100 to-indigo-100 rounded-lg p-4">
                <p className="text-purple-800 font-medium">
                  ✨ {demoSteps[demoStep].highlight}
                </p>
              </div>
              
              {/* Progress Bar */}
              <div className="mt-4">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-purple-600 to-indigo-600 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${((demoStep + 1) / demoSteps.length) * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex justify-center mb-8">
          <div className="bg-white rounded-lg shadow-lg p-2 flex space-x-2">
            {demoSections.map((section) => (
              <button
                key={section.id}
                onClick={() => setCurrentDemo(section.id)}
                className={`flex items-center px-4 py-2 rounded-lg font-medium transition-colors ${
                  currentDemo === section.id
                    ? `bg-${section.color}-600 text-white`
                    : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
                }`}
              >
                <section.icon className="h-4 w-4 mr-2" />
                {section.title}
              </button>
            ))}
          </div>
        </div>

        {/* Demo Content */}
        <div className="space-y-8">
          {currentDemo === 'overview' && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <SecurityPreview />
              <AIEthicsPreview />
              <IntegrationPreview />
            </div>
          )}

          {currentDemo === 'security' && (
            <div className="max-w-4xl mx-auto">
              <SecurityPreview />
            </div>
          )}

          {currentDemo === 'ai-ethics' && (
            <div className="max-w-4xl mx-auto">
              <AIEthicsPreview />
            </div>
          )}

          {currentDemo === 'integration' && (
            <div className="max-w-4xl mx-auto">
              <IntegrationPreview />
            </div>
          )}
        </div>

        {/* Features Overview */}
        <div className="mt-16 bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-8">
            🚀 Phase 3 Implementation Complete
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="h-8 w-8 text-blue-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Security Agent</h3>
              <p className="text-sm text-gray-600">
                Real-time threat detection, data validation, and incident management
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Brain className="h-8 w-8 text-purple-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Responsible AI</h3>
              <p className="text-sm text-gray-600">
                Bias detection, fairness monitoring, and ethics compliance
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Activity className="h-8 w-8 text-indigo-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Enhanced Orchestrator</h3>
              <p className="text-sm text-gray-600">
                Multi-agent workflow with integrated security and ethics oversight
              </p>
            </div>

            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="h-8 w-8 text-green-600" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Security Dashboard</h3>
              <p className="text-sm text-gray-600">
                Comprehensive monitoring, alerting, and compliance reporting
              </p>
            </div>
          </div>

          <div className="mt-8 text-center">
            <p className="text-gray-600 mb-6">
              All Phase 3 components are production-ready with comprehensive testing and validation
            </p>
            <div className="flex justify-center space-x-4">
              <button
                onClick={() => navigate('/security')}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Explore Security Dashboard
              </button>
              <button
                onClick={() => navigate('/ai-ethics')}
                className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
              >
                Explore AI Ethics Dashboard
              </button>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>Phase 3 Advanced Intelligence Framework - Production Ready</p>
          <p>Enterprise-grade Security & AI Ethics for Weather Operations</p>
        </div>
      </div>
    </div>
  );
};

export default Phase3Demo;