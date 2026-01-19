# AI Answering Service - Testing Guide

Austin Kidwell | ASR Inc / Intellegix

## Testing Checklist

### Local Development Testing

#### Backend API Tests
```bash
# Health check
curl http://localhost:5000/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-01-19T...",
  "database": "connected",
  "version": "1.0.0"
}

# Test API endpoints
curl http://localhost:5000/api/calls
curl http://localhost:5000/api/stats
```

#### Conversation Relay Tests
```bash
# Health check
curl http://localhost:5001/relay/health

# Expected response:
{
  "status": "healthy",
  "service": "conversation-relay",
  "timestamp": "2024-01-19T..."
}
```

#### Frontend Tests
1. Open http://localhost:3000
2. Verify dashboard loads without errors
3. Check that stats section displays correctly
4. Test search functionality (should show "no calls found" initially)
5. Verify responsive design on mobile viewport

### Production Deployment Tests

#### Service Health Checks
- Backend: https://ai-secretary-backend.onrender.com/health
- Relay: https://ai-conversation-relay.onrender.com/relay/health
- Frontend: https://ai-secretary-frontend.onrender.com

#### End-to-End Call Flow Test

1. **Make Test Call**
   - Call your Twilio phone number
   - Verify AI assistant answers professionally
   - Have a brief conversation (ask about services)
   - Note the call duration and hang up

2. **Verify Call Logging**
   - Check dashboard within 2-3 minutes
   - Verify call appears in recent calls
   - Check that call duration is accurate
   - Verify call status shows "completed"

3. **Test Call Summary**
   - Click on the test call in dashboard
   - Verify transcript was captured
   - Check that AI summary was generated
   - Verify caller intent was identified
   - Check action items (if any were generated)

4. **Test Search Functionality**
   - Search by your phone number
   - Search by keywords from conversation
   - Test date range filtering
   - Verify results are accurate

### Performance Tests

#### Response Time Verification
- Dashboard load time: <3 seconds
- Call answer time: <5 seconds
- API response time: <1 second
- Search results: <2 seconds

#### Concurrent Call Test
If expecting high call volume:
- Test multiple simultaneous calls (ask friends/family to call)
- Verify all calls are handled properly
- Check that summaries are generated for all calls
- Monitor Render service scaling in dashboard

### Security Tests

#### API Security
```bash
# Test CORS (should be configured for frontend domain)
curl -H "Origin: https://malicious-site.com" https://ai-secretary-backend.onrender.com/api/calls

# Test rate limiting (should prevent abuse)
for i in {1..100}; do curl https://ai-secretary-backend.onrender.com/health; done
```

#### Environment Variables
- Verify no API keys are exposed in frontend code
- Check that .env files are not committed to git
- Confirm all sensitive data is in Render environment variables

### Error Handling Tests

#### Network Failures
1. Turn off internet during call
2. Verify graceful degradation
3. Check error logging

#### API Failures
1. Temporarily set invalid Claude API key
2. Make test call
3. Verify fallback message is played
4. Check error logs in Render dashboard

#### Database Failures
1. Test with database temporarily unavailable
2. Verify API health check reports issue
3. Confirm graceful error handling

### Mobile Responsiveness Tests

Test dashboard on various devices:
- iPhone (Safari)
- Android (Chrome)
- iPad (Safari)
- Various screen sizes (320px to 1920px)

Verify all features work:
- ✅ Stats cards display properly
- ✅ Call list is readable and clickable
- ✅ Search functionality works
- ✅ Call details are accessible
- ✅ Navigation is intuitive

### Integration Tests

#### Twilio Webhook Tests
1. Use Twilio Console webhook tester
2. Send test webhook to your endpoints
3. Verify database updates correctly
4. Check response format compliance

#### Claude API Integration
1. Monitor Claude API usage in console
2. Verify conversation quality
3. Check response times and errors
4. Test edge cases (very long conversations)

#### OpenAI TTS Integration
1. Listen to generated speech quality
2. Test different voice settings
3. Verify audio clarity over phone
4. Check for any audio artifacts

## Troubleshooting Common Issues

### "Health check failed"
- Check Render service logs
- Verify environment variables are set
- Check database connectivity

### "No calls appearing in dashboard"
- Verify Twilio webhook URLs are correct
- Check backend service is running
- Look for errors in conversation relay logs

### "Poor call quality or delays"
- Check your internet connection
- Monitor Claude API response times
- Verify TTS service performance
- Test with different phone/network

### "Search not working"
- Check database contains call data
- Verify search API endpoints
- Test with simple queries first
- Check for JavaScript errors in browser

## Performance Monitoring

### Metrics to Track
- Call volume per day/week
- Average call duration
- Call completion rate
- Dashboard page load times
- API response times
- Error rates

### Render Dashboard Monitoring
- CPU and memory usage
- Request counts and response times
- Error logs and patterns
- Database performance metrics

## Success Criteria

✅ **Basic Functionality**
- Calls are answered automatically
- AI responds intelligently
- Calls are logged in dashboard
- Summaries are generated

✅ **Performance**
- <5 second call answer time
- <3 second dashboard load time
- 95%+ call completion rate
- No dropped calls or failed webhooks

✅ **User Experience**
- Professional AI conversation quality
- Mobile-responsive dashboard
- Fast and accurate search
- Clear call information display

✅ **Reliability**
- 24/7 uptime for call handling
- Automatic error recovery
- Data backup and persistence
- Monitoring and alerting

## Test Data Cleanup

After testing, you may want to clean up test calls:

```sql
-- Connect to database and run:
DELETE FROM call_logs WHERE caller_phone = '+1YOUR_TEST_PHONE';

-- Or delete all test data:
DELETE FROM call_logs WHERE created_at > 'YYYY-MM-DD';
```

## Ongoing Testing

### Weekly Tests
- Make a test call and verify end-to-end flow
- Check dashboard for any UI issues
- Review call quality and AI responses
- Monitor service health and performance

### Monthly Reviews
- Analyze call patterns and volume
- Review conversation quality samples
- Update system prompts if needed
- Check cost vs usage trends

---

**Testing Complete?** Your AI answering service should now be handling calls professionally and providing excellent dashboard analytics for business management.