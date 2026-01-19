# AI Answering Service

**Professional AI-powered phone answering system built with Claude + Twilio + React**

*Austin Kidwell | ASR Inc / Intellegix*

---

## 🚀 Overview

A complete AI answering service that handles incoming phone calls using Claude 3.5 Sonnet for intelligent conversation, OpenAI TTS for natural speech, and a React dashboard for call management. Perfect for small businesses that need professional phone coverage 24/7.

### Key Features

✅ **Intelligent Conversations**: Claude 3.5 Sonnet handles calls professionally
✅ **Real-time Voice**: Bidirectional audio streaming via Twilio
✅ **Call Management**: Complete React dashboard for call history and analytics
✅ **Automatic Summaries**: AI-generated call summaries and action items
✅ **Mobile Responsive**: Dashboard works perfectly on mobile devices
✅ **Search & Filter**: Powerful search across call transcripts and metadata
✅ **Business Context**: Customizable for your specific industry and services

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Incoming      │    │  Twilio Voice    │    │  Claude 3.5     │
│   Phone Call    │───▶│  WebSocket       │───▶│  Sonnet API     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  React          │    │  Flask API       │    │  OpenAI TTS     │
│  Dashboard      │◀───│  Backend         │◀───│  Speech         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  PostgreSQL      │
                       │  Call Logs       │
                       └──────────────────┘
```

### Technology Stack
- **Backend**: Flask (Python) + SQLAlchemy + PostgreSQL
- **AI Engine**: Node.js + Claude API + OpenAI TTS
- **Frontend**: React + Modern CSS (mobile-first)
- **Voice**: Twilio Voice API + WebSocket streaming
- **Deployment**: Render.com with auto-scaling
- **Estimated Cost**: $50-85/month for typical usage

## 📁 Project Structure

```
AI Answering Service/
├── backend/
│   ├── app.py                  # Flask API server
│   ├── conversation_relay.js   # Node.js conversation engine
│   ├── requirements.txt        # Python dependencies
│   ├── package.json           # Node.js dependencies
│   └── .env.example           # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Main React application
│   │   ├── App.css            # Complete styling (mobile-responsive)
│   │   └── components/
│   │       ├── CallList.jsx   # Call history display
│   │       ├── CallDetail.jsx # Individual call view
│   │       ├── SearchBar.jsx  # Search and filtering
│   │       └── Stats.jsx      # Analytics dashboard
│   ├── public/
│   │   └── index.html         # HTML template
│   ├── package.json          # React dependencies
│   └── .env.example          # Frontend environment
├── render.yaml               # Deployment configuration
├── DEPLOYMENT.md            # Detailed deployment guide
├── .gitignore               # Git ignore rules
└── README.md               # This file
```

## 🚀 Quick Start

### 1. Get API Keys
- **Anthropic**: [console.anthropic.com](https://console.anthropic.com/) (Claude API)
- **OpenAI**: [platform.openai.com](https://platform.openai.com/) (TTS API)
- **Twilio**: [twilio.com](https://twilio.com/) (Phone number + API)

### 2. Local Development
```bash
# Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python app.py &

# Conversation Service
npm install
node conversation_relay.js &

# Frontend Setup
cd ../frontend
npm install
cp .env.example .env
npm start
```

### 3. Production Deployment
See [DEPLOYMENT.md](./DEPLOYMENT.md) for complete Render.com deployment instructions.

## 📱 Dashboard Screenshots

### Call Management Dashboard
- Real-time call statistics and analytics
- Recent activity feed with call summaries
- Performance insights and success rates

### Call History & Search
- Paginated call list with smart filtering
- Search by phone number, keywords, or intent
- Quick filters for today, this week, sales inquiries

### Call Detail View
- Complete conversation transcript
- Automatic AI-generated summary
- Extracted action items and caller intent
- Copy/export functionality for follow-up

## 🎯 Business Customization

### Industry-Specific Configuration
The system is pre-configured for construction/BI businesses but easily customizable:

```javascript
// Edit backend/conversation_relay.js
const SYSTEM_PROMPT = `
You are a professional AI secretary for [YOUR BUSINESS].
// Add your specific business context, services, and FAQs
`;
```

### Common Use Cases
- **Construction**: Project inquiries, estimates, scheduling
- **Professional Services**: Consultations, appointments, support
- **E-commerce**: Order status, returns, general inquiries
- **Healthcare**: Appointment scheduling, basic questions
- **Real Estate**: Property inquiries, showing requests

## 📊 Features in Detail

### Intelligent Call Handling
- Professional greeting and business context
- Intent recognition (sales, support, information)
- Natural conversation flow with context memory
- Automatic call summary generation
- Action item extraction for follow-up

### Dashboard Analytics
- Total calls and completion rates
- Daily/weekly call volume trends
- Average call duration tracking
- Recent call activity feed
- Performance insights and recommendations

### Search & Management
- Full-text search across call transcripts
- Filter by date range, phone number, intent
- Quick filters for common queries
- Pagination for large call volumes
- Export capabilities for reporting

## 🔒 Security & Privacy

### Data Protection
- All API keys stored as environment variables
- Call transcripts encrypted at rest
- HTTPS enforced on all endpoints
- Input validation and rate limiting
- CORS configured for frontend security

### Compliance Considerations
- Call recording disclosure (customize for your region)
- Data retention policies (configurable)
- Personal information handling
- Option for automatic transcript deletion

## 💰 Cost Breakdown

### Hosting (Render.com)
- Flask backend: $7/month
- Node.js conversation service: $7/month
- React frontend: Free (static site)
- PostgreSQL database: $7/month
- **Hosting Total**: $21/month

### API Usage (100 calls/month estimate)
- Claude 3.5 Sonnet: ~$15/month
- OpenAI TTS: ~$5/month
- Twilio phone + calls: ~$10/month
- **API Total**: ~$30/month

### **Grand Total**: ~$51/month

*Scales with usage - higher call volumes increase API costs*

## 🛠️ Customization Options

### Voice & Personality
- TTS voice selection (OpenAI offers multiple voices)
- Conversation style and personality adjustment
- Industry-specific terminology and responses
- Multi-language support (future enhancement)

### Business Integration
- Calendar integration for appointment scheduling
- CRM system webhooks for lead capture
- Email notifications for important calls
- Slack/Teams integration for real-time alerts

### Advanced Features (Roadmap)
- Call routing based on caller history
- Voicemail transcription and analysis
- Integration with payment processors
- Advanced analytics and reporting

## 📞 Support & Maintenance

### Monitoring
- Built-in health check endpoints
- Render dashboard for service monitoring
- Error logging and alerting
- Performance metrics tracking

### Troubleshooting
Common issues and solutions documented in [DEPLOYMENT.md](./DEPLOYMENT.md)

### Updates & Scaling
- Easy deployment via Git push to Render
- Auto-scaling based on call volume
- Database optimization for large call histories
- API rate limit management

## 🎯 Success Metrics

After deployment, you should achieve:
- ✅ 24/7 professional phone coverage
- ✅ <3 second average response time
- ✅ 95%+ call completion rate
- ✅ Automatic call documentation
- ✅ Mobile dashboard access anywhere
- ✅ Significant time savings on call handling

## 📝 License

MIT License - See [LICENSE](./LICENSE) for details.

## 👨‍💻 Author

**Austin Kidwell**
CEO & Systems Architect
ASR Inc / Intellegix
San Diego, CA

*Built with Claude Code for maximum efficiency and Austin's coding standards*

---

**Ready to deploy?** See [DEPLOYMENT.md](./DEPLOYMENT.md) for step-by-step instructions.

**Questions?** Check the troubleshooting section or create an issue for support.