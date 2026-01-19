/**
 * Stats Component - Display call statistics and metrics
 * Part of AI Answering Service Dashboard
 * Austin Kidwell | ASR Inc / Intellegix
 */

import React from 'react';

const Stats = ({ stats }) => {
  if (!stats) return null;

  // Calculate additional metrics
  const completionRate = stats.total_calls > 0
    ? Math.round((stats.completed_calls / stats.total_calls) * 100)
    : 0;

  const formatPhoneNumber = (phone) => {
    if (!phone) return 'Unknown';
    const cleaned = phone.replace(/^\+1/, '');
    if (cleaned.length === 10) {
      return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
    }
    return phone;
  };

  const formatTime = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit'
    });
  };

  return (
    <div className="stats-dashboard">
      <div className="stats-header">
        <h2>Call Analytics</h2>
        <div className="stats-updated">
          Last updated: {new Date().toLocaleTimeString()}
        </div>
      </div>

      <div className="stats-grid">
        {/* Primary Metrics */}
        <div className="stat-card primary">
          <div className="stat-icon">📞</div>
          <div className="stat-content">
            <div className="stat-number">{stats.total_calls}</div>
            <div className="stat-label">Total Calls</div>
          </div>
        </div>

        <div className="stat-card success">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <div className="stat-number">{stats.completed_calls}</div>
            <div className="stat-label">Completed</div>
            <div className="stat-meta">{completionRate}% success rate</div>
          </div>
        </div>

        <div className="stat-card info">
          <div className="stat-icon">📅</div>
          <div className="stat-content">
            <div className="stat-number">{stats.calls_today}</div>
            <div className="stat-label">Today</div>
          </div>
        </div>

        <div className="stat-card warning">
          <div className="stat-icon">⏱️</div>
          <div className="stat-content">
            <div className="stat-number">{stats.avg_duration_formatted || '0m 0s'}</div>
            <div className="stat-label">Avg Duration</div>
            <div className="stat-meta">{stats.avg_duration_seconds} seconds</div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      {stats.recent_activity && stats.recent_activity.length > 0 && (
        <div className="recent-activity">
          <div className="activity-header">
            <h3>Recent Activity</h3>
            <span className="activity-count">
              Last {stats.recent_activity.length} calls
            </span>
          </div>

          <div className="activity-list">
            {stats.recent_activity.map((call, index) => (
              <div key={call.id} className="activity-item">
                <div className="activity-indicator">
                  <div className={`activity-dot ${call.call_status}`}></div>
                </div>

                <div className="activity-content">
                  <div className="activity-main">
                    <span className="activity-phone">
                      {formatPhoneNumber(call.caller_phone)}
                    </span>
                    {call.caller_intent && (
                      <span className="activity-intent">
                        • {call.caller_intent.substring(0, 50)}
                        {call.caller_intent.length > 50 ? '...' : ''}
                      </span>
                    )}
                  </div>

                  <div className="activity-meta">
                    <span className="activity-time">
                      {formatTime(call.created_at)}
                    </span>
                    {call.call_duration > 0 && (
                      <span className="activity-duration">
                        • {Math.floor(call.call_duration / 60)}m {call.call_duration % 60}s
                      </span>
                    )}
                    <span className={`activity-status ${call.call_status}`}>
                      • {call.call_status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Performance Insights */}
      <div className="performance-insights">
        <h3>Insights</h3>
        <div className="insights-grid">
          <div className="insight-item">
            <div className="insight-metric">
              {completionRate >= 95 ? '🟢' : completionRate >= 85 ? '🟡' : '🔴'}
            </div>
            <div className="insight-content">
              <div className="insight-title">Call Success Rate</div>
              <div className="insight-description">
                {completionRate >= 95
                  ? 'Excellent performance! Calls are completing successfully.'
                  : completionRate >= 85
                  ? 'Good performance with room for improvement.'
                  : 'Some calls may need attention or troubleshooting.'
                }
              </div>
            </div>
          </div>

          <div className="insight-item">
            <div className="insight-metric">
              {stats.avg_duration_seconds >= 60 ? '💬' : stats.avg_duration_seconds >= 30 ? '⚡' : '⏰'}
            </div>
            <div className="insight-content">
              <div className="insight-title">Call Duration</div>
              <div className="insight-description">
                {stats.avg_duration_seconds >= 120
                  ? 'Detailed conversations - good engagement!'
                  : stats.avg_duration_seconds >= 60
                  ? 'Moderate conversation length - efficient handling.'
                  : stats.avg_duration_seconds >= 30
                  ? 'Quick calls - possibly simple inquiries.'
                  : 'Very brief calls - may indicate connection issues.'
                }
              </div>
            </div>
          </div>

          <div className="insight-item">
            <div className="insight-metric">
              {stats.calls_today >= 5 ? '📈' : stats.calls_today >= 2 ? '📊' : '📉'}
            </div>
            <div className="insight-content">
              <div className="insight-title">Daily Activity</div>
              <div className="insight-description">
                {stats.calls_today >= 5
                  ? 'High activity today - business is busy!'
                  : stats.calls_today >= 2
                  ? 'Moderate activity - steady flow of inquiries.'
                  : stats.calls_today >= 1
                  ? 'Light activity today.'
                  : 'No calls yet today - quiet period.'
                }
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Stats;