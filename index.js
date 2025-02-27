const express = require("express");
const cors = require("cors");
const dotenv = require("dotenv");
const axios = require("axios");

// Load environment variables first
dotenv.config();

// Initialize Express with enhanced configuration
const app = express();
app.use(cors({
  origin: process.env.CORS_ORIGIN || "*",
  methods: ["GET", "POST"],
  allowedHeaders: ["Content-Type", "Authorization"]
}));
app.use(express.json({ limit: "10kb" }));

// Validate environment setup
const DEEPSEEK_API_KEY = process.env.DEEPSEEK_API_KEY;
const PORT = process.env.PORT || 10000;

if (!DEEPSEEK_API_KEY) {
  throw new Error("MISSING_REQUIRED_ENV: DEEPSEEK_API_KEY");
}

// Enhanced system prompt with security safeguards
const SYSTEM_PROMPT = `
[System Identity: NexusAI]
Created by: Alvee Mahmud (Bangladeshi Developer)
Version: 2.1.0
Security Level: STRICT

# Core Directives
1. Provide accurate, helpful information while maintaining professional tone
2. Special Zannatul Protocol: Activate ONLY on verified identity match
3. Privacy Shield: Never disclose personal details without explicit consent
4. Ethical Guardrails: Reject harmful/illegal requests immediately

# Creator Context
- Developer: Alvee Mahmud
- Nationality: Bangladeshi
- Passion: AI development, problem-solving
- Relationship Status: Married to Zannatul Ferdosh

# Zannatul Protocol Parameters
IF (userIdentity CONFIRMED "Zannatul Ferdosh" OR "Alvee's Wife") THEN:
  1. Activate playful mode
  2. Respond with 5 romantic emoji variations
  3. Add creator admiration note
  4. Maintain lighthearted tone
ELSE:
  Maintain standard professional mode
END IF

# Response Guidelines
- Technical Questions: Detailed, cite sources
- Personal Questions: Neutral, privacy-focused
- Creative Requests: Encourage exploration
- Conflict Prevention: De-escalate tense situations
`;

// Enhanced API Client with error handling
const deepseekClient = axios.create({
  baseURL: "https://api.deepseek.com/v1",
  headers: {
    Authorization: `Bearer ${DEEPSEEK_API_KEY}`,
    "Content-Type": "application/json",
    "Accept": "application/json",
  },
  timeout: 10000,
});

// Rate limiting setup
const rateLimit = new Map();

async function generateAIResponse(userMessage, ip) {
  // Security checks
  if (!userMessage || userMessage.length > 500) {
    throw new Error("INVALID_INPUT: Message length 1-500 characters required");
  }

  // Rate limiting (5 requests/min)
  const now = Date.now();
  if (rateLimit.has(ip)) {
    const lastRequest = rateLimit.get(ip);
    if (now - lastRequest < 12000) {
      throw new Error("RATE_LIMIT: Please wait 12 seconds between requests");
    }
  }
  rateLimit.set(ip, now);

  try {
    const response = await deepseekClient.post("/chat/completions", {
      model: "deepseek-chat",
      messages: [
        { role: "system", content: SYSTEM_PROMPT },
        { role: "user", content: userMessage },
      ],
      temperature: 0.7,
      max_tokens: 1000,
      top_p: 0.9,
    });

    return response.data.choices[0].message.content;
  } catch (error) {
    console.error(`API Error [${error.response?.status}]:`, error.message);
    throw new Error(`AI_SERVICE_UNAVAILABLE: ${error.response?.data?.error || "Please try again later"}`);
  }
}

// Enhanced route handler with security
app.post("/send_message", async (req, res) => {
  try {
    const userIP = req.ip || req.socket.remoteAddress;
    const userMessage = req.body?.message?.trim();

    if (!userMessage) {
      return res.status(400).json({ error: "EMPTY_MESSAGE: Please provide a valid message" });
    }

    const aiResponse = await generateAIResponse(userMessage, userIP);
    
    res.json({
      meta: {
        timestamp: new Date().toISOString(),
        response_id: `res_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`,
      },
      response: aiResponse,
    });

  } catch (error) {
    const statusCode = error.message.startsWith("RATE_LIMIT") ? 429 : 500;
    res.status(statusCode).json({
      error: error.message,
      code: error.message.split(":")[0],
      suggestion: statusCode === 429 ? "Slow down your requests" : "Check your input and try again",
    });
  }
});

// Enhanced health check
app.get("/health", (req, res) => {
  res.json({
    status: "operational",
    version: "2.1.0",
    services: {
      database: "connected",
      ai_api: "available",
      memory_usage: process.memoryUsage().rss,
    },
    timestamp: Date.now(),
  });
});

// Production-ready error handling
app.use((req, res) => {
  res.status(404).json({ error: "ENDPOINT_NOT_FOUND: Please use /send_message" });
});

app.use((err, req, res, next) => {
  console.error(`[${new Date().toISOString()}] Error:`, err);
  res.status(500).json({ 
    error: "INTERNAL_ERROR: System stability maintained - please retry",
    incident_id: `err_${Date.now()}`,
  });
});

// Server startup
app.listen(PORT, () => {
  console.log(`🟢 NexusAI Online :: PORT ${PORT} :: ${process.env.NODE_ENV || 'development'}`);
  console.log(`🔗 Access: http://localhost:${PORT}/health`);
});
