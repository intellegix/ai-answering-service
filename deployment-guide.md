# AI SECRETARY COMPLETE SETUP & DEPLOYMENT GUIDE

## STEP 1: Prerequisites Setup

### 1.1 Create Twilio Account
- Go to https://www.twilio.com/console
- Sign up and verify your account
- Buy a phone number (any US/international number)
- Note your: **Account SID**, **Auth Token**, **Phone Number**

### 1.2 Set Up Supabase (PostgreSQL Database)
- Go to https://supabase.com
- Create a new project
- Copy your **Connection String** (Postgres URI)
- Under Authentication > Policies, ensure RLS is properly configured

### 1.3 Get API Keys
- **Anthropic Claude**: https://console.anthropic.com → Get API Key
- **OpenAI**: https://platform.openai.com → Get API Key for TTS
- **Perplexity** (optional): https://www.perplexity.ai/api → Get API Key

### 1.4 Install Local Dependencies
```bash
# Python
python --version  # Should be 3.10+

# Node.js
node --version   # Should be 16+
npm --version
```

---

## STEP 2: Backend Setup (Flask + Twilio)

### 2.1 Create Backend Directory
```bash
mkdir ai-secretary-backend
cd ai-secretary-backend
```

### 2.2 Create Virtual Environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

### 2.3 Create requirements.txt
```
Flask==3.0.0
Flask-CORS==4.0.0
Flask-SQLAlchemy==3.1.1
psycopg2-binary==2.9.9
anthropic==0.7.1
twilio==8.10.0
python-dotenv==1.0.0
gunicorn==21.2.0
httpx==0.25.1
pydub==0.25.1
```

```bash
pip install -r requirements.txt
```

### 2.4 Create .env File
```
# Database
DATABASE_URL=postgresql://[user]:[password]@[host]:[port]/[database]

# Twilio
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890

# APIs
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
PERPLEXITY_API_KEY=ppl-...

# Deployment
RENDER_HOST=ai-secretary-backend.onrender.com
FLASK_ENV=production
PORT=5000
```

### 2.5 Create app.py
See **backend-setup.md** for complete Flask application code.

### 2.6 Test Locally
```bash
flask run
# App should start at http://localhost:5000
# Visit http://localhost:5000/health to test
```

---

## STEP 3: Frontend Setup (React)

### 3.1 Create React App
```bash
# In parent directory
npx create-react-app ai-secretary-frontend
cd ai-secretary-frontend
```

### 3.2 Replace src files
Copy all files from **frontend-setup.md** into src/ directory:
- src/App.jsx
- src/App.css
- src/components/CallList.jsx
- src/components/CallDetail.jsx
- src/components/SearchBar.jsx
- src/components/Stats.jsx
- src/utils/formatting.js

### 3.3 Create .env File
```
REACT_APP_API_URL=http://localhost:5000/api
```

### 3.4 Test Locally
```bash
npm start
# App should open at http://localhost:3000
```

---

## STEP 4: Deploy to Render

### 4.1 Prepare Backend for Render

**Create render.yaml in backend root:**
```yaml
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

### 4.2 Deploy Backend to Render
1. Push backend code to GitHub
2. Go to https://render.com
3. Click "New +" → "Web Service"
4. Connect your GitHub repo
5. Use settings from render.yaml
6. Add environment variables (don't use DATABASE_URL yet - Render will provide it)
7. Click "Deploy"
8. Once deployed, copy your Render URL (e.g., ai-secretary-backend.onrender.com)

### 4.3 Update Environment Variables
After Render creates the PostgreSQL service:
1. Go to your Render project
2. Environment → Add `DATABASE_URL` from PostgreSQL service
3. Add: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `ANTHROPIC_API_KEY`, etc.
4. Redeploy

### 4.4 Deploy Frontend to Render
```bash
# In frontend directory
npm run build
```

1. Create Render account (if not done)
2. Click "New +" → "Static Site"
3. Connect your frontend GitHub repo
4. Build Command: `npm run build`
5. Publish Directory: `build`
6. Add environment variable:
   ```
   REACT_APP_API_URL=https://ai-secretary-backend.onrender.com/api
   ```
7. Deploy

**Your frontend is now live at:** `https://ai-secretary-frontend.onrender.com`

---

## STEP 5: Configure Twilio Webhooks

### 5.1 Set Up Call Handler Webhook
1. Go to Twilio Console → Phone Numbers → Active Numbers
2. Click your phone number
3. Under "Voice & Faxes" → Webhook URL for incoming calls:
   ```
   https://ai-secretary-backend.onrender.com/incoming-call
   ```
4. HTTP Method: POST
5. Save

### 5.2 Set Up Call Ended Webhook (Optional)
If you want logging when calls end:
```
https://ai-secretary-backend.onrender.com/call-ended
```

---

## STEP 6: Configure Claude Integration

### 6.1 System Prompt Customization
Edit the SYSTEM_PROMPT in conversation-relay.js to match your use case:

```javascript
const SYSTEM_PROMPT = `You are a professional AI secretary answering calls 
for [YOUR NAME/BUSINESS]. 

Key responsibilities:
- Greet callers professionally
- Ask clarifying questions about their purpose
- Be patient and courteous
- Gather contact information
- Take detailed notes

For [YOUR SPECIFIC BUSINESS], prioritize:
- Getting caller name and contact
- Understanding their specific need
- Any relevant details for follow-up

After the call, generate:
1. Summary of conversation
2. Caller intent
3. Action items for follow-up
`;
```

### 6.2 Enable Perplexity Search (Optional)
If caller mentions needing information, Claude can search the web:

```python
# In app.py, add:
import httpx

async def search_perplexity(query):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.perplexity.ai/chat/completions",
            json={
                "model": "pplx-7b-online",
                "messages": [{"role": "user", "content": query}],
            },
            headers={"Authorization": f"Bearer {PERPLEXITY_API_KEY}"}
        )
    return response.json()
```

---

## STEP 7: Testing

### 7.1 Test Call Flow
1. Ensure Render backend is running
2. Visit React app dashboard
3. Call your Twilio phone number
4. Speak with the AI secretary
5. After call ends, check dashboard for call log

### 7.2 Debug Issues
```bash
# Check Render logs
# In Render dashboard: your-service → Logs

# Check Twilio logs
# In Twilio Console → Monitor → Logs

# Local testing
curl http://localhost:5000/health
```

### 7.3 Common Issues

**"Call not connecting"**
- Check Twilio webhook URL is correct
- Verify TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN
- Check Render logs for errors

**"Database connection error"**
- Verify DATABASE_URL in Render environment
- Check Supabase PostgreSQL is running
- Ensure IP allowlist permits Render

**"Claude not responding"**
- Verify ANTHROPIC_API_KEY is valid
- Check API key isn't revoked
- Review Anthropic usage limits

---

## STEP 8: Advanced Configuration

### 8.1 Custom Call Routing
In app.py:
```python
@app.route('/incoming-call', methods=['POST'])
def incoming_call():
    caller_number = request.form.get('From')
    
    # Route VIP numbers differently
    if caller_number in PRIORITY_CALLERS:
        greeting = "Connecting you to the priority line..."
    else:
        greeting = "Thank you for calling..."
```

### 8.2 Email Notifications
```python
from flask_mail import Mail, Message

mail = Mail(app)

def send_call_summary(email, call_data):
    msg = Message(
        'New Call Summary',
        recipients=[email],
        html=f"<h2>{call_data['caller_intent']}</h2>"
             f"<p>{call_data['summary']}</p>"
    )
    mail.send(msg)
```

### 8.3 Slack Integration
```python
import slack_sdk

def notify_slack(call_data):
    client = slack_sdk.WebClient(token=SLACK_BOT_TOKEN)
    client.chat_postMessage(
        channel="#calls",
        text=f"📞 New Call from {call_data['caller_phone']}\n"
             f"Intent: {call_data['caller_intent']}"
    )
```

---

## STEP 9: Monitoring & Maintenance

### 9.1 Daily Checks
- Monitor Render service health
- Check database size growth
- Review error logs
- Test with a sample call weekly

### 9.2 Monthly Tasks
- Backup database
- Review call patterns/trends
- Update system prompt based on learnings
- Check API usage/costs

### 9.3 Performance Optimization
- Cache frequently asked responses
- Implement call queuing if busy
- Monitor API response times
- Optimize database queries

---

## COST ESTIMATES

| Service | Cost | Notes |
|---------|------|-------|
| Twilio | $1/phone + $0.0075/min incoming | Small volume: ~$20-50/month |
| Render | $7-15 | Web service + PostgreSQL |
| Supabase | Free-$25 | Included in Render setup |
| Anthropic Claude | $3-10/million tokens | Depends on conversation length |
| OpenAI TTS | $0.015 per 1000 chars | Small amount per call |
| **Total** | ~$50-100/month | For low-volume use |

---

## Next Steps

1. ✅ Set up all accounts (Step 1)
2. ✅ Deploy backend (Steps 2-4)
3. ✅ Deploy frontend (Step 4)
4. ✅ Configure Twilio (Step 5)
5. ✅ Test the system (Step 7)
6. ✅ Customize for your needs (Step 8)
7. Monitor and iterate (Step 9)

**You now have a fully functional AI secretary system!**
