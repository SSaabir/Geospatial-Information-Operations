import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// Note: StrictMode disabled temporarily due to React-Leaflet compatibility issues
// StrictMode causes double mounting which breaks Leaflet map initialization
createRoot(document.getElementById('root')).render(
  <App />
)
