/**
 * CallDetail Component - Display full call information and transcript
 * Part of AI Answering Service Dashboard
 * Austin Kidwell | ASR Inc / Intellegix
 */

import React, { useState, useEffect } from 'react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const CallDetail = ({ callId, onBack }) => {
  const [call, setCall] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch call details
  useEffect(() => {
    const fetchCallDetail = async () => {
      try {
        setLoading(true);
        setError(null);

        const response = await fetch(`${API_BASE_URL}/api/calls/${callId}`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        setCall(data);
      } catch (err) {
        console.error('Error fetching call details:', err);
        setError('Failed to load call details. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    if (callId) {
      fetchCallDetail();
    }
  }, [callId]);

  // Format helpers
  const formatPhoneNumber = (phone) => {
    if (!phone) return 'Unknown';
    const cleaned = phone.replace(/^\+1/, '');
    if (cleaned.length === 10) {
      return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
    }
    return phone;
  };

  const formatDuration = (seconds) => {
    if (!seconds) return '0m 0s';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const formatDateTime = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit'
    });
  };

  const getStatusBadge = (status) => {
    const statusClasses = {
      'completed': 'status-badge status-completed',
      'in-progress': 'status-badge status-progress',
      'failed': 'status-badge status-failed'
    };
    return statusClasses[status] || 'status-badge status-unknown';
  };

  // Parse transcript into conversation format
  const parseTranscript = (transcript) => {
    if (!transcript) return [];

    // Split by speaker labels if present
    const lines = transcript.split('\n').filter(line => line.trim());
    const conversation = [];

    lines.forEach(line => {
      const trimmed = line.trim();
      if (trimmed.startsWith('Caller:') || trimmed.startsWith('User:')) {
        conversation.push({
          speaker: 'Caller',
          message: trimmed.replace(/^(Caller:|User:)\s*/, '')
        });
      } else if (trimmed.startsWith('Assistant:') || trimmed.startsWith('AI:')) {
        conversation.push({
          speaker: 'Assistant',
          message: trimmed.replace(/^(Assistant:|AI:)\s*/, '')
        });
      } else if (trimmed) {
        // If no speaker label, assume it's a continuation or system message
        conversation.push({
          speaker: 'System',
          message: trimmed
        });
      }
    });

    return conversation;
  };

  // Copy text to clipboard
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      // Could add a toast notification here
      console.log('Copied to clipboard');
    }).catch(err => {
      console.error('Failed to copy:', err);
    });
  };

  if (loading) {
    return (
      <div className="call-detail loading">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading call details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="call-detail error">
        <div className="error-container">
          <h3>Error Loading Call</h3>
          <p>{error}</p>
          <div className="error-actions">
            <button onClick={onBack} className="btn btn-secondary">
              ← Back to Dashboard
            </button>
            <button onClick={() => window.location.reload()} className="btn btn-primary">
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!call) {
    return (
      <div className="call-detail not-found">
        <div className="not-found-container">
          <h3>Call Not Found</h3>
          <p>The requested call could not be found.</p>
          <button onClick={onBack} className="btn btn-primary">
            ← Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const conversationMessages = parseTranscript(call.transcript);

  return (
    <div className="call-detail">
      {/* Call Header */}
      <div className="call-detail-header">
        <div className="call-header-info">
          <h1>Call Details</h1>
          <div className="call-basic-info">
            <div className="caller-phone">
              <strong>{formatPhoneNumber(call.caller_phone)}</strong>
            </div>
            <div className={getStatusBadge(call.call_status)}>
              {call.call_status}
            </div>
          </div>
        </div>
      </div>

      {/* Call Metadata */}
      <div className="call-metadata">
        <div className="metadata-grid">
          <div className="metadata-item">
            <label>Call Time</label>
            <value>{formatDateTime(call.created_at)}</value>
          </div>
          <div className="metadata-item">
            <label>Duration</label>
            <value>{formatDuration(call.call_duration)}</value>
          </div>
          <div className="metadata-item">
            <label>Call ID</label>
            <value>#{call.id}</value>
          </div>
          <div className="metadata-item">
            <label>Status</label>
            <value className={call.call_status}>{call.call_status}</value>
          </div>
        </div>
      </div>

      {/* Caller Intent */}
      {call.caller_intent && (
        <div className="call-section">
          <div className="section-header">
            <h3>Purpose of Call</h3>
          </div>
          <div className="intent-content">
            <p>{call.caller_intent}</p>
          </div>
        </div>
      )}

      {/* Call Summary */}
      {call.summary && (
        <div className="call-section">
          <div className="section-header">
            <h3>Summary</h3>
            <button
              onClick={() => copyToClipboard(call.summary)}
              className="copy-btn"
              title="Copy summary"
            >
              📋
            </button>
          </div>
          <div className="summary-content">
            <p>{call.summary}</p>
          </div>
        </div>
      )}

      {/* Action Items */}
      {call.action_items && call.action_items.length > 0 && (
        <div className="call-section">
          <div className="section-header">
            <h3>Action Items</h3>
            <span className="item-count">
              {call.action_items.length} item{call.action_items.length !== 1 ? 's' : ''}
            </span>
          </div>
          <div className="action-items">
            {call.action_items.map((item, index) => (
              <div key={index} className="action-item">
                <div className="action-number">{index + 1}</div>
                <div className="action-text">{item}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Call Transcript */}
      {call.transcript && (
        <div className="call-section">
          <div className="section-header">
            <h3>Conversation Transcript</h3>
            <button
              onClick={() => copyToClipboard(call.transcript)}
              className="copy-btn"
              title="Copy transcript"
            >
              📋
            </button>
          </div>

          {conversationMessages.length > 0 ? (
            <div className="transcript-conversation">
              {conversationMessages.map((message, index) => (
                <div key={index} className={`message ${message.speaker.toLowerCase()}`}>
                  <div className="message-speaker">{message.speaker}:</div>
                  <div className="message-content">{message.message}</div>
                </div>
              ))}
            </div>
          ) : (
            <div className="transcript-raw">
              <pre>{call.transcript}</pre>
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="call-actions">
        <button onClick={onBack} className="btn btn-secondary">
          ← Back to Dashboard
        </button>
        <button
          onClick={() => copyToClipboard(JSON.stringify(call, null, 2))}
          className="btn btn-outline"
        >
          Export Call Data
        </button>
      </div>
    </div>
  );
};

export default CallDetail;