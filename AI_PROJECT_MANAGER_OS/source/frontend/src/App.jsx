import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './stores';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';

// Placeholder for ProjectDetail page
function ProjectDetail() {
  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <h1 className="text-2xl font-bold">Project Detail - Coming Soon</h1>
      <p className="mt-4 text-gray-600">This page will contain the chat interface, file explorer, and other project tools.</p>
    </div>
  );
}

function App() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  // Protected Route component
  const ProtectedRoute = ({ children }) => {
    if (!isAuthenticated) {
      return <Navigate to="/login" replace />;
    }
    return children;
  };

  return (
    <Routes>
      <Route 
        path="/login" 
        element={isAuthenticated ? <Navigate to="/" replace /> : <Login />} 
      />
      <Route 
        path="/" 
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/project/:id" 
        element={
          <ProtectedRoute>
            <ProjectDetail />
          </ProtectedRoute>
        } 
      />
    </Routes>
  );
}

export default App;
