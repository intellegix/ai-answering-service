/**
 * AI Answering Service - Conversation Relay
 * Real-time bidirectional conversation handler using Claude + Twilio
 * Austin Kidwell | ASR Inc / Intellegix
 */

const WebSocket = require('ws');
const express = require('express');
const http = require('http');
const Anthropic = require('@anthropic-ai/sdk');
const OpenAI = require('openai');
require('dotenv').config();

// Initialize clients
const anthropic = new Anthropic({
    apiKey: process.env.ANTHROPIC_API_KEY,
});

const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
});

// System prompt for Claude - customized for Austin's businesses
const SYSTEM_PROMPT = `
You are a professional AI secretary for Austin Kidwell's businesses: ASR Inc (Systems Integration) and Intellegix (Construction Business Intelligence SaaS). You handle phone calls with the professionalism of an experienced executive assistant.

CORE RESPONSIBILITIES:
- Answer calls professionally and gather caller information
- Determine the purpose of their call (sales inquiry, support, partnership, etc.)
- Schedule meetings or take detailed messages
- Provide basic information about our services
- Handle construction/BI industry inquiries appropriately

BUSINESS CONTEXT:
- ASR Inc: Systems integration, construction technology, project management
- Intellegix: SaaS platform for construction business intelligence, job costing, WIP analysis
- Location: San Diego, CA
- Industries: Construction, Commercial development, Fire mitigation, SB721 balcony compliance

CONVERSATION STYLE:
- Professional but warm and approachable
- Keep responses concise (under 30 seconds when spoken)
- Ask clarifying questions to understand their needs
- Always offer to take a message or schedule a callback
- Be knowledgeable about construction/BI terminology

IMPORTANT INSTRUCTIONS:
- Always get: caller name, company, phone number, reason for calling
- For technical questions: acknowledge expertise needed, offer to connect with Austin
- For sales inquiries: gather project details, timeline, budget range
- For existing clients: prioritize and offer immediate assistance
- End calls politely with next steps clearly stated

Keep responses conversational, natural, and under 100 words when possible.
`;

class ConversationManager {
    constructor() {
        this.conversations = new Map(); // Track active conversations
        this.conversationHistory = new Map(); // Store conversation context
    }

    async processUserMessage(sessionId, userMessage) {
        try {
            // Get or initialize conversation history
            if (!this.conversationHistory.has(sessionId)) {
                this.conversationHistory.set(sessionId, [{
                    role: 'system',
                    content: SYSTEM_PROMPT
                }]);
            }

            const history = this.conversationHistory.get(sessionId);

            // Add user message to history
            history.push({
                role: 'user',
                content: userMessage
            });

            // Get Claude's response
            const response = await anthropic.messages.create({
                model: 'claude-3-5-sonnet-20241022',
                max_tokens: 300,
                temperature: 0.7,
                messages: history.slice(1), // Exclude system message for API call
                system: SYSTEM_PROMPT
            });

            const assistantMessage = response.content[0].text;

            // Add assistant response to history
            history.push({
                role: 'assistant',
                content: assistantMessage
            });

            // Keep history manageable (last 20 messages)
            if (history.length > 21) {
                history.splice(1, 2); // Keep system message, remove oldest user/assistant pair
            }

            return assistantMessage;

        } catch (error) {
            console.error('Error processing Claude message:', error);
            return "I apologize, but I'm having trouble processing your request. Could you please repeat that?";
        }
    }

    async generateSpeech(text) {
        try {
            const response = await openai.audio.speech.create({
                model: 'tts-1',
                voice: 'nova', // Professional female voice
                input: text,
                response_format: 'mp3',
                speed: 0.95 // Slightly slower for clarity
            });

            return Buffer.from(await response.arrayBuffer());
        } catch (error) {
            console.error('Error generating speech:', error);
            throw error;
        }
    }

    getConversationSummary(sessionId) {
        const history = this.conversationHistory.get(sessionId);
        if (!history || history.length <= 1) {
            return null;
        }

        // Extract conversation for summary
        const conversation = history.slice(1).map(msg =>
            `${msg.role === 'user' ? 'Caller' : 'Assistant'}: ${msg.content}`
        ).join('\n');

        return {
            transcript: conversation,
            messageCount: history.length - 1
        };
    }

    async generateCallSummary(sessionId) {
        try {
            const conversationData = this.getConversationSummary(sessionId);
            if (!conversationData) {
                return null;
            }

            const summaryPrompt = `Please analyze this phone conversation and provide a structured summary:

${conversationData.transcript}

Provide a JSON response with:
- caller_intent: Brief description of why they called
- summary: 2-3 sentence summary of the conversation
- action_items: Array of specific follow-up actions needed
- caller_info: Any gathered contact information

Format as valid JSON only.`;

            const response = await anthropic.messages.create({
                model: 'claude-3-5-sonnet-20241022',
                max_tokens: 500,
                temperature: 0.3,
                messages: [{
                    role: 'user',
                    content: summaryPrompt
                }]
            });

            const summaryText = response.content[0].text;

            // Extract JSON from response
            const jsonMatch = summaryText.match(/\{[\s\S]*\}/);
            if (jsonMatch) {
                return JSON.parse(jsonMatch[0]);
            }

            return {
                caller_intent: "Call summary generation failed",
                summary: conversationData.transcript.substring(0, 200) + "...",
                action_items: [],
                caller_info: {}
            };

        } catch (error) {
            console.error('Error generating call summary:', error);
            return null;
        }
    }

    endConversation(sessionId) {
        this.conversations.delete(sessionId);
        // Keep history briefly for summary generation
        setTimeout(() => {
            this.conversationHistory.delete(sessionId);
        }, 30000); // 30 seconds
    }
}

// Initialize conversation manager
const conversationManager = new ConversationManager();

// Express app for health checks
const app = express();
app.use(express.json());

app.get('/relay/health', (req, res) => {
    res.json({
        status: 'healthy',
        service: 'conversation-relay',
        timestamp: new Date().toISOString()
    });
});

// WebSocket server for Twilio streams
const server = http.createServer(app);
const wss = new WebSocket.Server({
    server,
    path: '/ws/stream'
});

wss.on('connection', (ws, req) => {
    console.log('New WebSocket connection established');

    let sessionId = null;
    let conversationBuffer = '';
    let isProcessing = false;

    ws.on('message', async (message) => {
        try {
            const data = JSON.parse(message);

            switch (data.event) {
                case 'connected':
                    console.log('Twilio connected:', data);
                    break;

                case 'start':
                    sessionId = data.streamSid;
                    console.log(`Conversation started: ${sessionId}`);

                    // Send initial greeting
                    const greeting = "Hello! Thank you for calling ASR Inc and Intellegix. This is Austin's AI assistant. How can I help you today?";
                    const audioBuffer = await conversationManager.generateSpeech(greeting);

                    // Send audio to Twilio
                    ws.send(JSON.stringify({
                        event: 'media',
                        streamSid: sessionId,
                        media: {
                            payload: audioBuffer.toString('base64')
                        }
                    }));
                    break;

                case 'media':
                    // Receive audio from caller
                    const audioData = Buffer.from(data.media.payload, 'base64');

                    // Here you would typically use speech-to-text
                    // For now, we'll simulate with a simple response trigger
                    // In production, integrate with a STT service like Deepgram or AssemblyAI
                    break;

                case 'interim-transcription':
                    // Handle real-time transcription
                    if (data.alternatives && data.alternatives[0]) {
                        conversationBuffer = data.alternatives[0].transcript;
                    }
                    break;

                case 'transcription':
                    // Handle final transcription
                    if (data.alternatives && data.alternatives[0] && !isProcessing) {
                        const userMessage = data.alternatives[0].transcript;
                        console.log(`User said: ${userMessage}`);

                        if (userMessage.trim().length > 0) {
                            isProcessing = true;

                            try {
                                // Get Claude's response
                                const response = await conversationManager.processUserMessage(sessionId, userMessage);
                                console.log(`Assistant responding: ${response}`);

                                // Generate speech
                                const audioBuffer = await conversationManager.generateSpeech(response);

                                // Send to Twilio
                                ws.send(JSON.stringify({
                                    event: 'media',
                                    streamSid: sessionId,
                                    media: {
                                        payload: audioBuffer.toString('base64')
                                    }
                                }));

                            } catch (error) {
                                console.error('Error processing conversation:', error);

                                // Send error message
                                const errorResponse = "I'm sorry, I didn't catch that. Could you please repeat your question?";
                                const errorAudio = await conversationManager.generateSpeech(errorResponse);

                                ws.send(JSON.stringify({
                                    event: 'media',
                                    streamSid: sessionId,
                                    media: {
                                        payload: errorAudio.toString('base64')
                                    }
                                }));
                            } finally {
                                isProcessing = false;
                            }
                        }
                    }
                    break;

                case 'stop':
                    console.log(`Conversation ended: ${sessionId}`);

                    if (sessionId) {
                        // Generate call summary
                        setTimeout(async () => {
                            const summary = await conversationManager.generateCallSummary(sessionId);
                            if (summary) {
                                console.log('Call summary:', summary);
                                // Here you would send the summary to your Flask API
                                // to update the call log in the database
                            }
                            conversationManager.endConversation(sessionId);
                        }, 1000);
                    }
                    break;

                default:
                    console.log('Unknown event:', data.event);
            }

        } catch (error) {
            console.error('Error processing WebSocket message:', error);
        }
    });

    ws.on('close', () => {
        console.log('WebSocket connection closed');
        if (sessionId) {
            conversationManager.endConversation(sessionId);
        }
    });

    ws.on('error', (error) => {
        console.error('WebSocket error:', error);
    });
});

// Start server
const PORT = process.env.RELAY_PORT || 5001;
server.listen(PORT, () => {
    console.log(`Conversation Relay Service listening on port ${PORT}`);
    console.log(`WebSocket endpoint: ws://localhost:${PORT}/ws/stream`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('Shutting down Conversation Relay Service...');
    wss.close(() => {
        server.close(() => {
            process.exit(0);
        });
    });
});

module.exports = { conversationManager };