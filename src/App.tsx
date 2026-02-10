import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Layout from './components/Layout/Layout';
import Login from './pages/Auth/Login';
import Dashboard from './pages/Dashboard/Dashboard';
import Cases from './pages/Cases/Cases';
import CaseDetail from './pages/Cases/CaseDetail';
import Judges from './pages/Judges/Judges';
import Calendar from './pages/Calendar/Calendar';
import Scheduling from './pages/Scheduling/Scheduling';
import Documents from './pages/Documents/Documents';
import MLPredictions from './pages/MLPredictions/MLPredictions';
import Courts from './pages/Courts/Courts';
import DelayJustification from './pages/DelayJustification/DelayJustification';
import './App.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }
  
  return user ? <>{children}</> : <Navigate to="/login" />;
};

const AppRoutes: React.FC = () => {
  const { user } = useAuth();
  
  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" /> : <Login />} />
      <Route path="/" element={
        <ProtectedRoute>
          <Layout>
            <Dashboard />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/cases" element={
        <ProtectedRoute>
          <Layout>
            <Cases />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/cases/:id" element={
        <ProtectedRoute>
          <Layout>
            <CaseDetail />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/judges" element={
        <ProtectedRoute>
          <Layout>
            <Judges />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/calendar" element={
        <ProtectedRoute>
          <Layout>
            <Calendar />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/scheduling" element={
        <ProtectedRoute>
          <Layout>
            <Scheduling />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/documents" element={
        <ProtectedRoute>
          <Layout>
            <Documents />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/ml-predictions" element={
        <ProtectedRoute>
          <Layout>
            <MLPredictions />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/courts" element={
        <ProtectedRoute>
          <Layout>
            <Courts />
          </Layout>
        </ProtectedRoute>
      } />
      <Route path="/delay-justification" element={
        <DelayJustification />
      } />
    </Routes>
  );
};

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <div className="App">
            <AppRoutes />
            <Toaster position="top-right" />
          </div>
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
};

export default App;