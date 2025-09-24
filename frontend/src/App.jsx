import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import './App.css'

// Import page components
import HomePage from './pages/HomePage'
import AboutUs from './pages/AboutUs'
import ContactUs from './pages/ContactUs'
import FaqPage from './pages/FaqPage'
import TermsAndConditions from './pages/TermsAndConditions'
import WeatherPredictor from './pages/WeatherPredictor'
import Login from './pages/Login'
import Chat from './pages/Chat'
import Dashboard from './pages/Dashboard'
import AdminDashboard from './pages/admin/AdminDashboard'

// Import layout components
import Header from './components/Header'
import Footer from './components/Footer'

// Import context providers
import { AuthProvider } from './contexts/AuthContext'

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App min-h-screen flex flex-col">
          <Routes>
            {/* Login route - no header/footer */}
            <Route path="/login" element={<Login />} />
            
            {/* Routes with header and footer layout */}
            <Route path="*" element={
              <>
                <Header />
                <main className="flex-1">
                  <Routes>
                    {/* Default route - redirect to home */}
                    <Route path="/" element={<Navigate to="/home" replace />} />
                    
                    {/* Main routes */}
                    <Route path="/home" element={<HomePage />} />
                    <Route path="/about" element={<AboutUs />} />
                    <Route path="/contact" element={<ContactUs />} />
                    <Route path="/faq" element={<FaqPage />} />
                    <Route path="/terms" element={<TermsAndConditions />} />
                    <Route path="/weather-predictor" element={<WeatherPredictor />} />
                    
                    {/* Dashboard routes */}
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/chat" element={<Chat />} />
                    
                    {/* Admin routes */}
                    <Route path="/admin/dashboard" element={<AdminDashboard />} />
                    
                    {/* Catch all route - redirect to home */}
                    <Route path="*" element={<Navigate to="/home" replace />} />
                  </Routes>
                </main>
                <Footer />
              </>
            } />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  )
}

export default App
