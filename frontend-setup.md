# AI SECRETARY - REACT FRONTEND

## Complete React App Structure

```jsx
// src/App.jsx - Main application
import React, { useState, useEffect } from 'react';
import CallList from './components/CallList';
import CallDetail from './components/CallDetail';
import SearchBar from './components/SearchBar';
import Stats from './components/Stats';
import './App.css';

function App() {
  const [calls, setCalls] = useState([]);
  const [selectedCall, setSelectedCall] = useState(null);
  const [searchResults, setSearchResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);

  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

  useEffect(() => {
    fetchCalls();
    fetchStats();
  }, []);

  const fetchCalls = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/calls`);
      const data = await response.json();
      setCalls(data);
      if (data.length > 0) {
        setSelectedCall(data[0]);
      }
    } catch (error) {
      console.error('Error fetching calls:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/stats`);
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const handleSearch = async (query) => {
    try {
      const response = await fetch(`${API_BASE}/calls/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });
      const data = await response.json();
      setSearchResults(data);
      if (data.length > 0) {
        setSelectedCall(data[0]);
      }
    } catch (error) {
      console.error('Error searching calls:', error);
    }
  };

  const handleClearSearch = () => {
    setSearchResults(null);
    fetchCalls();
  };

  const displayCalls = searchResults !== null ? searchResults : calls;

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🤖 AI Secretary Dashboard</h1>
          <p>Manage and review all incoming calls</p>
        </div>
      </header>

      <main className="app-main">
        <aside className="sidebar">
          <SearchBar onSearch={handleSearch} onClear={handleClearSearch} />
          
          {stats && <Stats stats={stats} />}

          <div className="calls-section">
            <h2>Call History</h2>
            {loading ? (
              <p className="loading">Loading calls...</p>
            ) : displayCalls.length === 0 ? (
              <p className="no-calls">No calls found</p>
            ) : (
              <CallList
                calls={displayCalls}
                selectedCall={selectedCall}
                onSelectCall={setSelectedCall}
              />
            )}
          </div>
        </aside>

        <section className="main-content">
          {selectedCall ? (
            <CallDetail call={selectedCall} />
          ) : (
            <div className="no-selection">
              <p>Select a call to view details</p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
```

```jsx
// src/components/CallList.jsx
import React from 'react';
import { formatDate, formatDuration } from '../utils/formatting';

function CallList({ calls, selectedCall, onSelectCall }) {
  return (
    <div className="call-list">
      {calls.map(call => (
        <div
          key={call.id}
          className={`call-item ${selectedCall?.id === call.id ? 'active' : ''}`}
          onClick={() => onSelectCall(call)}
        >
          <div className="call-item-header">
            <span className="caller-phone">{call.caller_phone}</span>
            <span className="call-duration">{formatDuration(call.call_duration)}</span>
          </div>
          <div className="call-item-intent">
            {call.caller_intent || 'Pending analysis...'}
          </div>
          <div className="call-item-time">
            {formatDate(new Date(call.created_at))}
          </div>
        </div>
      ))}
    </div>
  );
}

export default CallList;
```

```jsx
// src/components/CallDetail.jsx
import React from 'react';
import { formatDate, formatDuration } from '../utils/formatting';

function CallDetail({ call }) {
  return (
    <div className="call-detail">
      <div className="detail-header">
        <div className="detail-title">
          <h2>Call from {call.caller_phone}</h2>
          <p className="detail-time">{formatDate(new Date(call.created_at))}</p>
        </div>
        <div className="detail-meta">
          <div className="meta-item">
            <span className="label">Duration</span>
            <span className="value">{formatDuration(call.call_duration)}</span>
          </div>
          <div className="meta-item">
            <span className="label">Intent</span>
            <span className="value">{call.caller_intent || '—'}</span>
          </div>
        </div>
      </div>

      {call.summary && (
        <div className="detail-section">
          <h3>Summary</h3>
          <div className="summary-text">
            {call.summary}
          </div>
        </div>
      )}

      {call.action_items && call.action_items.length > 0 && (
        <div className="detail-section">
          <h3>Action Items</h3>
          <ul className="action-items">
            {call.action_items.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      {call.transcript && (
        <div className="detail-section">
          <h3>Full Transcript</h3>
          <div className="transcript">
            {call.transcript.split('\n').map((line, idx) => (
              <p key={idx} className={line.includes('CALLER') ? 'caller-line' : 'assistant-line'}>
                {line}
              </p>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default CallDetail;
```

```jsx
// src/components/SearchBar.jsx
import React, { useState } from 'react';

function SearchBar({ onSearch, onClear }) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query);
    }
  };

  const handleClear = () => {
    setQuery('');
    onClear();
  };

  return (
    <div className="search-bar">
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Search by phone, intent, or keywords..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit">Search</button>
      </form>
      {query && (
        <button className="clear-btn" onClick={handleClear}>Clear</button>
      )}
    </div>
  );
}

export default SearchBar;
```

```jsx
// src/components/Stats.jsx
import React from 'react';

function Stats({ stats }) {
  return (
    <div className="stats">
      <h3>Statistics</h3>
      <div className="stat-item">
        <span className="stat-label">Total Calls</span>
        <span className="stat-value">{stats.total_calls}</span>
      </div>
      <div className="stat-item">
        <span className="stat-label">Total Duration</span>
        <span className="stat-value">{Math.round(stats.total_duration_minutes)}m</span>
      </div>
      <div className="stat-item">
        <span className="stat-label">Avg Duration</span>
        <span className="stat-value">{Math.round(stats.avg_duration)}s</span>
      </div>
    </div>
  );
}

export default Stats;
```

```javascript
// src/utils/formatting.js
export function formatDate(date) {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date);
}

export function formatDuration(seconds) {
  if (seconds < 60) return `${seconds}s`;
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${minutes}m ${secs}s`;
}
```

```css
/* src/App.css - Main styles */
:root {
  --primary: #2180d0;
  --primary-hover: #1a66b3;
  --bg-primary: #f5f5f5;
  --bg-secondary: #ffffff;
  --text-primary: #1a1a1a;
  --text-secondary: #666666;
  --border: #e0e0e0;
  --success: #4caf50;
  --error: #f44336;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  background: linear-gradient(135deg, var(--primary), #1a66b3);
  color: white;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-content h1 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.header-content p {
  font-size: 1rem;
  opacity: 0.9;
}

.app-main {
  display: flex;
  flex: 1;
  gap: 1rem;
  padding: 1rem;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.sidebar {
  width: 350px;
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
}

.main-content {
  flex: 1;
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
}

.no-selection {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-secondary);
  font-size: 1.1rem;
}

/* Search Bar */
.search-bar {
  margin-bottom: 2rem;
}

.search-bar form {
  display: flex;
  gap: 0.5rem;
}

.search-bar input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid var(--border);
  border-radius: 4px;
  font-size: 0.95rem;
}

.search-bar button,
.clear-btn {
  padding: 0.75rem 1.5rem;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s;
}

.search-bar button:hover,
.clear-btn:hover {
  background: var(--primary-hover);
}

.clear-btn {
  width: 100%;
  margin-top: 0.5rem;
  background: var(--text-secondary);
}

/* Stats */
.stats {
  background: var(--bg-primary);
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1.5rem;
}

.stats h3 {
  font-size: 0.9rem;
  text-transform: uppercase;
  color: var(--text-secondary);
  margin-bottom: 1rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--border);
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-label {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.stat-value {
  font-weight: 600;
  color: var(--primary);
}

/* Call List */
.calls-section h2 {
  font-size: 1.2rem;
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.call-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.call-item {
  padding: 1rem;
  background: var(--bg-primary);
  border: 1px solid var(--border);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.call-item:hover {
  background: #f0f0f0;
  border-color: var(--primary);
}

.call-item.active {
  background: #e3f2fd;
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(33, 128, 208, 0.1);
}

.call-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.caller-phone {
  font-weight: 600;
  color: var(--text-primary);
}

.call-duration {
  font-size: 0.85rem;
  color: var(--text-secondary);
  background: rgba(0, 0, 0, 0.05);
  padding: 0.25rem 0.75rem;
  border-radius: 3px;
}

.call-item-intent {
  font-size: 0.9rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.call-item-time {
  font-size: 0.8rem;
  color: #999;
}

.loading,
.no-calls {
  padding: 2rem;
  text-align: center;
  color: var(--text-secondary);
}

/* Call Detail */
.call-detail {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.detail-header {
  border-bottom: 2px solid var(--border);
  padding-bottom: 1.5rem;
}

.detail-title h2 {
  font-size: 1.8rem;
  margin-bottom: 0.5rem;
}

.detail-time {
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.detail-meta {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-top: 1.5rem;
}

.meta-item {
  display: flex;
  flex-direction: column;
}

.meta-item .label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  margin-bottom: 0.25rem;
}

.meta-item .value {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--primary);
}

/* Detail Sections */
.detail-section {
  padding: 1rem;
  background: var(--bg-primary);
  border-radius: 4px;
}

.detail-section h3 {
  font-size: 1.1rem;
  margin-bottom: 1rem;
  color: var(--text-primary);
}

.summary-text {
  line-height: 1.6;
  color: var(--text-primary);
  white-space: pre-wrap;
}

.action-items {
  list-style: none;
  padding: 0;
}

.action-items li {
  padding: 0.75rem;
  margin-bottom: 0.5rem;
  background: white;
  border-left: 3px solid var(--primary);
  border-radius: 2px;
}

.transcript {
  background: white;
  padding: 1rem;
  border-radius: 4px;
  max-height: 400px;
  overflow-y: auto;
  font-family: 'Courier New', monospace;
  font-size: 0.9rem;
}

.transcript p {
  margin-bottom: 0.75rem;
  line-height: 1.4;
}

.caller-line {
  color: var(--primary);
  font-weight: 500;
}

.assistant-line {
  color: var(--text-secondary);
}

/* Responsive */
@media (max-width: 768px) {
  .app-main {
    flex-direction: column;
  }

  .sidebar {
    width: 100%;
  }

  .detail-meta {
    grid-template-columns: 1fr;
  }

  .transcript {
    max-height: 250px;
  }
}
```

```json
// package.json
{
  "name": "ai-secretary-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": ["react-app"]
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version"]
  }
}
```

```
# .env.example
REACT_APP_API_URL=http://localhost:5000/api
```
