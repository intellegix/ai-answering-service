/**
 * AI Answering Service - Main React Dashboard
 * Call management dashboard with real-time updates
 * Austin Kidwell | ASR Inc / Intellegix
 */

import React, { useState, useEffect } from 'react';
import CallList from './components/CallList';
import CallDetail from './components/CallDetail';
import SearchBar from './components/SearchBar';
import Stats from './components/Stats';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

function App() {
  // State management
  const [currentView, setCurrentView] = useState('dashboard'); // dashboard, call-detail
  const [selectedCallId, setSelectedCallId] = useState(null);
  const [calls, setCalls] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchParams, setSearchParams] = useState({});
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 20,
    total: 0,
    pages: 0
  });

  // Fetch calls from API
  const fetchCalls = async (page = 1, search = {}) => {
    try {
      setLoading(true);
      setError(null);

      let url = `${API_BASE_URL}/api/calls?page=${page}&per_page=${pagination.per_page}`;
      let response;

      // Use search endpoint if search parameters provided
      if (Object.keys(search).length > 0) {
        response = await fetch(`${API_BASE_URL}/api/calls/search`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            ...search,
            limit: pagination.per_page,
            offset: (page - 1) * pagination.per_page
          }),
        });
      } else {
        response = await fetch(url);
      }

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      if (data.calls) {
        setCalls(data.calls);

        if (data.pagination) {
          setPagination(data.pagination);
        } else {
          // Handle search response pagination
          setPagination(prev => ({
            ...prev,
            page,
            total: data.total || 0,
            pages: Math.ceil((data.total || 0) / pagination.per_page)
          }));
        }
      }

    } catch (err) {
      console.error('Error fetching calls:', err);
      setError('Failed to load calls. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Fetch statistics
  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/stats`);
      if (!response.ok) {
        throw new Error('Failed to fetch stats');
      }
      const data = await response.json();
      setStats(data);
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

  // Initial data load
  useEffect(() => {
    fetchCalls();
    fetchStats();

    // Set up polling for real-time updates
    const interval = setInterval(() => {
      fetchCalls(pagination.page, searchParams);
      fetchStats();
    }, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, []);

  // Handle search
  const handleSearch = (params) => {
    setSearchParams(params);
    setPagination(prev => ({ ...prev, page: 1 }));
    fetchCalls(1, params);
  };

  // Handle pagination
  const handlePageChange = (newPage) => {
    fetchCalls(newPage, searchParams);
  };

  // View navigation
  const showCallDetail = (callId) => {
    setSelectedCallId(callId);
    setCurrentView('call-detail');
  };

  const showDashboard = () => {
    setCurrentView('dashboard');
    setSelectedCallId(null);
  };

  // Refresh data
  const handleRefresh = () => {
    fetchCalls(pagination.page, searchParams);
    fetchStats();
  };

  // Error display
  const ErrorMessage = ({ message, onRetry }) => (
    <div className="error-container">
      <div className="error-message">
        <h3>Error</h3>
        <p>{message}</p>
        <button onClick={onRetry} className="btn btn-primary">
          Try Again
        </button>
      </div>
    </div>
  );

  // Loading spinner
  const LoadingSpinner = () => (
    <div className="loading-container">
      <div className="loading-spinner"></div>
      <p>Loading calls...</p>
    </div>
  );

  return (
    <div className="App">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="header-title">
            <h1>
              {currentView === 'dashboard' ? (
                'AI Answering Service'
              ) : (
                <button onClick={showDashboard} className="back-button">
                  ← Back to Dashboard
                </button>
              )}
            </h1>
            <p>ASR Inc / Intellegix Call Management</p>
          </div>

          {currentView === 'dashboard' && (
            <div className="header-actions">
              <button onClick={handleRefresh} className="btn btn-secondary" disabled={loading}>
                {loading ? 'Refreshing...' : 'Refresh'}
              </button>
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {currentView === 'dashboard' && (
          <>
            {/* Statistics Dashboard */}
            {stats && <Stats stats={stats} />}

            {/* Search Bar */}
            <SearchBar onSearch={handleSearch} loading={loading} />

            {/* Error State */}
            {error && (
              <ErrorMessage
                message={error}
                onRetry={() => fetchCalls(pagination.page, searchParams)}
              />
            )}

            {/* Loading State */}
            {loading && calls.length === 0 && <LoadingSpinner />}

            {/* Calls List */}
            {!error && (
              <CallList
                calls={calls}
                loading={loading}
                pagination={pagination}
                onPageChange={handlePageChange}
                onCallSelect={showCallDetail}
              />
            )}
          </>
        )}

        {currentView === 'call-detail' && selectedCallId && (
          <CallDetail
            callId={selectedCallId}
            onBack={showDashboard}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <div className="footer-content">
          <p>&copy; 2024 ASR Inc / Intellegix | AI Answering Service</p>
          <div className="footer-links">
            <a href="#" onClick={(e) => { e.preventDefault(); handleRefresh(); }}>
              Refresh Data
            </a>
            <span className="separator">|</span>
            <a href="#" onClick={(e) => { e.preventDefault(); fetchStats(); }}>
              Update Stats
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;