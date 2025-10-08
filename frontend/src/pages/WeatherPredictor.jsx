import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import FeatureGate from '../components/FeatureGate';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';

// ✅ Yup validation schema
const weatherSchema = yup.object().shape({
  datetime: yup
    .string()
    .trim()
    .required('Please enter a date.')
    .matches(/^(0?[1-9]|1[0-2])\/(0?[1-9]|[12][0-9]|3[01])\/\d{4}$/, 'Invalid date format. Use MM/DD/YYYY.'),
  sunrise: yup
    .string()
    .trim()
    .required('Please enter sunrise time.')
    .matches(/^(0?[1-9]|1[0-2]):[0-5][0-9]:[0-5][0-9]\s?(AM|PM)$/i, 'Invalid time format. Use hh:mm:ss AM/PM.'),
  sunset: yup
    .string()
    .trim()
    .required('Please enter sunset time.')
    .matches(/^(0?[1-9]|1[0-2]):[0-5][0-9]:[0-5][0-9]\s?(AM|PM)$/i, 'Invalid time format. Use hh:mm:ss AM/PM.'),
  humidity: yup
    .number()
    .typeError('Humidity must be a number')
    .required('Please enter humidity.')
    .min(0, 'Humidity must be between 0 and 100%')
    .max(100, 'Humidity must be between 0 and 100%'),
  sealevelpressure: yup
    .number()
    .typeError('Pressure must be a number')
    .required('Please enter sea level pressure.')
    .min(800, 'Pressure must be between 800–1100 hPa')
    .max(1100, 'Pressure must be between 800–1100 hPa'),
  temp: yup
    .number()
    .typeError('Temperature must be a number')
    .required('Please enter temperature.')
    .min(-50, 'Temperature must be between -50°C and 60°C')
    .max(60, 'Temperature must be between -50°C and 60°C'),
});

const WeatherPredictor = () => {
  const [loading, setLoading] = useState(false);
  const [activeView, setActiveView] = useState('form');
  const [prediction, setPrediction] = useState(null);
  const [datasetInfo, setDatasetInfo] = useState(null);
  const [similarConditions, setSimilarConditions] = useState(null);
  const [error, setError] = useState('');
  const { tier } = useAuth();

  // ✅ React Hook Form setup
  const {
    register,
    handleSubmit,
    setValue,
    reset,
    formState: { errors },
  } = useForm({
    resolver: yupResolver(weatherSchema),
    mode: 'onChange',
  });

  const onSubmit = async (formData) => {
    setError('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      const data = await response.json();
      if (data.result) {
        setPrediction({
          prediction: data.result.replace('Predicted Weather Condition: ', ''),
          confidence: null,
          groq_explanation: '',
          dataset_stats: {},
          processed_features: {},
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

  const fillExample = () => {
    const example = {
      datetime: '3/15/2020',
      sunrise: '6:30:15 AM',
      sunset: '6:45:20 PM',
      humidity: '68',
      sealevelpressure: '1015.2',
      temp: '18.5',
    };
    Object.keys(example).forEach((key) => setValue(key, example[key]));
    reset(example);
  };

  const loadDatasetInfo = async () => {
    setLoading(true);
    setError('');
    try {
      await new Promise((resolve) => setTimeout(resolve, 1500));
      const mockInfo = {
        total_records: 1987,
        date_range: { start: '1997-01-01', end: '2024-12-31' },
        conditions_distribution: {
          Clear: 456,
          'Partly Cloudy': 423,
          Cloudy: 378,
          Rain: 298,
          Snow: 187,
          Fog: 145,
          Thunderstorm: 100,
        },
        feature_statistics: {
          temperature: { min: -15.2, max: 42.8, mean: 18.6 },
          humidity: { min: 12.5, max: 98.7, mean: 64.2 },
          pressure: { min: 985.3, max: 1045.7, mean: 1013.8 },
        },
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
    setLoading(true);
    setError('');
    try {
      await new Promise((resolve) => setTimeout(resolve, 1800));
      const mockSimilar = {
        found_similar: 23,
        most_common_conditions: {
          'Partly Cloudy': 12,
          Clear: 7,
          Cloudy: 4,
        },
        historical_matches: [
          { datetime: '2023-03-14', conditions: 'Partly Cloudy', temp: 18.3, humidity: 67.2, sealevelpressure: 1015.1 },
          { datetime: '2022-04-12', conditions: 'Clear', temp: 18.7, humidity: 68.5, sealevelpressure: 1014.9 },
          { datetime: '2021-05-08', conditions: 'Partly Cloudy', temp: 18.1, humidity: 67.8, sealevelpressure: 1015.4 },
        ],
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
        <h1 className="text-5xl font-bold text-center mb-10 text-gray-800">🌤 Enhanced Climate Predictor</h1>

        <form onSubmit={handleSubmit(onSubmit)} className="mb-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {[
              { name: 'datetime', label: '📅 Date (MM/DD/YYYY):', placeholder: '2/11/1997' },
              { name: 'sunrise', label: '🌅 Sunrise (hh:mm:ss AM/PM):', placeholder: '6:04:10 AM' },
              { name: 'sunset', label: '🌆 Sunset (hh:mm:ss AM/PM):', placeholder: '6:20:56 PM' },
              { name: 'humidity', label: '💧 Humidity (%):', placeholder: '75', type: 'number' },
              { name: 'sealevelpressure', label: '🌊 Sea Level Pressure (hPa):', placeholder: '1013.25', type: 'number' },
              { name: 'temp', label: '🌡️ Temperature (°C):', placeholder: '22.5', type: 'number' },
            ].map((field) => (
              <div key={field.name} className="flex flex-col">
                <label className="font-semibold mb-3 text-gray-700 text-lg">{field.label}</label>
                <input
                  type={field.type || 'text'}
                  {...register(field.name)}
                  placeholder={field.placeholder}
                  className="p-4 border-2 rounded-lg focus:outline-none focus:border-purple-400 transition-colors text-lg"
                  style={{ borderColor: '#E5D9F2' }}
                />
                {errors[field.name] && <p className="text-red-600 text-sm mt-2">{errors[field.name]?.message}</p>}
              </div>
            ))}
          </div>

          <div className="flex flex-wrap gap-4 justify-center">
            <button
              type="submit"
              className="px-8 py-4 rounded-lg font-semibold text-white transition-all duration-300 hover:transform hover:-translate-y-1 hover:shadow-lg text-lg min-w-52"
              style={{ background: 'linear-gradient(135deg, #A294F9 0%, #CDC1FF 100%)' }}
            >
              🔮 Predict Weather
            </button>
            <FeatureGate minTier="researcher" fallback={<button disabled className="px-8 py-4 rounded-lg font-semibold text-gray-400 border-2 text-lg min-w-52" style={{ borderColor: '#E5D9F2', backgroundColor: '#F5EFFF' }}>📊 Dataset Info (Locked)</button>}>
              <button type="button" onClick={loadDatasetInfo} className="px-8 py-4 rounded-lg font-semibold text-gray-800 border-2 transition-all duration-300 hover:transform hover:-translate-y-1 hover:shadow-lg text-lg min-w-52" style={{ borderColor: '#E5D9F2', backgroundColor: '#F5EFFF' }}>📊 Dataset Info</button>
            </FeatureGate>
            <FeatureGate minTier="professional" fallback={<button disabled className="px-8 py-4 rounded-lg font-semibold text-gray-400 border-2 text-lg min-w-52" style={{ borderColor: '#E5D9F2', backgroundColor: '#F5EFFF' }}>🔍 Find Similar (Locked)</button>}>
              <button type="button" onClick={findSimilar} className="px-8 py-4 rounded-lg font-semibold text-gray-800 border-2 transition-all duration-300 hover:transform hover:-translate-y-1 hover:shadow-lg text-lg min-w-52" style={{ borderColor: '#E5D9F2', backgroundColor: '#F5EFFF' }}>🔍 Find Similar</button>
            </FeatureGate>
            <button type="button" onClick={fillExample} className="px-8 py-4 rounded-lg font-semibold text-gray-800 border-2 transition-all duration-300 hover:transform hover:-translate-y-1 hover:shadow-lg text-lg min-w-52" style={{ borderColor: '#E5D9F2', backgroundColor: '#F5EFFF' }}>📝 Fill Example</button>
          </div>
        </form>

        {loading && <LoadingSpinner />}

        {error && (
          <div className="bg-red-50 border-l-4 border-red-400 p-4 mb-6 rounded">
            <div className="text-red-700">⚠️ {error}</div>
          </div>
        )}

        {activeView === 'result' && prediction && !loading && <div>{/* original result view */}</div>}
        {activeView === 'dataset' && datasetInfo && !loading && <div>{/* original dataset view */}</div>}
        {activeView === 'similar' && similarConditions && !loading && <div>{/* original similar view */}</div>}
      </div>
    </div>
  );
};

export default WeatherPredictor;
