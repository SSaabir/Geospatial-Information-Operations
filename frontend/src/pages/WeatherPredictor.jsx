import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import FeatureGate from '../components/FeatureGate';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';

// Yup validation schema
const schema = yup.object().shape({
  datetime: yup
    .string()
    .required('Date is required')
    .matches(/^(0?[1-9]|1[0-2])\/(0?[1-9]|[12][0-9]|3[01])\/\d{4}$/, 'Date must be in MM/DD/YYYY format'),
  sunrise: yup
    .string()
    .required('Sunrise time is required')
    .matches(/^([0]?[1-9]|1[0-2]):([0-5][0-9]):([0-5][0-9]) (AM|PM)$/, 'Sunrise must be in hh:mm:ss AM/PM format'),
  sunset: yup
    .string()
    .required('Sunset time is required')
    .matches(/^([0]?[1-9]|1[0-2]):([0-5][0-9]):([0-5][0-9]) (AM|PM)$/, 'Sunset must be in hh:mm:ss AM/PM format'),
  humidity: yup
    .number()
    .typeError('Humidity must be a number')
    .required('Humidity is required')
    .min(0, 'Humidity cannot be less than 0')
    .max(100, 'Humidity cannot be more than 100'),
  sealevelpressure: yup
    .number()
    .typeError('Sea Level Pressure must be a number')
    .required('Sea Level Pressure is required')
    .min(900, 'Pressure too low')
    .max(1100, 'Pressure too high'),
  temp: yup
    .number()
    .typeError('Temperature must be a number')
    .required('Temperature is required')
    .min(-50, 'Temperature too low')
    .max(60, 'Temperature too high')
});

const WeatherPredictor = () => {
  const { tier } = useAuth();
  const [loading, setLoading] = useState(false);
  const [activeView, setActiveView] = useState('form');
  const [prediction, setPrediction] = useState(null);
  const [datasetInfo, setDatasetInfo] = useState(null);
  const [similarConditions, setSimilarConditions] = useState(null);
  const [error, setError] = useState('');

  // react-hook-form
  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: yupResolver(schema),
    defaultValues: {
      datetime: '',
      sunrise: '',
      sunset: '',
      humidity: '',
      sealevelpressure: '',
      temp: ''
    }
  });

  const fillExample = () => {
    const exampleData = {
      datetime: '3/15/2020',
      sunrise: '6:30:15 AM',
      sunset: '6:45:20 PM',
      humidity: '68',
      sealevelpressure: '1015.2',
      temp: '18.5'
    };
    reset(exampleData);
  };

  const handlePredict = async (formData) => {
    setLoading(true);
    setError('');
    try {
      const response = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });
      const data = await response.json();
      if (data.result) {
        setPrediction({
          prediction: data.result.replace('Predicted Weather Condition: ', ''),
          confidence: null,
          groq_explanation: '',
          dataset_stats: {},
          processed_features: {}
        });
        setActiveView('result');
      } else {
        setError(data.error || 'Failed to get prediction. Please try again.');
      }
    } catch (err) {
      setError('Failed to get prediction. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const loadDatasetInfo = async () => {
    setLoading(true);
    setError('');
    
    try {
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

  const findSimilar = async (formData) => {
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
    <div className="min-h-screen w-full p-6" style={{ background: 'linear-gradient(135deg, #F5EFFF 0%, #E5D9F2 50%, #CDC1FF 100%)' }}>
      <div className="w-full max-w-6xl mx-auto bg-white rounded-2xl shadow-xl p-8">
        <h1 className="text-5xl font-bold text-center mb-10 text-gray-800">
          🌤 Enhanced Climate Predictor
        </h1>

        <div className="mb-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div className="flex flex-col">
              <label className="font-semibold mb-3 text-gray-700 text-lg">📅 Date (MM/DD/YYYY):</label>
              <input
                type="text"
                name="datetime"
                value={formData.datetime}
                onChange={handleInputChange}
                placeholder="2/11/1997"
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
                placeholder="6:04:10 AM"
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
                placeholder="6:20:56 PM"
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
                placeholder="75"
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
                placeholder="1013.25"
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
                placeholder="22.5"
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
              className="px-8 py-4 rounded-lg font-semibold text-white transition-all duration-300 hover:transform hover:-translate-y-1 hover:shadow-lg text-lg min-w-52"
              style={{ background: 'linear-gradient(135deg, #A294F9 0%, #CDC1FF 100%)' }}
            >
              🔮 Predict Weather
            </button>
            
            <FeatureGate minTier="researcher" fallback={<button disabled className="px-8 py-4 rounded-lg font-semibold text-gray-400 border-2 text-lg min-w-52" style={{ borderColor: '#E5D9F2', backgroundColor: '#F5EFFF' }}>📊 Dataset Info (Locked)</button>}>
              <button
                type="button"
                onClick={loadDatasetInfo}
                className="px-8 py-4 rounded-lg font-semibold text-gray-800 border-2 transition-all duration-300 hover:transform hover:-translate-y-1 hover:shadow-lg text-lg min-w-52"
                style={{ borderColor: '#E5D9F2', backgroundColor: '#F5EFFF' }}
              >
                📊 Dataset Info
              </button>
            </FeatureGate>
            
            <FeatureGate minTier="professional" fallback={<button disabled className="px-8 py-4 rounded-lg font-semibold text-gray-400 border-2 text-lg min-w-52" style={{ borderColor: '#E5D9F2', backgroundColor: '#F5EFFF' }}>🔍 Find Similar (Locked)</button>}>
              <button
                type="button"
                onClick={findSimilar}
                className="px-8 py-4 rounded-lg font-semibold text-gray-800 border-2 transition-all duration-300 hover:transform hover:-translate-y-1 hover:shadow-lg text-lg min-w-52"
                style={{ borderColor: '#E5D9F2', backgroundColor: '#F5EFFF' }}
              >
                🔍 Find Similar
              </button>
            </FeatureGate>
            
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
              <div className="text-3xl font-bold mb-4">{prediction.prediction}</div>
              <div className="mb-2">Confidence:</div>
              <div className="bg-gray-200 rounded-full h-5 mb-2">
                <div 
                  className="h-5 rounded-full transition-all duration-500"
                  style={{ 
                    width: `${(prediction.confidence * 100)}%`,
                    background: 'linear-gradient(90deg, #ff4757, #ffa502, #2ed573)'
                  }}
                ></div>
              </div>
              <div>{(prediction.confidence * 100).toFixed(1)}%</div>
            </div>

            <div className="space-y-6">
              <div className="bg-white p-4 rounded-lg border" style={{ borderColor: '#E5D9F2' }}>
                <h3 className="text-lg font-semibold mb-3" style={{ color: '#A294F9' }}>🤖 AI Analysis</h3>
                <p className="text-gray-700">{prediction.groq_explanation}</p>
              </div>

              <div className="bg-white p-4 rounded-lg border" style={{ borderColor: '#E5D9F2' }}>
                <h3 className="text-lg font-semibold mb-3" style={{ color: '#A294F9' }}>📊 Historical Data Context</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="text-center p-3 rounded-lg" style={{ backgroundColor: '#F5EFFF' }}>
                    <strong>Occurrences</strong><br />
                    {prediction.dataset_stats.total_occurrences} times ({prediction.dataset_stats.percentage_of_dataset.toFixed(1)}%)
                  </div>
                  <div className="text-center p-3 rounded-lg" style={{ backgroundColor: '#F5EFFF' }}>
                    <strong>Avg Temperature</strong><br />
                    {prediction.dataset_stats.avg_temp.toFixed(1)}°C
                  </div>
                  <div className="text-center p-3 rounded-lg" style={{ backgroundColor: '#F5EFFF' }}>
                    <strong>Avg Humidity</strong><br />
                    {prediction.dataset_stats.avg_humidity.toFixed(1)}%
                  </div>
                  <div className="text-center p-3 rounded-lg" style={{ backgroundColor: '#F5EFFF' }}>
                    <strong>Avg Pressure</strong><br />
                    {prediction.dataset_stats.avg_pressure.toFixed(1)} hPa
                  </div>
                </div>
              </div>

              <div className="bg-white p-4 rounded-lg border" style={{ borderColor: '#E5D9F2' }}>
                <h3 className="text-lg font-semibold mb-3" style={{ color: '#A294F9' }}>⚙️ Processed Features</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {Object.entries(prediction.processed_features).map(([key, value]) => (
                    <div key={key} className="text-center p-3 rounded-lg" style={{ backgroundColor: '#F5EFFF' }}>
                      <strong>{key}</strong><br />
                      {typeof value === 'number' ? value.toFixed(3) : value}
                    </div>
                  ))}
                </div>
              </div>
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