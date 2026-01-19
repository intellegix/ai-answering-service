# AI SECRETARY SYSTEM - QUICK START & ARCHITECTURE

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         INCOMING PHONE CALL                      │
│                         (via Twilio)                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │    Twilio Voice API            │
        │  - Handles phone routing       │
        │  - WebSocket streaming         │
        │  - Audio encoding/decoding     │
        └────────┬───────────────────────┘
                 │
                 ▼
    ┌─────────────────────────────────────────┐
    │   Twilio ConversationRelay              │
    │   (Real-time voice bidirectional)       │
    └──────────┬──────────────────────────────┘
               │
      ┌────────┴─────────┐
      ▼                  ▼
┌────────────────┐  ┌──────────────────┐
│  Audio Input   │  │  Speech-to-Text  │
│  (Caller)      │  │  (OpenAI Whisper)│
└────────────────┘  └────────┬─────────┘
                             │
                             ▼
                    ┌────────────────────────────┐
                    │   Claude 3.5 Sonnet        │
                    │  - Conversation reasoning  │
                    │  - Context awareness       │
                    │  - Decision making         │
                    │  - Note generation         │
                    └────────┬───────────────────┘
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
            ┌──────────────┐  ┌────────────────┐
            │ Claude Notes │  │ Perplexity API │
            │ & Summary    │  │ (Web search)   │
            └──────┬───────┘  └────────────────┘
                   │
                   ▼
           ┌──────────────────┐
           │  Text-to-Speech  │
           │  (OpenAI TTS)    │
           └────────┬─────────┘
                    │
                    ▼
        ┌──────────────────────────┐
        │    Audio Output          │
        │    (Back to Caller)      │
        └──────────────────────────┘


POST-CALL PROCESSING:
                    ▼
        ┌──────────────────────────┐
        │  Save to Database        │
        │  (PostgreSQL/Supabase)   │
        │  - Transcript            │
        │  - Summary               │
        │  - Intent                │
        │  - Action items          │
        └────────┬─────────────────┘
                 │
                 ▼
        ┌──────────────────────────┐
        │   React Web Dashboard    │
        │  - View call history     │
        │  - Search by intent      │
        │  - Review summaries      │
        │  - See transcripts       │
        └──────────────────────────┘
```

---

## Project Structure

```
ai-secretary-system/
│
├── ai-secretary-backend/          # Flask backend
│   ├── app.py                    # Main Flask app
│   ├── models.py                 # Database models (CallLog)
│   ├── config.py                 # Configuration
│   ├── conversation_relay.js     # Twilio ConversationRelay handler
│   ├── requirements.txt           # Python dependencies
│   ├── .env.example              # Environment variables template
│   ├── render.yaml               # Render deployment config
│   └── README.md                 # Setup instructions
│
├── ai-secretary-frontend/        # React frontend
│   ├── public/
│   ├── src/
│   │   ├── App.jsx              # Main app component
│   │   ├── App.css              # Styles
│   │   ├── components/
│   │   │   ├── CallList.jsx
│   │   │   ├── CallDetail.jsx
│   │   │   ├── SearchBar.jsx
│   │   │   └── Stats.jsx
│   │   └── utils/
│   │       └── formatting.js
│   ├── package.json
│   ├── .env.example
│   └── README.md
│
└── docs/
    ├── ARCHITECTURE.md           # This file
    ├── DEPLOYMENT.md             # Full deployment guide
    ├── API.md                    # API documentation
    └── TROUBLESHOOTING.md        # Common issues & fixes
```

---

## Data Flow Example

### 1. INCOMING CALL
```
Phone rings → Twilio receives → Routes to /incoming-call → Claude initialized
```

### 2. CONVERSATION
```
Caller: "Hi, I need to schedule a service appointment"
     ↓
Twilio captures audio → Whisper transcribes
     ↓
"Hi, I need to schedule a service appointment"
     ↓
Claude (with context): "I understand. Can you tell me what service you need?
This will help me make sure you get the right appointment."
     ↓
TTS converts to audio → Plays back to caller
```

### 3. CONVERSATION CONTINUES...
```
Caller: "Plumbing repair, water heater issue"
     ↓
Claude analyzes intent: "maintenance_request" + perplexity searches for relevant info
     ↓
Claude: "For water heater issues, we typically have availability Tuesday-Thursday.
What's your preferred date?"
     ↓
Caller: "Wednesday afternoon works"
     ↓
Claude notes: action_item = ["Schedule plumbing Wed afternoon for water heater repair"]
```

### 4. CALL ENDS
```
Database updated with:
- Transcript (full conversation)
- Summary (what was discussed)
- Intent (maintenance_request)
- Action Items (schedule Wed afternoon)
- Duration (5m 23s)
- Caller phone number
- Timestamp
```

### 5. DASHBOARD DISPLAY
```
User checks dashboard → Sees new call:
- From: +1-555-123-4567
- Duration: 5m 23s
- Intent: Maintenance Request
- Summary: Customer reported water heater issue, prefers Wed afternoon

Click to expand:
- Full transcript displayed
- Can search by phone or keyword
- Edit notes if needed
```

---

## Configuration Deep Dive

### Claude System Prompt Customization

Tailor the system prompt in `conversation_relay.js` to your business:

```javascript
const SYSTEM_PROMPT = `You are a professional AI secretary for [YOUR BUSINESS NAME].

BUSINESS CONTEXT:
- Business type: [e.g., Plumbing service]
- Available hours: [e.g., 9 AM - 5 PM Mon-Fri]
- Service areas: [e.g., Greater Los Angeles]
- Typical inquiry types: [e.g., emergencies, estimates, scheduling]

YOUR RESPONSIBILITIES:
1. Greet callers professionally and warmly
2. Quickly understand their inquiry type
3. Ask clarifying questions
4. Provide relevant information (hours, service areas, etc.)
5. Take detailed notes for [BUSINESS OWNER]

FOR [SPECIFIC SERVICE] INQUIRIES:
- Always get: Name, phone number, address, issue description
- Offer available appointment slots
- Explain next steps clearly
- Be empathetic about emergency situations

TONE: Professional, helpful, patient, friendly

After every call, summarize:
- Caller name and contact
- Primary reason for call
- Key details mentioned
- Next steps/appointments offered
`;
```

---

## API Endpoints Reference

### Call Management
```
GET    /api/calls                 # Get all calls
GET    /api/calls/<id>            # Get specific call
POST   /api/calls/search          # Search calls (query, intent, phone)
GET    /api/stats                 # Get statistics
```

### Twilio Webhooks
```
POST   /incoming-call             # Called when phone rings
POST   /call-ended                # Called when call ends
GET    /ws/stream                 # WebSocket for audio (Twilio)
```

### Health Check
```
GET    /health                    # Server status
```

---

## Security Considerations

### 1. API Authentication (Optional)
Add bearer token validation:
```python
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get('Authorization')
        if not key or key.split(' ')[1] != API_KEY:
            return {'error': 'Unauthorized'}, 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/calls')
@require_api_key
def get_calls():
    ...
```

### 2. CORS Configuration
```python
CORS(app, origins=[
    "https://ai-secretary-frontend.onrender.com",
    "http://localhost:3000"
])
```

### 3. Database Security
- Use strong Supabase passwords
- Enable Row Level Security (RLS)
- Regular backups
- Never commit .env files

### 4. API Key Management
- Store all keys in environment variables
- Rotate keys regularly
- Use service-specific keys where possible
- Monitor API usage for unusual patterns

---

## Performance Optimization

### 1. Response Time
- Claude typically responds in 1-3 seconds
- OpenAI TTS: <2 seconds for 30s of speech
- Optimize by keeping conversations brief

### 2. Database Optimization
```sql
-- Add indexes for faster searches
CREATE INDEX idx_caller_phone ON call_logs(caller_phone);
CREATE INDEX idx_caller_intent ON call_logs(caller_intent);
CREATE INDEX idx_created_at ON call_logs(created_at);
```

### 3. Caching
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_business_hours():
    # Cache business hours to avoid repeated queries
    return {"Mon-Fri": "9 AM - 5 PM"}
```

### 4. Async Processing
```python
from celery import Celery

celery = Celery(app.name)

@celery.task
def process_call_summary(call_id):
    # Process summaries asynchronously
    call = CallLog.query.get(call_id)
    call.summary = generate_summary(call.transcript)
    db.session.commit()
```

---

## Scaling Considerations

### Current Capacity
- Handles: 50-100 concurrent calls per server
- Response time: <3 seconds
- Database: Can store 100k+ calls

### Scaling Strategy
1. **Multiple Render instances** (auto-scaling)
2. **Database read replicas** for analytics
3. **Call queuing system** for peak times
4. **Caching layer** (Redis) for frequently accessed data

---

## Common Customizations

### 1. Multi-language Support
```python
lang = request.form.get('lang', 'en')
system_prompt = PROMPTS[lang]
response = client.messages.create(..., system=system_prompt)
```

### 2. Sentiment Analysis
```python
def analyze_sentiment(transcript):
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        messages=[{
            "role": "user",
            "content": f"Rate sentiment (positive/neutral/negative): {transcript}"
        }]
    )
    return response.content[0].text
```

### 3. Auto-routing to Departments
```python
intent = analyze_intent(transcript)
if "billing" in intent.lower():
    route_to = "billing@company.com"
elif "technical" in intent.lower():
    route_to = "support@company.com"
```

---

## Testing Checklist

- [ ] Backend starts without errors
- [ ] Frontend loads dashboard
- [ ] Database connection works
- [ ] Twilio webhook endpoint reachable
- [ ] Test call from any number
- [ ] Claude responds to caller
- [ ] Call duration recorded
- [ ] Summary generates after call
- [ ] Dashboard shows new call
- [ ] Search functionality works
- [ ] Stats update correctly

---

## Monitoring Dashboard (Optional)

Add to React dashboard:
```jsx
<div className="monitoring">
  <h3>System Health</h3>
  <p>Backend Status: {backendHealthy ? '✅ Healthy' : '❌ Down'}</p>
  <p>Database: {dbHealthy ? '✅ Connected' : '❌ Disconnected'}</p>
  <p>Avg Response Time: {avgResponseTime}ms</p>
  <p>Active Calls: {activeCalls}</p>
</div>
```

---

## Next Steps

1. Follow deployment-guide.md step-by-step
2. Test with sample calls
3. Review all Claude responses and customize prompt
4. Monitor system performance
5. Set up backups and maintenance schedule
6. Plan for scaling if needed

**Your AI Secretary is ready to serve!** 🤖
