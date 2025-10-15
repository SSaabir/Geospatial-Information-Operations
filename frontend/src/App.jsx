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
import WorkflowChat from './pages/WorkflowChat'
import SecurityDashboard from './pages/SecurityDashboard'
import AIEthicsDashboard from './pages/AIEthicsDashboard'
import EnhancedAdminDashboard from './pages/admin/EnhancedAdminDashboard'
import Pricing from './components/Pricing'
import Analytics from './pages/Analytics'
import Settings from './pages/Settings'
import Checkout from './pages/Checkout'
import PaymentSuccess from './pages/PaymentSuccess'
import NotificationsPage from './pages/NotificationsPage'
import MapView from './components/MapView'
import News from './pages/News'

// Import layout components
import Header from './components/Header'
import Footer from './components/Footer'
import ProtectedRoute from './components/ProtectedRoute'

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
                    <Route path="/pricing" element={<Pricing />} />
                    <Route path="/checkout" element={<Checkout />} />
                    <Route path="/payment-success" element={<PaymentSuccess />} />
                    
                    {/* Map route - Public access with tier-based features */}
                    <Route path="/map" element={<MapView />} />
                    
                    {/* News route - Public access */}
                    <Route path="/news" element={<News />} />
                    
                    {/* Dashboard routes - Protected */}
                    <Route path="/dashboard" element={
                      <ProtectedRoute>
                        <Dashboard />
                      </ProtectedRoute>
                    } />
                    <Route path="/workflow" element={
                      <ProtectedRoute>
                        <WorkflowChat />
                      </ProtectedRoute>
                    } />

                    <Route path="/security" element={
                      <ProtectedRoute requireAdmin={true}>
                        <SecurityDashboard />
                      </ProtectedRoute>
                    } />
                    <Route path="/ai-ethics" element={
                      <ProtectedRoute requireAdmin={true}>
                        <AIEthicsDashboard />
                      </ProtectedRoute>
                    } />
                    <Route path="/analytics" element={
                      <ProtectedRoute requireAdmin={true}>
                        <Analytics />
                      </ProtectedRoute>
                    } />

                    <Route path="/chat" element={
                      <ProtectedRoute>
                        <Chat />
                      </ProtectedRoute>
                    } />

                    {/* ✅ Settings Page route - Protected */}
                    <Route path="/settings" element={
                      <ProtectedRoute>
                        <Settings />
                      </ProtectedRoute>
                    } />

                    {/* ✅ Notifications Page route - Protected */}
                    <Route path="/notifications" element={
                      <ProtectedRoute>
                        <NotificationsPage />
                      </ProtectedRoute>
                    } />

                                 
                    {/* Admin routes - Admin Only */}
                    <Route path="/admin/dashboard" element={
                      <ProtectedRoute requireAdmin={true}>
                        <EnhancedAdminDashboard />
                      </ProtectedRoute>
                    } />
                    
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
