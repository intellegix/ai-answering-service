/**
 * SearchBar Component - Search and filter calls
 * Part of AI Answering Service Dashboard
 * Austin Kidwell | ASR Inc / Intellegix
 */

import React, { useState } from 'react';

const SearchBar = ({ onSearch, loading }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [searchParams, setSearchParams] = useState({
    phone: '',
    intent: '',
    keywords: '',
    start_date: '',
    end_date: ''
  });

  // Handle input changes
  const handleInputChange = (field, value) => {
    setSearchParams(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Handle search submission
  const handleSearch = (e) => {
    e.preventDefault();

    // Filter out empty values
    const params = {};
    Object.keys(searchParams).forEach(key => {
      const value = searchParams[key].trim();
      if (value) {
        params[key] = value;
      }
    });

    onSearch(params);
  };

  // Clear all search parameters
  const handleClear = () => {
    setSearchParams({
      phone: '',
      intent: '',
      keywords: '',
      start_date: '',
      end_date: ''
    });
    onSearch({});
  };

  // Get today's date in YYYY-MM-DD format for date inputs
  const getToday = () => {
    return new Date().toISOString().split('T')[0];
  };

  // Get date one week ago
  const getLastWeek = () => {
    const date = new Date();
    date.setDate(date.getDate() - 7);
    return date.toISOString().split('T')[0];
  };

  // Quick search presets
  const handleQuickSearch = (preset) => {
    const today = getToday();
    const lastWeek = getLastWeek();

    switch (preset) {
      case 'today':
        setSearchParams(prev => ({
          ...prev,
          start_date: today,
          end_date: today
        }));
        onSearch({
          start_date: today,
          end_date: today
        });
        break;
      case 'week':
        setSearchParams(prev => ({
          ...prev,
          start_date: lastWeek,
          end_date: today
        }));
        onSearch({
          start_date: lastWeek,
          end_date: today
        });
        break;
      case 'sales':
        setSearchParams(prev => ({
          ...prev,
          keywords: 'sales inquiry quote project'
        }));
        onSearch({
          keywords: 'sales inquiry quote project'
        });
        break;
      case 'support':
        setSearchParams(prev => ({
          ...prev,
          keywords: 'support help issue problem'
        }));
        onSearch({
          keywords: 'support help issue problem'
        });
        break;
      default:
        break;
    }
  };

  // Check if any search parameters are set
  const hasActiveSearch = Object.values(searchParams).some(value => value.trim() !== '');

  return (
    <div className="search-bar">
      <div className="search-bar-header">
        <div className="search-title">
          <h3>Search Calls</h3>
          {hasActiveSearch && (
            <span className="active-search-indicator">
              Active filters applied
            </span>
          )}
        </div>
        <button
          type="button"
          onClick={() => setIsExpanded(!isExpanded)}
          className="expand-toggle"
        >
          {isExpanded ? '▲ Less filters' : '▼ More filters'}
        </button>
      </div>

      <form onSubmit={handleSearch} className="search-form">
        {/* Quick Search Bar */}
        <div className="quick-search">
          <div className="search-input-group">
            <input
              type="text"
              placeholder="Search by phone, keywords, or purpose..."
              value={searchParams.keywords}
              onChange={(e) => handleInputChange('keywords', e.target.value)}
              className="search-input primary"
            />
            <button
              type="submit"
              disabled={loading}
              className="search-btn primary"
            >
              {loading ? '⏳' : '🔍'}
            </button>
          </div>
        </div>

        {/* Quick Filters */}
        <div className="quick-filters">
          <span className="quick-filters-label">Quick filters:</span>
          <button
            type="button"
            onClick={() => handleQuickSearch('today')}
            className="quick-filter-btn"
          >
            Today
          </button>
          <button
            type="button"
            onClick={() => handleQuickSearch('week')}
            className="quick-filter-btn"
          >
            This Week
          </button>
          <button
            type="button"
            onClick={() => handleQuickSearch('sales')}
            className="quick-filter-btn"
          >
            Sales Inquiries
          </button>
          <button
            type="button"
            onClick={() => handleQuickSearch('support')}
            className="quick-filter-btn"
          >
            Support Calls
          </button>
        </div>

        {/* Advanced Filters (Expandable) */}
        {isExpanded && (
          <div className="advanced-filters">
            <div className="filter-row">
              <div className="filter-group">
                <label htmlFor="phone-filter">Phone Number</label>
                <input
                  id="phone-filter"
                  type="text"
                  placeholder="(555) 123-4567"
                  value={searchParams.phone}
                  onChange={(e) => handleInputChange('phone', e.target.value)}
                  className="filter-input"
                />
              </div>

              <div className="filter-group">
                <label htmlFor="intent-filter">Call Purpose</label>
                <input
                  id="intent-filter"
                  type="text"
                  placeholder="e.g., sales, support, partnership"
                  value={searchParams.intent}
                  onChange={(e) => handleInputChange('intent', e.target.value)}
                  className="filter-input"
                />
              </div>
            </div>

            <div className="filter-row">
              <div className="filter-group">
                <label htmlFor="start-date">From Date</label>
                <input
                  id="start-date"
                  type="date"
                  value={searchParams.start_date}
                  onChange={(e) => handleInputChange('start_date', e.target.value)}
                  max={getToday()}
                  className="filter-input"
                />
              </div>

              <div className="filter-group">
                <label htmlFor="end-date">To Date</label>
                <input
                  id="end-date"
                  type="date"
                  value={searchParams.end_date}
                  onChange={(e) => handleInputChange('end_date', e.target.value)}
                  max={getToday()}
                  className="filter-input"
                />
              </div>
            </div>

            <div className="filter-actions">
              <button
                type="submit"
                disabled={loading}
                className="btn btn-primary"
              >
                {loading ? 'Searching...' : 'Apply Filters'}
              </button>
              <button
                type="button"
                onClick={handleClear}
                className="btn btn-secondary"
              >
                Clear All
              </button>
            </div>
          </div>
        )}
      </form>

      {/* Search Tips */}
      {isExpanded && (
        <div className="search-tips">
          <h4>Search Tips</h4>
          <ul>
            <li><strong>Keywords:</strong> Search across call transcripts and summaries</li>
            <li><strong>Phone:</strong> Partial phone number matching (555, 1234, etc.)</li>
            <li><strong>Purpose:</strong> Filter by identified call intent</li>
            <li><strong>Date Range:</strong> Find calls within specific time periods</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default SearchBar;