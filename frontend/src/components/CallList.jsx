/**
 * CallList Component - Display paginated call history
 * Part of AI Answering Service Dashboard
 * Austin Kidwell | ASR Inc / Intellegix
 */

import React from 'react';

const CallList = ({ calls, loading, pagination, onPageChange, onCallSelect }) => {

  // Format duration for display
  const formatDuration = (seconds) => {
    if (!seconds) return 'N/A';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  // Format phone number for display
  const formatPhoneNumber = (phone) => {
    if (!phone) return 'Unknown';

    // Remove +1 country code for US numbers
    const cleaned = phone.replace(/^\+1/, '');

    // Format as (XXX) XXX-XXXX
    if (cleaned.length === 10) {
      return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
    }

    return phone;
  };

  // Format date for display
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';

    const date = new Date(dateString);
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const callDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());

    if (callDate.getTime() === today.getTime()) {
      return `Today ${date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}`;
    }

    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (callDate.getTime() === yesterday.getTime()) {
      return `Yesterday ${date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}`;
    }

    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit'
    });
  };

  // Get call status styling
  const getStatusClass = (status) => {
    switch (status) {
      case 'completed': return 'status-completed';
      case 'in-progress': return 'status-progress';
      case 'failed': return 'status-failed';
      default: return 'status-unknown';
    }
  };

  // Truncate text for display
  const truncateText = (text, maxLength = 100) => {
    if (!text) return 'No summary available';
    return text.length > maxLength ? `${text.substring(0, maxLength)}...` : text;
  };

  // Pagination component
  const Pagination = () => {
    if (pagination.pages <= 1) return null;

    const pages = [];
    const currentPage = pagination.page;
    const totalPages = pagination.pages;

    // Always show first page
    pages.push(1);

    // Show pages around current page
    const start = Math.max(2, currentPage - 1);
    const end = Math.min(totalPages - 1, currentPage + 1);

    if (start > 2) pages.push('...');

    for (let i = start; i <= end; i++) {
      pages.push(i);
    }

    if (end < totalPages - 1) pages.push('...');

    // Always show last page if more than 1 page
    if (totalPages > 1) pages.push(totalPages);

    return (
      <div className="pagination">
        <button
          onClick={() => onPageChange(currentPage - 1)}
          disabled={currentPage <= 1}
          className="pagination-btn pagination-prev"
        >
          Previous
        </button>

        <div className="pagination-numbers">
          {pages.map((page, index) => (
            <button
              key={index}
              onClick={() => page !== '...' && onPageChange(page)}
              disabled={page === '...' || page === currentPage}
              className={`pagination-btn ${page === currentPage ? 'active' : ''} ${page === '...' ? 'ellipsis' : ''}`}
            >
              {page}
            </button>
          ))}
        </div>

        <button
          onClick={() => onPageChange(currentPage + 1)}
          disabled={currentPage >= totalPages}
          className="pagination-btn pagination-next"
        >
          Next
        </button>
      </div>
    );
  };

  // No calls message
  if (!loading && calls.length === 0) {
    return (
      <div className="call-list">
        <div className="call-list-header">
          <h2>Recent Calls</h2>
        </div>
        <div className="no-calls">
          <div className="no-calls-icon">📞</div>
          <h3>No calls found</h3>
          <p>Calls will appear here once your AI assistant starts receiving them.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="call-list">
      <div className="call-list-header">
        <h2>Recent Calls</h2>
        <div className="call-count">
          {loading ? (
            'Loading...'
          ) : (
            `Showing ${calls.length} of ${pagination.total} calls`
          )}
        </div>
      </div>

      <div className="call-list-content">
        {calls.map((call) => (
          <div
            key={call.id}
            className="call-item"
            onClick={() => onCallSelect(call.id)}
          >
            <div className="call-item-header">
              <div className="call-info">
                <div className="caller-phone">
                  {formatPhoneNumber(call.caller_phone)}
                </div>
                <div className="call-time">
                  {formatDate(call.created_at)}
                </div>
              </div>
              <div className="call-meta">
                <div className={`call-status ${getStatusClass(call.call_status)}`}>
                  {call.call_status}
                </div>
                <div className="call-duration">
                  {formatDuration(call.call_duration)}
                </div>
              </div>
            </div>

            {call.caller_intent && (
              <div className="call-intent">
                <strong>Purpose:</strong> {truncateText(call.caller_intent, 80)}
              </div>
            )}

            {call.summary && (
              <div className="call-summary">
                {truncateText(call.summary, 120)}
              </div>
            )}

            {call.action_items && call.action_items.length > 0 && (
              <div className="call-actions">
                <div className="action-count">
                  {call.action_items.length} action item{call.action_items.length !== 1 ? 's' : ''}
                </div>
              </div>
            )}

            <div className="call-item-footer">
              <button className="view-details-btn">
                View Details →
              </button>
            </div>
          </div>
        ))}

        {loading && (
          <div className="loading-more">
            <div className="loading-spinner small"></div>
            <span>Loading calls...</span>
          </div>
        )}
      </div>

      <Pagination />
    </div>
  );
};

export default CallList;