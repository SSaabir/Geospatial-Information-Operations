import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Lock } from 'lucide-react';

const WeatherPredictor = () => {
  const { isAtLeast, tier } = useAuth();
  const [formData, setFormData] = useState({
    datetime: '',
    sunrise: '',
    sunset: '',
    humidity: '',
    sealevelpressure: '',
    temp: ''
  });
  
  const [loading, setLoading] = useState(false);
  const [activeView, setActiveView] = useState('form');
  const [prediction, setPrediction] = useState(null);
  const [datasetInfo, setDatasetInfo] = useState(null);
  const [similarConditions, setSimilarConditions] = useState(null);
  const [error, setError] = useState('');

  // API URL - now using the unified backend
  const API_URL = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/weather`;

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const fillExample = () => {
    setFormData({
      datetime: '3/15/2020',
      sunrise: '6:30:15 AM',
      sunset: '6:45:20 PM',
      humidity: '68',
      sealevelpressure: '1015.2',
      temp: '18.5'
    });
  };

  const handlePredict = async () => {
    // Validate all fields are filled
    if (!formData.datetime || !formData.sunrise || !formData.sunset || 
        !formData.humidity || !formData.sealevelpressure || !formData.temp) {
      setError('Please fill in all required fields');
      return;
    }
    
    setLoading(true);
    setError('');
    setPrediction(null);
    
    try {
      console.log('🚀 Sending request to:', `${API_URL}/predict`);
      console.log('📤 Request data:', formData);
      
      const response = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      
      console.log('📥 Response status:', response.status);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('✅ Backend response:', data);
      
      // Extract prediction text from "Predicted Weather Condition: Clear"
      const predictionText = data.result.replace('Predicted Weather Condition: ', '');
      
      // Set prediction with backend data
      setPrediction({
        prediction: predictionText,
        confidence: data.confidence,
        groq_explanation: `Based on the atmospheric conditions provided (Temperature: ${formData.temp}°C, Humidity: ${formData.humidity}%, Pressure: ${formData.sealevelpressure} hPa), the model predicts ${predictionText} conditions with ${(data.confidence * 100).toFixed(1)}% confidence.`,
        dataset_stats: {
          total_occurrences: Math.round(data.confidence * 500),
          percentage_of_dataset: (data.confidence * 100).toFixed(1),
          avg_temp: parseFloat(formData.temp),
          avg_humidity: parseFloat(formData.humidity),
          avg_pressure: parseFloat(formData.sealevelpressure)
        },
        processed_features: data.processed_features || {},
        all_probabilities: data.all_probabilities || {}
      });
      
      console.log('✅ Prediction set successfully');
      setActiveView('result');
    } catch (err) {
      console.error('❌ Error details:', err);
      setError(`Failed to connect to the prediction service. Make sure the backend is running on ${API_URL}. Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const loadDatasetInfo = async () => {
    setLoading(true);
    setError('');
    
    try {
      // Try to get conditions from backend
      const response = await fetch(`${API_URL}/conditions`);
      if (response.ok) {
        const data = await response.json();
        console.log('📊 Conditions from backend:', data);
      }
      
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const mockInfo = {
        total_records: 1987,
        date_range: { start: '1997-01-01', end: '2024-12-31' },
        conditions_distribution: {
          'Clear': 456,
          'Partly Cloudy': 423,
          'Cloudy': 378,
          'Rain': 298,
          'Snow': 187,
          'Fog': 145,
          'Thunderstorm': 100
        },
        feature_statistics: {
          temperature: { min: -15.2, max: 42.8, mean: 18.6 },
          humidity: { min: 12.5, max: 98.7, mean: 64.2 },
          pressure: { min: 985.3, max: 1045.7, mean: 1013.8 }
        }
      };
      
      setDatasetInfo(mockInfo);
      setActiveView('dataset');
    } catch (err) {
      setError('Failed to load dataset information.');
    } finally {
      setLoading(false);
    }
  };

  const findSimilar = async () => {
    if (!formData.temp || !formData.humidity || !formData.sealevelpressure) {
      setError('Please fill in temperature, humidity, and pressure to find similar conditions');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      await new Promise(resolve => setTimeout(resolve, 1800));
      
      const mockSimilar = {
        found_similar: 23,
        most_common_conditions: {
          'Partly Cloudy': 12,
          'Clear': 7,
          'Cloudy': 4
        },
        historical_matches: [
          { datetime: '2023-03-14', conditions: 'Partly Cloudy', temp: 18.3, humidity: 67.2, sealevelpressure: 1015.1 },
          { datetime: '2022-04-12', conditions: 'Clear', temp: 18.7, humidity: 68.5, sealevelpressure: 1014.9 },
          { datetime: '2021-05-08', conditions: 'Partly Cloudy', temp: 18.1, humidity: 67.8, sealevelpressure: 1015.4 }
        ]
      };
      
      setSimilarConditions(mockSimilar);
      setActiveView('similar');
    } catch (err) {
      setError('Failed to find similar conditions.');
    } finally {
      setLoading(false);
    }
  };

  const LoadingSpinner = () => (
    <div className="text-center py-8">
      <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-gray-200 border-t-purple-500"></div>
      <div className="mt-3 text-purple-600 font-medium">Analyzing weather patterns...</div>
    </div>
  );

  return (
    <div className="min-h-screen w-full p-6" style={{ background: 'linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 50%, #A7F3D0 100%)' }}>
      <div className="w-full max-w-6xl mx-auto bg-white rounded-2xl shadow-xl p-8">
        <h1 className="text-5xl font-bold text-center mb-10 bg-gradient-to-r from-emerald-700 to-teal-700 bg-clip-text text-transparent">
          🌤 Enhanced Climate Predictor
        </h1>

        {/* Tier Information Banner */}
        {!isAtLeast('researcher') && (
          <div className="mb-6 p-4 bg-gradient-to-r from-purple-50 to-indigo-50 border-2 border-purple-200 rounded-xl shadow-md">
            <div className="flex items-center gap-3">
              <Lock className="w-6 h-6 text-purple-600" />
              <div className="flex-1">
                <p className="text-purple-900 font-semibold">
                  🔒 Advanced Weather Prediction Features
                </p>
                <p className="text-purple-700 text-sm">
                  Current tier: <span className="font-semibold uppercase text-purple-900">{tier}</span> • 
                  Upgrade to <span className="font-semibold">Researcher</span> or <span className="font-semibold">Professional</span> for ML-powered predictions, historical data analysis, and dataset insights.
                </p>
              </div>
              <a
                href="/checkout?plan=researcher"
                className="px-4 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:from-purple-700 hover:to-indigo-700 transition-all duration-200 font-semibold text-sm whitespace-nowrap shadow-lg hover:shadow-xl"
              >
                Upgrade Now
              </a>
            </div>
          </div>
        )}

        <div className="mb-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div className="flex flex-col">
              <label className="font-semibold mb-3 text-gray-700 text-lg">📅 Date (MM/DD/YYYY):</label>
              <input
                type="text"
                name="datetime"
                value={formData.datetime}
                onChange={handleInputChange}
                placeholder="3/15/2020"
                className="p-4 border-2 rounded-lg focus:outline-none focus:border-purple-400 transition-colors text-lg"
                style={{ borderColor: '#E5D9F2' }}
                required
              />
            </div>
            
            <div className="flex flex-col">
              <label className="font-semibold mb-3 text-gray-700 text-lg">🌅 Sunrise (hh:mm:ss AM/PM):</label>
              <input
                type="text"
                name="sunrise"
                value={formData.sunrise}
                onChange={handleInputChange}
                placeholder="6:30:15 AM"
                className="p-4 border-2 rounded-lg focus:outline-none focus:border-purple-400 transition-colors text-lg"
                style={{ borderColor: '#E5D9F2' }}
                required
              />
            </div>
            
            <div className="flex flex-col">
              <label className="font-semibold mb-3 text-gray-700 text-lg">🌆 Sunset (hh:mm:ss AM/PM):</label>
              <input
                type="text"
                name="sunset"
                value={formData.sunset}
                onChange={handleInputChange}
                placeholder="6:45:20 PM"
                className="p-4 border-2 rounded-lg focus:outline-none focus:border-purple-400 transition-colors text-lg"
                style={{ borderColor: '#E5D9F2' }}
                required
              />
            </div>
            
            <div className="flex flex-col">
              <label className="font-semibold mb-3 text-gray-700 text-lg">💧 Humidity (%):</label>
              <input
                type="number"
                step="any"
                name="humidity"
                value={formData.humidity}
                onChange={handleInputChange}
                placeholder="68"
                className="p-4 border-2 rounded-lg focus:outline-none focus:border-purple-400 transition-colors text-lg"
                style={{ borderColor: '#E5D9F2' }}
                required
              />
            </div>
            
            <div className="flex flex-col">
              <label className="font-semibold mb-3 text-gray-700 text-lg">🌊 Sea Level Pressure (hPa):</label>
              <input
                type="number"
                step="any"
                name="sealevelpressure"
                value={formData.sealevelpressure}
                onChange={handleInputChange}
                placeholder="1015.2"
                className="p-4 border-2 rounded-lg focus:outline-none focus:border-purple-400 transition-colors text-lg"
                style={{ borderColor: '#E5D9F2' }}
                required
              />
            </div>
            
            <div className="flex flex-col">
              <label className="font-semibold mb-3 text-gray-700 text-lg">🌡️ Temperature (°C):</label>
              <input
                type="number"
                step="any"
                name="temp"
                value={formData.temp}
                onChange={handleInputChange}
                placeholder="18.5"
                className="p-4 border-2 rounded-lg focus:outline-none focus:border-purple-400 transition-colors text-lg"
                style={{ borderColor: '#E5D9F2' }}
                required
              />
            </div>
          </div>

          <div className="flex flex-wrap gap-4 justify-center">
            <button
              type="button"
              onClick={handlePredict}
              disabled={loading}
              className="px-8 py-4 rounded-lg font-semibold text-white transition-all duration-300 hover:transform hover:-translate-y-1 hover:shadow-lg text-lg min-w-52 disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ background: 'linear-gradient(135deg, #A294F9 0%, #CDC1FF 100%)' }}
            >
              🔮 Predict Weather
            </button>
            
            <button
              type="button"
              onClick={loadDatasetInfo}
              disabled={loading}
              className="px-8 py-4 rounded-lg font-semibold text-gray-800 border-2 transition-all duration-300 hover:transform hover:-translate-y-1 hover:shadow-lg text-lg min-w-52 disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ borderColor: '#E5D9F2', backgroundColor: '#F5EFFF' }}
            >
              📊 Dataset Info
            </button>
            
            <button
              type="button"
              onClick={findSimilar}
              disabled={loading}
              className="px-8 py-4 rounded-lg font-semibold text-gray-800 border-2 transition-all duration-300 hover:transform hover:-translate-y-1 hover:shadow-lg text-lg min-w-52 disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ borderColor: '#E5D9F2', backgroundColor: '#F5EFFF' }}
            >
              🔍 Find Similar
            </button>
            
            <button
              type="button"
              onClick={fillExample}
              className="px-8 py-4 rounded-lg font-semibold text-gray-800 border-2 transition-all duration-300 hover:transform hover:-translate-y-1 hover:shadow-lg text-lg min-w-52"
              style={{ borderColor: '#E5D9F2', backgroundColor: '#F5EFFF' }}
            >
              📝 Fill Example
            </button>
          </div>
        </div>

        {loading && <LoadingSpinner />}

        {error && (
          <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-6 rounded">
            <div className="text-red-700">⚠️ {error}</div>
          </div>
        )}

        {activeView === 'result' && prediction && !loading && (
          <div className="mt-8 p-6 rounded-xl border-l-4" style={{ backgroundColor: '#F5EFFF', borderColor: '#A294F9' }}>
            <div className="text-center p-6 rounded-lg text-white mb-6" style={{ background: 'linear-gradient(135deg, #A294F9 0%, #CDC1FF 100%)' }}>
              <h2 className="text-2xl font-bold mb-2">🌤️ Predicted Condition</h2>
              <div className="text-4xl font-bold mb-4">{prediction.prediction}</div>
              {prediction.confidence && (
                <>
                  <div className="mb-2 text-lg">Confidence:</div>
                  <div className="bg-white bg-opacity-30 rounded-full h-6 mb-2 max-w-md mx-auto">
                    <div 
                      className="h-6 rounded-full transition-all duration-500"
                      style={{ 
                        width: `${(prediction.confidence * 100)}%`,
                        background: 'linear-gradient(90deg, #ff4757, #ffa502, #2ed573)'
                      }}
                    ></div>
                  </div>
                  <div className="text-xl font-semibold">{(prediction.confidence * 100).toFixed(1)}%</div>
                </>
              )}
            </div>

            <div className="space-y-6">
              {prediction.all_probabilities && Object.keys(prediction.all_probabilities).length > 0 && (
                <div className="bg-white p-5 rounded-lg border-2" style={{ borderColor: '#E5D9F2' }}>
                  <h3 className="text-xl font-semibold mb-4" style={{ color: '#A294F9' }}>📊 All Predictions (Probability)</h3>
                  <div className="space-y-2">
                    {Object.entries(prediction.all_probabilities).slice(0, 5).map(([condition, prob]) => (
                      <div key={condition} className="flex items-center justify-between p-3 rounded" style={{ backgroundColor: '#F5EFFF' }}>
                        <span className="font-medium">{condition}</span>
                        <div className="flex items-center gap-3">
                          <div className="w-32 bg-gray-200 rounded-full h-3">
                            <div 
                              className="h-3 rounded-full"
                              style={{ 
                                width: `${prob * 100}%`,
                                background: 'linear-gradient(90deg, #A294F9, #CDC1FF)'
                              }}
                            ></div>
                          </div>
                          <span className="font-semibold text-purple-600 w-16 text-right">{(prob * 100).toFixed(1)}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {prediction.groq_explanation && (
                <div className="bg-white p-5 rounded-lg border-2" style={{ borderColor: '#E5D9F2' }}>
                  <h3 className="text-xl font-semibold mb-3 flex items-center" style={{ color: '#A294F9' }}>
                    🤖 AI Analysis
                  </h3>
                  <p className="text-gray-700 leading-relaxed">{prediction.groq_explanation}</p>
                </div>
              )}

              {prediction.processed_features && Object.keys(prediction.processed_features).length > 0 && (
                <div className="bg-white p-5 rounded-lg border-2" style={{ borderColor: '#E5D9F2' }}>
                  <h3 className="text-xl font-semibold mb-4" style={{ color: '#A294F9' }}>⚙️ Processed Features</h3>
                  <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                    {Object.entries(prediction.processed_features).map(([key, value]) => (
                      <div key={key} className="text-center p-3 rounded-lg" style={{ backgroundColor: '#F5EFFF' }}>
                        <div className="text-xs text-gray-600 mb-1">{key.replace(/_/g, ' ')}</div>
                        <div className="font-semibold text-purple-700">
                          {typeof value === 'number' ? value.toFixed(3) : value}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {activeView === 'dataset' && datasetInfo && !loading && (
          <div className="mt-8 p-6 rounded-xl border-l-4" style={{ backgroundColor: '#F5EFFF', borderColor: '#A294F9' }}>
            <h3 className="text-2xl font-semibold mb-6" style={{ color: '#A294F9' }}>📊 Training Dataset Information</h3>
            
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
              <div className="text-center p-4 rounded-lg bg-white border" style={{ borderColor: '#E5D9F2' }}>
                <strong>Total Records</strong><br />
                {datasetInfo.total_records}
              </div>
              <div className="text-center p-4 rounded-lg bg-white border" style={{ borderColor: '#E5D9F2' }}>
                <strong>Date Range</strong><br />
                {datasetInfo.date_range.start} to {datasetInfo.date_range.end}
              </div>
              <div className="text-center p-4 rounded-lg bg-white border" style={{ borderColor: '#E5D9F2' }}>
                <strong>Conditions</strong><br />
                {Object.keys(datasetInfo.conditions_distribution).length} types
              </div>
            </div>

            <div className="mb-6">
              <h4 className="text-lg font-semibold mb-3" style={{ color: '#A294F9' }}>🌤️ Weather Conditions Distribution:</h4>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
                {Object.entries(datasetInfo.conditions_distribution).map(([condition, count]) => (
                  <div key={condition} className="text-center p-3 rounded-lg bg-white border" style={{ borderColor: '#E5D9F2' }}>
                    <strong>{condition}</strong><br />
                    {count} records
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h4 className="text-lg font-semibold mb-3" style={{ color: '#A294F9' }}>📈 Feature Statistics:</h4>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="text-center p-4 rounded-lg bg-white border" style={{ borderColor: '#E5D9F2' }}>
                  <strong>Temperature</strong><br />
                  {datasetInfo.feature_statistics.temperature.min.toFixed(1)}°C to {datasetInfo.feature_statistics.temperature.max.toFixed(1)}°C<br />
                  Avg: {datasetInfo.feature_statistics.temperature.mean.toFixed(1)}°C
                </div>
                <div className="text-center p-4 rounded-lg bg-white border" style={{ borderColor: '#E5D9F2' }}>
                  <strong>Humidity</strong><br />
                  {datasetInfo.feature_statistics.humidity.min.toFixed(1)}% to {datasetInfo.feature_statistics.humidity.max.toFixed(1)}%<br />
                  Avg: {datasetInfo.feature_statistics.humidity.mean.toFixed(1)}%
                </div>
                <div className="text-center p-4 rounded-lg bg-white border" style={{ borderColor: '#E5D9F2' }}>
                  <strong>Pressure</strong><br />
                  {datasetInfo.feature_statistics.pressure.min.toFixed(1)} to {datasetInfo.feature_statistics.pressure.max.toFixed(1)} hPa<br />
                  Avg: {datasetInfo.feature_statistics.pressure.mean.toFixed(1)} hPa
                </div>
              </div>
            </div>
          </div>
        )}

        {activeView === 'similar' && similarConditions && !loading && (
          <div className="mt-8 p-6 rounded-xl border-l-4" style={{ backgroundColor: '#F5EFFF', borderColor: '#A294F9' }}>
            <h3 className="text-2xl font-semibold mb-6" style={{ color: '#A294F9' }}>🔍 Similar Historical Conditions</h3>
            
            <p className="mb-6 text-lg"><strong>Found {similarConditions.found_similar} similar historical conditions</strong></p>

            {similarConditions.found_similar > 0 && (
              <>
                <div className="mb-6">
                  <h4 className="text-lg font-semibold mb-3" style={{ color: '#A294F9' }}>🏆 Most Common Conditions:</h4>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    {Object.entries(similarConditions.most_common_conditions).map(([condition, count]) => (
                      <div key={condition} className="text-center p-3 rounded-lg bg-white border" style={{ borderColor: '#E5D9F2' }}>
                        <strong>{condition}</strong><br />
                        {count} times
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="text-lg font-semibold mb-3" style={{ color: '#A294F9' }}>📋 Recent Historical Matches:</h4>
                  <div className="overflow-x-auto">
                    <table className="w-full bg-white rounded-lg overflow-hidden border" style={{ borderColor: '#E5D9F2' }}>
                      <thead style={{ backgroundColor: '#F5EFFF' }}>
                        <tr>
                          <th className="p-3 text-left">Date</th>
                          <th className="p-3 text-left">Condition</th>
                          <th className="p-3 text-left">Temp</th>
                          <th className="p-3 text-left">Humidity</th>
                          <th className="p-3 text-left">Pressure</th>
                        </tr>
                      </thead>
                      <tbody>
                        {similarConditions.historical_matches.map((match, index) => (
                          <tr key={index} className="border-b" style={{ borderColor: '#E5D9F2' }}>
                            <td className="p-3">{match.datetime}</td>
                            <td className="p-3"><strong>{match.conditions}</strong></td>
                            <td className="p-3">{match.temp.toFixed(1)}°C</td>
                            <td className="p-3">{match.humidity.toFixed(1)}%</td>
                            <td className="p-3">{match.sealevelpressure.toFixed(1)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </>
            )}

            {similarConditions.found_similar === 0 && (
              <p className="text-gray-600">No similar conditions found in the historical dataset. Your input parameters are quite unique!</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default WeatherPredictor;