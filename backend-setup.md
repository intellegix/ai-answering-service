## BACKEND: Flask Server with Twilio + Claude Integration

```python
# app.py - Main Flask application
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
import json
import asyncio
from anthropic import Anthropic
import httpx

app = Flask(__name__)
CORS(app)

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db = SQLAlchemy(app)

# Initialize clients
claude_client = Anthropic()

class CallLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caller_phone = db.Column(db.String(20))
    call_duration = db.Column(db.Integer)  # seconds
    transcript = db.Column(db.Text)
    summary = db.Column(db.Text)
    caller_intent = db.Column(db.String(255))
    action_items = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'caller_phone': self.caller_phone,
            'call_duration': self.call_duration,
            'transcript': self.transcript,
            'summary': self.summary,
            'caller_intent': self.caller_intent,
            'action_items': self.action_items,
            'created_at': self.created_at.isoformat()
        }

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

@app.route('/incoming-call', methods=['POST'])
def incoming_call():
    """Twilio webhook - when call comes in"""
    from twilio.twiml.voice_response import VoiceResponse
    
    response = VoiceResponse()
    response.say("Connecting you to AI Assistant. Please hold while we set up your call.")
    
    # Twilio will connect to our WebSocket for ConversationRelay
    response.connect(
        action="/call-ended",
        timeout="30"
    ).stream(
        url=f"wss://{os.getenv('RENDER_HOST')}/ws/stream"
    )
    
    return str(response), 200, {'Content-Type': 'application/xml'}

@app.route('/ws/stream', methods=['GET'])
def websocket_stream():
    """WebSocket endpoint for Twilio ConversationRelay"""
    # This handles the bidirectional audio stream
    # Claude responds in real-time
    pass

@app.route('/call-ended', methods=['POST'])
def call_ended():
    """Webhook called when Twilio call ends"""
    call_sid = request.form.get('CallSid')
    call_duration = int(request.form.get('CallDuration', 0))
    caller_number = request.form.get('From')
    
    # The transcript and summary would be generated during the call
    # via Claude's conversation
    
    return jsonify({'status': 'call_logged'}), 200

@app.route('/api/calls', methods=['GET'])
def get_calls():
    """Get all call logs"""
    calls = CallLog.query.order_by(CallLog.created_at.desc()).all()
    return jsonify([call.to_dict() for call in calls])

@app.route('/api/calls/<int:call_id>', methods=['GET'])
def get_call(call_id):
    """Get specific call details"""
    call = CallLog.query.get_or_404(call_id)
    return jsonify(call.to_dict())

@app.route('/api/calls/search', methods=['POST'])
def search_calls():
    """Search calls by intent, phone, or keywords"""
    data = request.json
    query = data.get('query', '')
    
    calls = CallLog.query.filter(
        db.or_(
            CallLog.caller_phone.contains(query),
            CallLog.caller_intent.contains(query),
            CallLog.summary.contains(query)
        )
    ).order_by(CallLog.created_at.desc()).all()
    
    return jsonify([call.to_dict() for call in calls])

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get call statistics"""
    total_calls = db.session.query(CallLog).count()
    total_duration = db.session.query(db.func.sum(CallLog.call_duration)).scalar() or 0
    
    return jsonify({
        'total_calls': total_calls,
        'total_duration_minutes': total_duration / 60,
        'avg_duration': (total_duration / total_calls) if total_calls > 0 else 0
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
```

## Twilio ConversationRelay Handler (Node.js - separate service)

```javascript
// conversation-relay.js - Real-time Claude conversation handler
import Anthropic from "@anthropic-ai/sdk";
import { ConversationRelay } from "twilio-conversations";

const client = new Anthropic();

const SYSTEM_PROMPT = `You are a professional AI secretary answering calls on behalf of the user. Your responsibilities:

1. Greet the caller professionally
2. Ask clarifying questions to understand their purpose
3. Be courteous and patient, even with difficult callers
4. Gather all relevant information (name, contact, issue details)
5. Provide brief, helpful responses
6. Confirm key information back to the caller

After the call, you'll generate:
- A summary of the conversation
- The caller's main intent
- Any action items or follow-ups needed

Keep responses concise and natural - sound like a helpful secretary, not a robot.`;

class CallHandler {
  constructor() {
    this.conversationHistory = [];
    this.callMetadata = {
      callerIntent: "",
      actionItems: [],
      importantDetails: {},
    };
  }

  async handleConversation(message) {
    // Add user message to history
    this.conversationHistory.push({
      role: "user",
      content: message,
    });

    try {
      // Get Claude's response
      const response = await client.messages.create({
        model: "claude-3-5-sonnet-20241022",
        max_tokens: 500,
        system: SYSTEM_PROMPT,
        messages: this.conversationHistory,
      });

      const assistantMessage = response.content[0].text;

      // Add assistant response to history
      this.conversationHistory.push({
        role: "assistant",
        content: assistantMessage,
      });

      // Analyze for intent and action items
      await this.analyzeConversation();

      return {
        response: assistantMessage,
        shouldContinue: response.stop_reason === "end_turn",
      };
    } catch (error) {
      console.error("Error getting Claude response:", error);
      return {
        response:
          "I apologize, there was a technical issue. Could you please repeat that?",
        shouldContinue: true,
      };
    }
  }

  async analyzeConversation() {
    if (this.conversationHistory.length < 4) return; // Wait for some conversation

    try {
      const analysisPrompt = `Based on this conversation history, extract:
1. Caller's main intent (brief phrase)
2. Action items or follow-ups needed
3. Important details mentioned (name, phone, issue, etc.)

Format as JSON.`;

      const response = await client.messages.create({
        model: "claude-3-5-sonnet-20241022",
        max_tokens: 300,
        messages: [
          {
            role: "user",
            content: `${analysisPrompt}\n\nConversation:\n${JSON.stringify(
              this.conversationHistory
            )}`,
          },
        ],
      });

      const analysis = JSON.parse(response.content[0].text);
      this.callMetadata = { ...this.callMetadata, ...analysis };
    } catch (error) {
      console.warn("Could not analyze conversation:", error);
    }
  }

  getCallSummary() {
    const fullTranscript = this.conversationHistory
      .map((msg) => `${msg.role.toUpperCase()}: ${msg.content}`)
      .join("\n\n");

    return {
      transcript: fullTranscript,
      summary: this.generateSummary(),
      ...this.callMetadata,
    };
  }

  generateSummary() {
    if (this.conversationHistory.length === 0) return "";

    const messages = this.conversationHistory
      .map((msg) => `${msg.role}: ${msg.content}`)
      .join("\n");

    return `Call Summary:\n- Intent: ${this.callMetadata.callerIntent}\n- Action Items: ${this.callMetadata.actionItems.join(
      ", "
    ) || "None"}\n- Details: ${JSON.stringify(
      this.callMetadata.importantDetails
    )}`;
  }
}

export default CallHandler;
```

## Configuration & Deployment Files

```yaml
# render.yaml - Render deployment config
services:
  - type: web
    name: ai-secretary-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --workers=2 --log-level=info app:app
    envVars:
      - key: PYTHON_VERSION
        value: "3.11"
      - key: DATABASE_URL
        sync: false
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: TWILIO_ACCOUNT_SID
        sync: false
      - key: TWILIO_AUTH_TOKEN
        sync: false
      - key: OPENAI_API_KEY
        sync: false

  - type: postgresql
    name: ai-secretary-db
    ipAllowList: []
```

```text
# requirements.txt
Flask==3.0.0
Flask-CORS==4.0.0
Flask-SQLAlchemy==3.1.1
psycopg2-binary==2.9.9
anthropic==0.7.1
twilio==8.10.0
python-dotenv==1.0.0
gunicorn==21.2.0
httpx==0.25.1
```

```json
// package.json - Node.js dependencies
{
  "name": "ai-secretary-relay",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "start": "node index.js",
    "dev": "nodemon index.js"
  },
  "dependencies": {
    "@anthropic-ai/sdk": "^0.16.0",
    "twilio": "^4.0.0",
    "express": "^4.18.2",
    "ws": "^8.14.2",
    "dotenv": "^16.3.1"
  }
}
```
