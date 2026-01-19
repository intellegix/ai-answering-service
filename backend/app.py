"""
AI Answering Service - Main Flask Application
Austin Kidwell | ASR Inc / Intellegix
Backend API for managing AI-powered phone calls with Claude + Twilio
"""

import os
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json
import logging

from flask import Flask, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from pydantic import BaseModel, validator, ValidationError
from twilio.twiml import VoiceResponse
from twilio.rest import Client as TwilioClient
import anthropic
import openai
from sqlalchemy import text
from werkzeug.exceptions import BadRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["*"])  # Configure for production

# Database configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///ai_answering.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# API clients
anthropic_client = anthropic.Client(api_key=os.environ.get("ANTHROPIC_API_KEY"))
openai_client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
twilio_client = TwilioClient(
    os.environ.get("TWILIO_ACCOUNT_SID"),
    os.environ.get("TWILIO_AUTH_TOKEN")
)

# Result pattern for error handling
@dataclass
class Result:
    success: bool
    data: Any = None
    error: str = None

    @classmethod
    def ok(cls, data: Any = None) -> 'Result':
        return cls(success=True, data=data)

    @classmethod
    def err(cls, error: str) -> 'Result':
        return cls(success=False, error=error)

# Database Models
class CallLog(db.Model):
    __tablename__ = 'call_logs'

    id = db.Column(db.Integer, primary_key=True)
    caller_phone = db.Column(db.String(20), nullable=False, index=True)
    call_duration = db.Column(db.Integer, default=0)  # seconds
    transcript = db.Column(db.Text)
    summary = db.Column(db.Text)
    caller_intent = db.Column(db.String(500))
    action_items = db.Column(db.JSON)  # List of action items
    call_status = db.Column(db.String(50), default='in-progress')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert call log to dictionary for API responses."""
        return {
            'id': self.id,
            'caller_phone': self.caller_phone,
            'call_duration': self.call_duration,
            'transcript': self.transcript,
            'summary': self.summary,
            'caller_intent': self.caller_intent,
            'action_items': self.action_items or [],
            'call_status': self.call_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# Pydantic models for request validation
class CallSearchRequest(BaseModel):
    phone: Optional[str] = None
    intent: Optional[str] = None
    keywords: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    limit: int = 50
    offset: int = 0

    @validator('limit')
    def validate_limit(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Limit must be between 1 and 100')
        return v

class CallEndedWebhook(BaseModel):
    CallSid: str
    Duration: str
    CallStatus: str
    From: str
    To: str

# API Routes

@app.route('/health', methods=['GET'])
def health_check() -> Response:
    """Health check endpoint for monitoring."""
    try:
        # Test database connection
        db.session.execute(text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected',
            'version': '1.0.0'
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@app.route('/api/calls', methods=['GET'])
def get_calls() -> Response:
    """Retrieve paginated list of call logs."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)

        calls = CallLog.query.order_by(CallLog.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'calls': [call.to_dict() for call in calls.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': calls.total,
                'pages': calls.pages,
                'has_next': calls.has_next,
                'has_prev': calls.has_prev
            }
        })
    except Exception as e:
        logger.error(f"Error retrieving calls: {str(e)}")
        return jsonify({'error': 'Failed to retrieve calls'}), 500

@app.route('/api/calls/<int:call_id>', methods=['GET'])
def get_call_detail(call_id: int) -> Response:
    """Get specific call details."""
    try:
        call = CallLog.query.get_or_404(call_id)
        return jsonify(call.to_dict())
    except Exception as e:
        logger.error(f"Error retrieving call {call_id}: {str(e)}")
        return jsonify({'error': 'Call not found'}), 404

@app.route('/api/calls/search', methods=['POST'])
def search_calls() -> Response:
    """Search calls by phone, intent, or keywords."""
    try:
        # Validate request data
        try:
            search_data = CallSearchRequest(**request.json)
        except ValidationError as e:
            return jsonify({'error': 'Invalid search parameters', 'details': e.errors()}), 400

        query = CallLog.query

        # Apply filters
        if search_data.phone:
            query = query.filter(CallLog.caller_phone.ilike(f'%{search_data.phone}%'))

        if search_data.intent:
            query = query.filter(CallLog.caller_intent.ilike(f'%{search_data.intent}%'))

        if search_data.keywords:
            query = query.filter(
                db.or_(
                    CallLog.transcript.ilike(f'%{search_data.keywords}%'),
                    CallLog.summary.ilike(f'%{search_data.keywords}%')
                )
            )

        if search_data.start_date:
            start_date = datetime.fromisoformat(search_data.start_date.replace('Z', '+00:00'))
            query = query.filter(CallLog.created_at >= start_date)

        if search_data.end_date:
            end_date = datetime.fromisoformat(search_data.end_date.replace('Z', '+00:00'))
            query = query.filter(CallLog.created_at <= end_date)

        # Execute query with pagination
        calls = query.order_by(CallLog.created_at.desc()).offset(search_data.offset).limit(search_data.limit).all()
        total_count = query.count()

        return jsonify({
            'calls': [call.to_dict() for call in calls],
            'total': total_count,
            'offset': search_data.offset,
            'limit': search_data.limit
        })

    except Exception as e:
        logger.error(f"Error searching calls: {str(e)}")
        return jsonify({'error': 'Search failed'}), 500

@app.route('/api/stats', methods=['GET'])
def get_call_stats() -> Response:
    """Get call statistics."""
    try:
        total_calls = CallLog.query.count()
        completed_calls = CallLog.query.filter_by(call_status='completed').count()

        # Average call duration
        avg_duration_result = db.session.execute(
            text("SELECT AVG(call_duration) FROM call_logs WHERE call_status = 'completed'")
        ).fetchone()
        avg_duration = int(avg_duration_result[0] or 0)

        # Calls today
        today = datetime.utcnow().date()
        calls_today = CallLog.query.filter(
            db.func.date(CallLog.created_at) == today
        ).count()

        # Recent activity
        recent_calls = CallLog.query.order_by(CallLog.created_at.desc()).limit(5).all()

        return jsonify({
            'total_calls': total_calls,
            'completed_calls': completed_calls,
            'calls_today': calls_today,
            'avg_duration_seconds': avg_duration,
            'avg_duration_formatted': f"{avg_duration // 60}m {avg_duration % 60}s",
            'recent_activity': [call.to_dict() for call in recent_calls]
        })

    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': 'Failed to retrieve statistics'}), 500

# Twilio Webhook Routes

@app.route('/incoming-call', methods=['POST'])
def handle_incoming_call() -> Response:
    """Handle incoming Twilio call webhook."""
    try:
        # Extract call data
        call_sid = request.form.get('CallSid')
        from_number = request.form.get('From')
        to_number = request.form.get('To')

        logger.info(f"Incoming call from {from_number} (SID: {call_sid})")

        # Create call log entry
        call_log = CallLog(
            caller_phone=from_number,
            call_status='in-progress'
        )
        db.session.add(call_log)
        db.session.commit()

        # Generate TwiML response for ConversationRelay
        response = VoiceResponse()

        # Connect to our Node.js conversation relay service
        connect = response.connect()
        connect.stream(
            url=f"wss://{request.host}/ws/stream",
            track='both_tracks'
        )

        # Fallback message if stream fails
        response.say("I'm sorry, I'm having trouble connecting. Please try again later.")

        return Response(str(response), mimetype='application/xml')

    except Exception as e:
        logger.error(f"Error handling incoming call: {str(e)}")
        response = VoiceResponse()
        response.say("I'm sorry, I'm experiencing technical difficulties. Please call back later.")
        return Response(str(response), mimetype='application/xml')

@app.route('/call-ended', methods=['POST'])
def handle_call_ended() -> Response:
    """Handle call ended webhook from Twilio."""
    try:
        # Validate webhook data
        try:
            webhook_data = CallEndedWebhook(**request.form.to_dict())
        except ValidationError as e:
            logger.error(f"Invalid webhook data: {e.errors()}")
            return jsonify({'error': 'Invalid webhook data'}), 400

        # Find the call log
        call_log = CallLog.query.filter_by(caller_phone=webhook_data.From).order_by(
            CallLog.created_at.desc()
        ).first()

        if call_log:
            call_log.call_duration = int(webhook_data.Duration)
            call_log.call_status = 'completed'
            call_log.updated_at = datetime.utcnow()
            db.session.commit()

            logger.info(f"Call ended: {webhook_data.CallSid} - Duration: {webhook_data.Duration}s")
        else:
            logger.warning(f"Call log not found for ended call: {webhook_data.CallSid}")

        return jsonify({'status': 'success'})

    except Exception as e:
        logger.error(f"Error handling call ended: {str(e)}")
        return jsonify({'error': 'Failed to process call ended webhook'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error) -> Response:
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(405)
def method_not_allowed(error) -> Response:
    return jsonify({'error': 'Method not allowed'}), 405

@app.errorhandler(500)
def internal_error(error) -> Response:
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

# Initialize database
@app.before_first_request
def create_tables():
    """Create database tables on first request."""
    db.create_all()

if __name__ == '__main__':
    # Development server
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'

    app.run(host='0.0.0.0', port=port, debug=debug)