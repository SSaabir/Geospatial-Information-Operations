# 🌐 Frontend - React Application

> Modern React frontend with JWT authentication, protected routing, and geospatial analysis interface

## 📋 Overview

This is the frontend React application for the Geospatial Information Operations platform. It features a modern, responsive interface built with React 19, Vite, and Tailwind CSS, with complete JWT authentication integration.

## 🎯 Key Features

- **🔐 JWT Authentication**: Complete login/logout flow with token management
- **🛡️ Protected Routes**: Route guards for authenticated and admin-only pages
- **📱 Responsive Design**: Mobile-first design with Tailwind CSS
- **🎨 Modern UI**: Clean, intuitive interface with Lucide icons
- **🔄 Real-time Updates**: Dynamic content updates and state management
- **🌍 Geospatial Interface**: Interactive maps and data visualization

## 🛠️ Technology Stack

- **React 19.1** - Modern UI framework with latest features
- **Vite 7.1** - Fast build tool and development server
- **Tailwind CSS 4.1** - Utility-first CSS framework
- **React Router DOM** - Client-side routing with protected routes
- **Lucide React** - Beautiful, consistent icons
- **Axios** - HTTP client for API communication

## 📁 Project Structure

```
frontend/
├── public/                 # Static assets
│   └── vite.svg           # Vite logo
├── src/
│   ├── components/        # Reusable UI components
│   │   ├── ChatWindow.jsx # Chat interface component
│   │   ├── Footer.jsx     # Application footer
│   │   ├── Header.jsx     # Navigation header
│   │   └── ProtectedRoute.jsx # Route protection component
│   ├── contexts/          # React contexts
│   │   └── AuthContext.jsx # Authentication state management
│   ├── pages/             # Application pages
│   │   ├── AboutUs.jsx    # About page
│   │   ├── Chat.jsx       # Chat interface
│   │   ├── ContactUs.jsx  # Contact form
│   │   ├── Dashboard.jsx  # Main dashboard
│   │   ├── FaqPage.jsx    # FAQ page
│   │   ├── HomePage.jsx   # Landing page
│   │   ├── Login.jsx      # Authentication page
│   │   ├── TermsAndConditions.jsx # Terms page
│   │   ├── WeatherPredictor.jsx   # Weather prediction interface
│   │   └── admin/
│   │       └── AdminDashboard.jsx # Admin panel
│   ├── assets/            # Static assets and images
│   │   └── react.svg      # React logo
│   ├── App.jsx           # Main application component
│   ├── App.css           # Application styles
│   ├── index.css         # Global styles and Tailwind imports
│   └── main.jsx          # Application entry point
├── .env                   # Environment variables
├── package.json          # Dependencies and scripts
├── vite.config.js        # Vite configuration
├── tailwind.config.js    # Tailwind CSS configuration
├── postcss.config.js     # PostCSS configuration
└── eslint.config.js      # ESLint configuration
```

## 🚀 Quick Start

### Prerequisites
- **Node.js 16+** installed
- Backend server running on `http://localhost:8000`

### Setup & Run

```bash
# Install dependencies
npm install

# Create environment file
echo "VITE_API_BASE_URL=http://localhost:8000" > .env

# Start development server
npm run dev
```

➡️ **Frontend will run on:** http://localhost:5173

## 🔐 Authentication System

### AuthContext (`src/contexts/AuthContext.jsx`)

The application uses a centralized authentication context that manages:

- **User State**: Current user information and authentication status
- **JWT Tokens**: Access token storage and management
- **Login/Logout**: Authentication flow methods
- **API Integration**: Axios interceptors for automatic token attachment

```jsx
// Example usage
import { useAuth } from '../contexts/AuthContext';

function MyComponent() {
  const { user, login, logout, isAuthenticated } = useAuth();
  
  return (
    <div>
      {isAuthenticated ? (
        <p>Welcome, {user.username}!</p>
      ) : (
        <button onClick={() => login(credentials)}>Login</button>
      )}
    </div>
  );
}
```

### Protected Routes (`src/components/ProtectedRoute.jsx`)

Route protection component that:

- **Authentication Check**: Verifies user login status
- **Admin Check**: Restricts admin-only routes
- **Automatic Redirect**: Redirects to login if unauthorized

```jsx
// Protected route usage in App.jsx
<Route path="/dashboard" element={
  <ProtectedRoute>
    <Dashboard />
  </ProtectedRoute>
} />

<Route path="/admin" element={
  <ProtectedRoute requireAdmin={true}>
    <AdminDashboard />
  </ProtectedRoute>
} />
```

## 🎨 Components Overview

### Core Components

- **`Header.jsx`**: Navigation bar with authentication state
- **`Footer.jsx`**: Application footer with links
- **`ChatWindow.jsx`**: Real-time chat interface
- **`ProtectedRoute.jsx`**: Route authentication guard

### Page Components

- **`HomePage.jsx`**: Landing page with features overview
- **`Login.jsx`**: Authentication form with validation
- **`Dashboard.jsx`**: Main user dashboard
- **`WeatherPredictor.jsx`**: Weather analysis interface
- **`AdminDashboard.jsx`**: Admin panel for user management

## 🌐 API Integration

### Environment Configuration

```env
# .env file
VITE_API_BASE_URL=http://localhost:8000
```

### API Communication

The frontend communicates with the backend through:

- **Authentication Endpoints**: Login, logout, token refresh
- **Protected Endpoints**: Dashboard data, user management
- **Orchestrator API**: Geospatial analysis and reports

```javascript
// Example API call
const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/auth/login`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ username, password })
});
```

## 📱 Styling & UI

### Tailwind CSS

The application uses Tailwind CSS for styling with:

- **Responsive Design**: Mobile-first approach
- **Component Classes**: Reusable utility classes
- **Dark Mode Support**: Ready for dark theme implementation
- **Custom Configuration**: Extended colors and spacing

### Design System

- **Colors**: Professional blue and gray palette
- **Typography**: Clean, readable fonts
- **Spacing**: Consistent margin and padding
- **Components**: Reusable button, form, and card styles

## 🔧 Development

### Available Scripts

```bash
npm run dev         # Start development server
npm run build       # Build for production
npm run preview     # Preview production build
npm run lint        # Run ESLint
```

### Development Server

The Vite development server provides:

- **Hot Module Replacement**: Instant updates during development
- **Fast Builds**: Optimized build process
- **Modern Features**: ES modules and modern JavaScript support

### Code Quality

- **ESLint**: Code linting and formatting
- **Prettier**: Code formatting (recommended)
- **Component Structure**: Consistent component organization

## 🚀 Production Deployment

### Build Process

```bash
# Build for production
npm run build

# Output will be in dist/ directory
```

### Environment Variables

For production, update the environment variables:

```env
VITE_API_BASE_URL=https://your-api-domain.com
```

### Deployment Options

- **Static Hosting**: Vercel, Netlify, GitHub Pages
- **CDN**: CloudFlare, AWS CloudFront
- **Self-hosted**: Nginx, Apache

## 🧪 Testing

### Testing Strategy

- **Component Testing**: Test individual React components
- **Integration Testing**: Test component interactions
- **E2E Testing**: Test complete user workflows

### Recommended Tools

- **Vitest**: Unit and component testing
- **React Testing Library**: Component testing utilities
- **Cypress**: End-to-end testing

## 🔍 Troubleshooting

### Common Issues

1. **API Connection Errors**
   ```bash
   # Check if backend is running
   curl http://localhost:8000/health
   ```

2. **Authentication Issues**
   ```bash
   # Clear browser storage
   localStorage.clear();
   ```

3. **Build Errors**
   ```bash
   # Clean install
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **Environment Variables**
   ```bash
   # Verify .env file exists and contains
   VITE_API_BASE_URL=http://localhost:8000
   ```

## 📞 Support

For frontend-specific issues:

1. **Check browser console** for JavaScript errors
2. **Verify API endpoints** are accessible
3. **Check authentication tokens** in localStorage
4. **Review network requests** in browser dev tools

## 🎯 Next Steps

- **Add tests** for critical components
- **Implement error boundaries** for better error handling
- **Add loading states** for better user experience
- **Optimize performance** with code splitting
- **Add PWA features** for offline functionality

---

**Happy Frontend Development! 🚀**

*For backend setup, see `../services/README.md`*
