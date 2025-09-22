import React, { useState } from 'react';

const WeatherPredictionForm = () => {
  const [formData, setFormData] = useState({
    date: '',
    month: '',
    temperature: '',
    humidity: '',
    windSpeed: '',
    precipitation: '',
    sunriseTime: '',
    sunsetTime: ''
  });

  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    // Simulate API call for prediction
    setTimeout(() => {
      // Mock prediction logic based on your dataset patterns
      const temp = parseFloat(formData.temperature);
      const humidity = parseFloat(formData.humidity);
      const month = parseInt(formData.month);
      
      let predictedCondition = 'Clear';
      let confidence = 'Medium';
      
      // Simple prediction logic based on Colombo weather patterns
      if (humidity > 80 && temp > 28) {
        predictedCondition = 'Rain';
        confidence = 'High';
      } else if (humidity > 70 && month >= 4 && month <= 9) {
        predictedCondition = 'Partially cloudy with possible rain';
        confidence = 'Medium';
      } else if (temp > 32 && humidity < 60) {
        predictedCondition = 'Clear and sunny';
        confidence = 'High';
      } else {
        predictedCondition = 'Partly cloudy';
        confidence = 'Medium';
      }
      
      setPrediction({
        condition: predictedCondition,
        confidence: confidence,
        temperature: temp,
        humidity: humidity,
        sunrise: formData.sunriseTime,
        sunset: formData.sunsetTime
      });
      setLoading(false);
    }, 1500);
  };

  const resetForm = () => {
    setFormData({
      date: '',
      month: '',
      temperature: '',
      humidity: '',
      windSpeed: '',
      precipitation: '',
      sunriseTime: '',
      sunsetTime: ''
    });
    setPrediction(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#F5EFFF] to-[#E5D9F2] p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-[#A294F9] mb-2">
            Colombo Weather Predictor
          </h1>
          <p className="text-lg text-gray-600">
            Based on historical data from 1997-1998
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Prediction Form */}
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-[#CDC1FF]">
            <h2 className="text-2xl font-semibold text-[#A294F9] mb-6">
              Enter Weather Parameters
            </h2>
            
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Date
                  </label>
                  <input
                    type="number"
                    name="date"
                    value={formData.date}
                    onChange={handleInputChange}
                    min="1"
                    max="31"
                    placeholder="1-31"
                    className="w-full px-4 py-2 border border-[#CDC1FF] rounded-lg focus:ring-2 focus:ring-[#A294F9] focus:border-transparent"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Month
                  </label>
                  <select
                    name="month"
                    value={formData.month}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-[#CDC1FF] rounded-lg focus:ring-2 focus:ring-[#A294F9] focus:border-transparent"
                    required
                  >
                    <option value="">Select Month</option>
                    <option value="1">January</option>
                    <option value="2">February</option>
                    <option value="3">March</option>
                    <option value="4">April</option>
                    <option value="5">May</option>
                    <option value="6">June</option>
                    <option value="7">July</option>
                    <option value="8">August</option>
                    <option value="9">September</option>
                    <option value="10">October</option>
                    <option value="11">November</option>
                    <option value="12">December</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Temperature (°C)
                  </label>
                  <input
                    type="number"
                    name="temperature"
                    value={formData.temperature}
                    onChange={handleInputChange}
                    step="0.1"
                    placeholder="e.g., 28.5"
                    className="w-full px-4 py-2 border border-[#CDC1FF] rounded-lg focus:ring-2 focus:ring-[#A294F9] focus:border-transparent"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Humidity (%)
                  </label>
                  <input
                    type="number"
                    name="humidity"
                    value={formData.humidity}
                    onChange={handleInputChange}
                    min="0"
                    max="100"
                    placeholder="0-100"
                    className="w-full px-4 py-2 border border-[#CDC1FF] rounded-lg focus:ring-2 focus:ring-[#A294F9] focus:border-transparent"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Wind Speed (km/h)
                  </label>
                  <input
                    type="number"
                    name="windSpeed"
                    value={formData.windSpeed}
                    onChange={handleInputChange}
                    step="0.1"
                    placeholder="e.g., 15.3"
                    className="w-full px-4 py-2 border border-[#CDC1FF] rounded-lg focus:ring-2 focus:ring-[#A294F9] focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Precipitation (mm)
                  </label>
                  <input
                    type="number"
                    name="precipitation"
                    value={formData.precipitation}
                    onChange={handleInputChange}
                    step="0.1"
                    placeholder="e.g., 5.2"
                    className="w-full px-4 py-2 border border-[#CDC1FF] rounded-lg focus:ring-2 focus:ring-[#A294F9] focus:border-transparent"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Sunrise Time
                  </label>
                  <input
                    type="time"
                    name="sunriseTime"
                    value={formData.sunriseTime}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-[#CDC1FF] rounded-lg focus:ring-2 focus:ring-[#A294F9] focus:border-transparent"
                    placeholder="06:30"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Sunset Time
                  </label>
                  <input
                    type="time"
                    name="sunsetTime"
                    value={formData.sunsetTime}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-[#CDC1FF] rounded-lg focus:ring-2 focus:ring-[#A294F9] focus:border-transparent"
                    placeholder="18:30"
                  />
                </div>
              </div>

              <div className="flex gap-4 pt-4">
                <button
                  onClick={handleSubmit}
                  disabled={loading}
                  className="flex-1 bg-gradient-to-r from-[#A294F9] to-[#CDC1FF] text-white py-3 rounded-lg font-semibold hover:from-[#8B7DE9] hover:to-[#B8A9FF] transition-all disabled:opacity-50"
                >
                  {loading ? 'Predicting...' : 'Get Prediction'}
                </button>
                
                <button
                  onClick={resetForm}
                  className="px-6 py-3 border border-[#CDC1FF] text-[#A294F9] rounded-lg font-semibold hover:bg-[#F5EFFF] transition-all"
                >
                  Reset
                </button>
              </div>
            </div>
          </div>

          {/* Prediction Result */}
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-[#CDC1FF]">
            <h2 className="text-2xl font-semibold text-[#A294F9] mb-6">
              Weather Prediction
            </h2>
            
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#A294F9]"></div>
              </div>
            ) : prediction ? (
              <div className="space-y-6">
                <div className="text-center p-6 bg-gradient-to-br from-[#F5EFFF] to-[#E5D9F2] rounded-xl">
                  <div className="text-4xl mb-2">🌤️</div>
                  <h3 className="text-xl font-bold text-[#A294F9]">
                    {prediction.condition}
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Confidence: <span className="font-semibold">{prediction.confidence}</span>
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-[#F5EFFF] p-4 rounded-lg text-center">
                    <div className="text-2xl text-[#A294F9]">🌡️</div>
                    <div className="text-sm text-gray-600">Temperature</div>
                    <div className="font-bold text-lg">{prediction.temperature}°C</div>
                  </div>
                  
                  <div className="bg-[#F5EFFF] p-4 rounded-lg text-center">
                    <div className="text-2xl text-[#A294F9]">💧</div>
                    <div className="text-sm text-gray-600">Humidity</div>
                    <div className="font-bold text-lg">{prediction.humidity}%</div>
                  </div>
                </div>

                {(prediction.sunrise || prediction.sunset) && (
                  <div className="grid grid-cols-2 gap-4">
                    {prediction.sunrise && (
                      <div className="bg-[#FFF5F5] p-4 rounded-lg text-center border border-orange-200">
                        <div className="text-2xl text-orange-500">🌅</div>
                        <div className="text-sm text-gray-600">Sunrise</div>
                        <div className="font-bold text-lg">{prediction.sunrise}</div>
                      </div>
                    )}
                    
                    {prediction.sunset && (
                      <div className="bg-[#FFF5F5] p-4 rounded-lg text-center border border-orange-200">
                        <div className="text-2xl text-orange-500">🌇</div>
                        <div className="text-sm text-gray-600">Sunset</div>
                        <div className="font-bold text-lg">{prediction.sunset}</div>
                      </div>
                    )}
                  </div>
                )}

                <div className="bg-[#E5D9F2] p-4 rounded-lg">
                  <h4 className="font-semibold text-[#A294F9] mb-2">Recommendations:</h4>
                  <ul className="text-sm text-gray-700 space-y-1">
                    {prediction.condition.includes('Rain') && (
                      <li>• Carry an umbrella or raincoat</li>
                    )}
                    {prediction.temperature > 30 && (
                      <li>• Stay hydrated and wear light clothing</li>
                    )}
                    {prediction.humidity > 80 && (
                      <li>• Expect humid conditions</li>
                    )}
                    {prediction.sunrise && (
                      <li>• Plan morning activities after sunrise</li>
                    )}
                    <li>• Check updates for any changes</li>
                  </ul>
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500">
                <div className="text-6xl mb-4">⛅</div>
                <p>Enter weather parameters to get prediction</p>
              </div>
            )}
          </div>
        </div>

        {/* Dataset Info */}
        <div className="mt-8 bg-white rounded-2xl shadow-lg p-6 border border-[#CDC1FF]">
          <h3 className="text-lg font-semibold text-[#A294F9] mb-3">
            About the Dataset
          </h3>
          <p className="text-sm text-gray-600">
            This prediction model is based on historical weather data from Colombo, Sri Lanka 
            spanning 1997-1998. The dataset includes temperature, humidity, precipitation, 
            wind patterns, atmospheric conditions, and solar data specific to the region.
          </p>
        </div>
      </div>
    </div>
  );
};

export default WeatherPredictionForm;