# AI Answering Service - Deployment Guide

Austin Kidwell | ASR Inc / Intellegix

## Overview
Complete deployment instructions for the AI-powered phone answering service using Claude + Twilio + React dashboard.

## Architecture
- **Backend**: Flask API (Python) - Call management and webhooks
- **Conversation Engine**: Node.js service with Claude + OpenAI TTS
- **Frontend**: React dashboard for call monitoring
- **Database**: PostgreSQL for call logs
- **Deployment**: Render.com with auto-scaling

## Prerequisites

### Required API Keys
1. **Anthropic Claude API**: [Get key here](https://console.anthropic.com/)
2. **OpenAI API**: [Get key here](https://platform.openai.com/)
3. **Twilio Account**: [Sign up here](https://www.twilio.com/)
4. **Perplexity API** (Optional): [Get key here](https://www.perplexity.ai/)

### Twilio Setup
1. Purchase a phone number in Twilio Console
2. Note your Account SID and Auth Token
3. Configure webhooks (done after deployment)

## Local Development

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Fill in your API keys in .env
python app.py
```

### Conversation Relay Setup
```bash
cd backend
npm install
# Make sure .env has ANTHROPIC_API_KEY and OPENAI_API_KEY
node conversation_relay.js
```

### Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env
# Set REACT_APP_API_URL=http://localhost:5000
npm start
```

### Test Locally
1. Backend health check: http://localhost:5000/health
2. Conversation relay health: http://localhost:5001/relay/health
3. Frontend dashboard: http://localhost:3000

## Production Deployment on Render

### Step 1: Create Render Account
1. Sign up at [render.com](https://render.com/)
2. Connect your GitHub repository

### Step 2: Deploy Using render.yaml
1. Push code to GitHub repository
2. In Render dashboard, create "New Blueprint"
3. Connect to your repository
4. Render will automatically deploy all services from render.yaml

### Step 3: Configure Environment Variables

#### Backend Service Environment Variables
```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-...
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...
PERPLEXITY_API_KEY=ppl-...  # Optional
FLASK_ENV=production
LOG_LEVEL=INFO
```

#### Conversation Relay Environment Variables
```bash
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-...
NODE_ENV=production
RELAY_PORT=5001
```

### Step 4: Database Setup
1. PostgreSQL database is automatically created via render.yaml
2. Database URL is automatically set for backend service
3. Tables are created automatically on first run

### Step 5: Configure Twilio Webhooks

#### Get Your Render URLs
After deployment, note these URLs:
- Backend: `https://ai-secretary-backend.onrender.com`
- Frontend: `https://ai-secretary-frontend.onrender.com`

#### Set Twilio Webhooks
1. Go to Twilio Console → Phone Numbers → Manage → Active numbers
2. Click your purchased number
3. Set webhook URL for incoming calls:
   ```
   https://ai-secretary-backend.onrender.com/incoming-call
   ```
4. Set webhook for call status updates:
   ```
   https://ai-secretary-backend.onrender.com/call-ended
   ```

### Step 6: Test Production Deployment

#### Health Checks
- Backend: https://ai-secretary-backend.onrender.com/health
- Relay: https://ai-conversation-relay.onrender.com/relay/health
- Frontend: https://ai-secretary-frontend.onrender.com

#### End-to-End Test
1. Call your Twilio phone number
2. Verify AI assistant answers professionally
3. Check dashboard for call logs
4. Verify call summary generation

## Configuration & Customization

### System Prompt Customization
Edit the `SYSTEM_PROMPT` in `backend/conversation_relay.js`:
```javascript
const SYSTEM_PROMPT = `
You are a professional AI secretary for [YOUR BUSINESS NAME].
// Add your specific business context here
`;
```

### Business Information
Update these details in the system prompt:
- Company names and services
- Location and contact information
- Industry-specific terminology
- Common inquiries and responses

### Call Routing Logic
Modify `backend/app.py` to add custom routing based on:
- Time of day
- Caller phone number
- Identified intent
- Keywords in conversation

## Monitoring & Maintenance

### Health Monitoring
Set up monitoring for these endpoints:
- `/health` - Backend API health
- `/relay/health` - Conversation service health
- Frontend availability

### Log Access
- Backend logs: Render dashboard → ai-secretary-backend → Logs
- Relay logs: Render dashboard → ai-conversation-relay → Logs
- Frontend: Browser developer tools

### Database Maintenance
```sql
-- View recent calls
SELECT * FROM call_logs ORDER BY created_at DESC LIMIT 10;

-- Call volume by day
SELECT DATE(created_at), COUNT(*)
FROM call_logs
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY DATE(created_at);

-- Average call duration
SELECT AVG(call_duration) as avg_seconds
FROM call_logs
WHERE call_status = 'completed';
```

## Cost Optimization

### Estimated Monthly Costs

#### Render.com Hosting
- Backend web service: $7/month
- Conversation relay: $7/month
- Frontend static site: Free
- PostgreSQL database: $7/month
- **Total**: ~$21/month

#### API Usage (based on 100 calls/month)
- Claude API: ~$15/month
- OpenAI TTS: ~$5/month
- Twilio phone + usage: ~$10/month
- **Total**: ~$30/month

#### **Grand Total**: ~$51/month

### Cost Reduction Tips
1. Use Render free tier for development
2. Optimize Claude prompts for shorter responses
3. Cache frequent responses
4. Use cheaper TTS voice options
5. Monitor and set API usage alerts

## Security Considerations

### API Key Protection
- Never commit API keys to version control
- Use Render environment variables only
- Rotate keys regularly
- Monitor usage for anomalies

### Network Security
- HTTPS enforced on all endpoints
- CORS configured for frontend domain
- Input validation on all API endpoints
- Rate limiting on public endpoints

### Data Protection
- Call transcripts stored securely in PostgreSQL
- Personal information handling compliance
- Option to auto-delete old calls
- Encryption at rest (Render default)

## Troubleshooting

### Common Issues

#### "Health check failed"
1. Check environment variables are set
2. Verify database connection
3. Check service logs in Render dashboard

#### "Claude API errors"
1. Verify API key is valid and active
2. Check rate limits and usage quotas
3. Monitor Claude status page

#### "Calls not connecting"
1. Verify Twilio webhook URLs are correct
2. Check Twilio phone number configuration
3. Test webhook endpoints manually

#### "Dashboard not loading calls"
1. Check backend API health endpoint
2. Verify frontend API URL configuration
3. Check CORS settings in backend

### Support Contacts
- Render Support: [render.com/docs](https://render.com/docs)
- Twilio Support: [twilio.com/help](https://twilio.com/help)
- Claude API: [docs.anthropic.com](https://docs.anthropic.com)
- Austin Kidwell: [Your contact information]

## Future Enhancements

### Planned Features
1. Real-time call notifications
2. Calendar integration for appointments
3. Multi-language support
4. Advanced analytics and reporting
5. Integration with CRM systems

### Scaling Considerations
- Implement caching for frequent responses
- Add load balancing for high call volumes
- Consider dedicated voice infrastructure
- Implement call queue management

---

**Success Criteria**: After deployment, you should be able to:
✅ Receive calls on your Twilio number
✅ Have Claude respond professionally
✅ View call logs in the dashboard
✅ Search and filter calls effectively
✅ Generate automatic call summaries
✅ Monitor call statistics in real-time