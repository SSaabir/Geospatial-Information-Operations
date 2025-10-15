import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { useAuth } from '../contexts/AuthContext';

// Fix for default marker icons in React-Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom weather marker icons
const createWeatherIcon = (temp, condition) => {
  const color = temp > 30 ? '#ef4444' : temp > 25 ? '#f97316' : temp > 20 ? '#eab308' : '#3b82f6';
  
  return L.divIcon({
    html: `
      <div style="
        background: ${color};
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        border: 3px solid white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        font-size: 12px;
      ">
        ${Math.round(temp)}°
      </div>
    `,
    className: 'custom-weather-marker',
    iconSize: [40, 40],
    iconAnchor: [20, 20],
    popupAnchor: [0, -20],
  });
};

// Weather stations data (mock - replace with actual data)
const weatherStations = [
  {
    id: 1,
    name: 'Colombo Station',
    lat: 6.9271,
    lng: 79.8612,
    temperature: 28.5,
    humidity: 75,
    wind_speed: 12,
    conditions: 'Partly Cloudy',
  },
  {
    id: 2,
    name: 'Galle Station',
    lat: 6.0535,
    lng: 80.2210,
    temperature: 29.2,
    humidity: 80,
    wind_speed: 15,
    conditions: 'Sunny',
  },
  {
    id: 3,
    name: 'Kandy Station',
    lat: 7.2906,
    lng: 80.6337,
    temperature: 24.8,
    humidity: 68,
    wind_speed: 8,
    conditions: 'Clear',
  },
  {
    id: 4,
    name: 'Jaffna Station',
    lat: 9.6615,
    lng: 80.0255,
    temperature: 32.1,
    humidity: 65,
    wind_speed: 18,
    conditions: 'Hot',
  },
  {
    id: 5,
    name: 'Trincomalee Station',
    lat: 8.5874,
    lng: 81.2152,
    temperature: 30.5,
    humidity: 72,
    wind_speed: 20,
    conditions: 'Windy',
  },
];

const MapView = () => {
  const { user } = useAuth();
  const mapRef = useRef(null);
  const [stations, setStations] = useState(weatherStations);
  const [loading, setLoading] = useState(false);
  const [selectedStation, setSelectedStation] = useState(null);
  const [mapStyle, setMapStyle] = useState('standard');
  
  // Get user tier for feature access
  const getUserTier = () => {
    if (!user) return 'free';
    return user.tier || 'free';
  };
  
  const tier = getUserTier();

  // Fetch real-time weather data (if available)
  useEffect(() => {
    const fetchWeatherData = async () => {
      try {
        setLoading(true);
        // API call to get current weather data for all stations
        // const response = await apiCall('/api/weather/stations', 'GET');
        // setStations(response.data);
      } catch (error) {
        console.error('Error fetching weather data:', error);
      } finally {
        setLoading(false);
      }
    };

    // Uncomment when API is ready
    // fetchWeatherData();
    
    // Refresh every 5 minutes
    const interval = setInterval(() => {
      // fetchWeatherData();
    }, 5 * 60 * 1000);

    return () => clearInterval(interval);
  }, []);

  // Map tile layers based on tier
  const getTileLayer = () => {
    const layers = {
      standard: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      satellite: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
      terrain: 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
      dark: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    };

    return layers[mapStyle] || layers.standard;
  };

  // Tier-specific features
  const canUseAdvancedLayers = tier === 'professional';
  const canUseInteractive = tier === 'researcher' || tier === 'professional';

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Weather Map</h2>
            <p className="text-sm text-gray-600 mt-1">
              {tier === 'free' ? 'Basic map view' : tier === 'researcher' ? 'Interactive map with weather data' : 'Advanced map with multiple layers'}
            </p>
          </div>
          
          {/* Map Style Selector (Professional tier only) */}
          {canUseAdvancedLayers && (
            <div className="flex gap-2">
              <button
                onClick={() => setMapStyle('standard')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  mapStyle === 'standard' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Standard
              </button>
              <button
                onClick={() => setMapStyle('satellite')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  mapStyle === 'satellite' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Satellite
              </button>
              <button
                onClick={() => setMapStyle('terrain')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  mapStyle === 'terrain' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Terrain
              </button>
              <button
                onClick={() => setMapStyle('dark')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  mapStyle === 'dark' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Dark
              </button>
            </div>
          )}
          
          {/* Upgrade prompt for Free tier */}
          {tier === 'free' && (
            <div className="text-sm text-gray-600">
              <a href="/pricing" className="text-blue-600 hover:text-blue-700 font-medium">
                Upgrade to Researcher
              </a>
              {' '}for interactive features
            </div>
          )}
        </div>
      </div>

      {/* Map Container */}
      <div className="flex-1 relative" style={{ minHeight: '500px' }}>
        {loading && (
          <div className="absolute top-4 right-4 z-[1000] bg-white px-4 py-2 rounded-lg shadow-lg">
            <div className="flex items-center gap-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
              <span className="text-sm text-gray-700">Updating weather data...</span>
            </div>
          </div>
        )}

        <MapContainer
          key="map-instance"
          ref={mapRef}
          center={[7.8731, 80.7718]} // Center of Sri Lanka
          zoom={8}
          style={{ height: '100%', width: '100%', minHeight: '500px' }}
          className="h-full w-full"
          zoomControl={true}
          scrollWheelZoom={canUseInteractive}
          whenReady={() => {
            // Map is ready, prevent re-initialization
            if (mapRef.current) {
              mapRef.current._container._leaflet_id = null;
            }
          }}
        >
          <TileLayer
            url={getTileLayer()}
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />

          {/* Weather station markers */}
          {stations.map((station) => (
            <Marker
              key={station.id}
              position={[station.lat, station.lng]}
              icon={createWeatherIcon(station.temperature, station.conditions)}
              eventHandlers={{
                click: () => setSelectedStation(station),
              }}
            >
              <Popup>
                <div className="p-2 min-w-[200px]">
                  <h3 className="font-bold text-lg mb-2">{station.name}</h3>
                  <div className="space-y-1 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Temperature:</span>
                      <span className="font-semibold">{station.temperature}°C</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Humidity:</span>
                      <span className="font-semibold">{station.humidity}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Wind Speed:</span>
                      <span className="font-semibold">{station.wind_speed} km/h</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Conditions:</span>
                      <span className="font-semibold">{station.conditions}</span>
                    </div>
                  </div>
                  
                  {/* Forecast link for Researcher+ */}
                  {canUseInteractive && (
                    <button
                      className="mt-3 w-full bg-blue-600 text-white py-2 px-3 rounded text-sm hover:bg-blue-700 transition-colors"
                      onClick={() => {
                        // Navigate to forecast view for this station
                        console.log('View forecast for', station.name);
                      }}
                    >
                      View Forecast
                    </button>
                  )}
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>

        {/* Station Info Panel (Researcher+ only) */}
        {canUseInteractive && selectedStation && (
          <div className="absolute bottom-4 left-4 z-[1000] bg-white rounded-lg shadow-xl p-4 max-w-sm">
            <div className="flex justify-between items-start mb-3">
              <h3 className="font-bold text-lg">{selectedStation.name}</h3>
              <button
                onClick={() => setSelectedStation(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-blue-50 p-3 rounded-lg">
                <div className="text-xs text-gray-600 mb-1">Temperature</div>
                <div className="text-2xl font-bold text-blue-600">{selectedStation.temperature}°C</div>
              </div>
              <div className="bg-green-50 p-3 rounded-lg">
                <div className="text-xs text-gray-600 mb-1">Humidity</div>
                <div className="text-2xl font-bold text-green-600">{selectedStation.humidity}%</div>
              </div>
              <div className="bg-orange-50 p-3 rounded-lg">
                <div className="text-xs text-gray-600 mb-1">Wind Speed</div>
                <div className="text-2xl font-bold text-orange-600">{selectedStation.wind_speed} km/h</div>
              </div>
              <div className="bg-orange-50 p-3 rounded-lg">
                <div className="text-xs text-gray-600 mb-1">Conditions</div>
                <div className="text-sm font-bold text-orange-600">{selectedStation.conditions}</div>
              </div>
            </div>
          </div>
        )}

        {/* Legend */}
        <div className="absolute top-4 left-4 z-[1000] bg-white rounded-lg shadow-lg p-3">
          <h4 className="font-semibold text-sm mb-2">Temperature Scale</h4>
          <div className="space-y-1 text-xs">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-red-500"></div>
              <span>&gt; 30°C (Hot)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-orange-500"></div>
              <span>25-30°C (Warm)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-yellow-500"></div>
              <span>20-25°C (Mild)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded-full bg-blue-500"></div>
              <span>&lt; 20°C (Cool)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Tier limitation notice */}
      {tier === 'free' && (
        <div className="bg-blue-50 border-t border-blue-200 p-4">
          <div className="flex items-center gap-3">
            <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p className="text-sm font-medium text-gray-900">
                Unlock interactive features with Researcher tier
              </p>
              <p className="text-xs text-gray-600 mt-1">
                Get clickable markers, station info panels, forecast links, and more with an upgrade.
              </p>
            </div>
            <a
              href="/pricing"
              className="ml-auto px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors"
            >
              Upgrade Now
            </a>
          </div>
        </div>
      )}
    </div>
  );
};

export default MapView;
