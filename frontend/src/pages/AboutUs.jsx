import React from 'react';
import { Globe, Users, Target, BarChart3 } from 'lucide-react';

export default function AboutUs() {
  const teamMembers = [
    { name: "Saabir", role: "Data Science Student" },
    { name: "Abdullah", role: "Data Science Student" },
    { name: "Mathushan", role: "Data Science Student" },
    { name: "Sakuni", role: "Data Science Student" }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-amber-50" style={{ backgroundColor: '#F9F5F0' }}>
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <div className="flex items-center space-x-3">
            <Globe className="w-8 h-8 text-orange-600" />
            <h1 className="text-2xl font-bold text-gray-800">Climate Explorer</h1>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-4 py-12">
        {/* About Us Section */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-800 mb-6">About Us</h1>
          <div className="max-w-3xl mx-auto">
            <p className="text-lg md:text-xl text-gray-600 leading-relaxed mb-8">
              We are a dedicated team of researchers and developers passionate about making climate change data 
              accessible and understandable for everyone. Our Climate Data Explorer platform transforms complex 
              environmental datasets into clear, interactive visualizations that empower informed decision-making 
              and raise awareness about our changing planet.
            </p>
            <div className="bg-white rounded-lg shadow-sm p-6 border-l-4 border-orange-400" style={{ backgroundColor: '#F2EAD3' }}>
              <p className="text-gray-700 italic">
                "Through data visualization and accessible tools, we aim to bridge the gap between 
                scientific research and public understanding of climate change."
              </p>
            </div>
          </div>
        </div>

        {/* Mission Section */}
        <div className="mb-16">
          <div className="bg-white rounded-xl shadow-lg p-8 md:p-12" style={{ backgroundColor: '#F2EAD3' }}>
            <div className="flex items-center justify-center mb-6">
              <Target className="w-12 h-12 text-orange-700" />
            </div>
            <h2 className="text-3xl font-bold text-center text-gray-800 mb-6">Our Mission</h2>
            <div className="max-w-4xl mx-auto">
              <p className="text-lg text-gray-700 text-center leading-relaxed mb-6">
                To democratize access to climate data and create powerful visualization tools that help 
                individuals, organizations, and policymakers understand the urgent realities of climate change.
              </p>
              <div className="grid md:grid-cols-3 gap-6 mt-8">
                <div className="text-center p-4">
                  <BarChart3 className="w-10 h-10 text-orange-600 mx-auto mb-3" />
                  <h3 className="font-semibold text-gray-800 mb-2">Data Visualization</h3>
                  <p className="text-sm text-gray-600">Transform complex datasets into intuitive charts and graphs</p>
                </div>
                <div className="text-center p-4">
                  <Globe className="w-10 h-10 text-orange-600 mx-auto mb-3" />
                  <h3 className="font-semibold text-gray-800 mb-2">Global Impact</h3>
                  <p className="text-sm text-gray-600">Create awareness about climate change worldwide</p>
                </div>
                <div className="text-center p-4">
                  <Users className="w-10 h-10 text-orange-600 mx-auto mb-3" />
                  <h3 className="font-semibold text-gray-800 mb-2">Community Driven</h3>
                  <p className="text-sm text-gray-600">Built by passionate individuals for the greater good</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Team Section */}
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-800 mb-12">Meet Our Team</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {teamMembers.map((member, index) => (
              <div 
                key={index} 
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow duration-300"
                style={{ backgroundColor: index % 2 === 0 ? '#F4991A' : '#F2EAD3' }}
              >
                <div className="w-20 h-20 bg-orange-200 rounded-full mx-auto mb-4 flex items-center justify-center">
                  <span className="text-2xl font-bold text-orange-700">
                    {member.name.charAt(0)}
                  </span>
                </div>
                <h3 className="text-xl font-semibold text-gray-800 mb-2">{member.name}</h3>
                <p className="text-gray-600">{member.role}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Call to Action */}
        <div className="text-center mt-16">
          <div className="bg-white rounded-lg shadow-sm p-8" style={{ backgroundColor: '#F2EAD3' }}>
            <h3 className="text-2xl font-bold text-gray-800 mb-4">Join Our Mission</h3>
            <p className="text-gray-600 mb-6">
              Explore our climate data tools and be part of the solution for a sustainable future.
            </p>
            <button className="bg-orange-600 hover:bg-orange-700 text-white px-8 py-3 rounded-lg font-semibold transition-colors duration-300">
              Explore Climate Data
            </button>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8 mt-16">
        <div className="max-w-6xl mx-auto px-4 text-center">
          <div className="flex items-center justify-center space-x-3 mb-4">
            <Globe className="w-6 h-6" />
            <span className="text-lg font-semibold">Climate Explorer</span>
          </div>
          <p className="text-gray-400">
            Empowering action through accessible climate data visualization
          </p>
        </div>
      </footer>
    </div>
  );
}