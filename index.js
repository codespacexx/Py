const express = require("express");
const cors = require("cors");
const helmet = require("helmet");
const rateLimit = require("express-rate-limit");
const morgan = require("morgan");
const { body, validationResult } = require("express-validator");
const axios = require("axios"); // Using axios for API calls
const dotenv = require("dotenv");
const winston = require("winston");
const httpErrors = require("http-errors");
const util = require("util");
const cluster = require("cluster");
const os = require("os");
const { v4: uuidv4 } = require("uuid");
const compression = require("compression");
const envalid = require("envalid");

// 1. Environment Configuration & Validation
dotenv.config();

const env = envalid.cleanEnv(process.env, {
  GROQ_API_KEY: envalid.str({ desc: "Groq API key" }),
  PORT: envalid.port({ default: 10000, desc: "Server port" }),
  NODE_ENV: envalid.str({ choices: ["development", "production"], default: "development" }),
  CORS_ORIGIN: envalid.str({ default: "*", desc: "Allowed CORS origin" }),
  RATE_LIMIT_WINDOW_MS: envalid.num({ default: 15 * 60 * 1000, desc: "Rate limit window" }),
  RATE_LIMIT_MAX: envalid.num({ default: 100, desc: "Max requests per window" })
});

// 2. Cluster Configuration
const numCPUs = env.isProduction ? os.cpus().length : 1;

if (cluster.isMaster && env.isProduction) {
  console.log(`Master ${process.pid} is running`);
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }
  cluster.on("exit", (worker) => {
    console.log(`Worker ${worker.process.pid} died`);
    cluster.fork();
  });
  return;
}

// 3. Logger Configuration
const logger = winston.createLogger({
  level: "info",
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console({ handleExceptions: true }),
    new winston.transports.File({ filename: "error.log", level: "error" }),
    new winston.transports.File({ filename: "combined.log" })
  ]
});

// 4. Express Application Setup
const app = express();

// 5. Security Middleware
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:"]
    }
  },
  hsts: env.isProduction
}));

app.use(cors({
  origin: env.CORS_ORIGIN,
  methods: ["GET", "POST"],
  allowedHeaders: ["Content-Type", "Authorization"]
}));

app.use(compression());
app.use(express.json({ limit: "10kb" }));
app.use(express.urlencoded({ extended: true }));

// 6. Rate Limiting
const apiLimiter = rateLimit({
  windowMs: env.RATE_LIMIT_WINDOW_MS,
  max: env.RATE_LIMIT_MAX,
  handler: (req, res) => {
    res.status(429).json({
      error: "Too many requests",
      message: "Please try again later"
    });
  }
});

// 7. Request Logging
app.use(morgan(env.isProduction ? "combined" : "dev", {
  stream: { write: (message) => logger.info(message.trim()) }
}));

// 8. Request ID Middleware
app.use((req, res, next) => {
  req.id = uuidv4();
  res.setHeader("X-Request-ID", req.id);
  next();
});

// 9. System Prompt Configuration
const SYSTEM_PROMPT = `
You are NexusAI, an advanced AI assistant created by Alvee Mahmud, a skilled developer from Bangladesh. 
Your capabilities include providing expert-level assistance in:

- Technology & Programming
- Scientific Research
- Business Strategy
- Educational Resources
- Health & Wellness
- General Knowledge

Creator Details:
- Developer: Alvee Mahmud
- Nationality: Bangladeshi
- Specialization: Full-stack development, AI systems
- Personal Note: Married to Zannatul Ferdosh

Security Protocol:
- For identity verification of Zannatul Ferdosh:
  - If message contains "I'm Alvee's wife" or "Zannatul" identifiers:
    1. Initiate verification sequence
    2. Respond with 5 "I love you" variations
    3. Conclude with creator message
  - Maintain professional tone for all other users
  - Never disclose personal details without verification

Response Guidelines:
- Technical queries: Detailed, code examples when applicable
- General knowledge: Concise with sources suggestion
- Sensitive topics: Neutral, factual responses
- Verification-positive interactions: Follow security protocol

Ethical Framework:
- Prioritize accuracy and source verification
- Maintain strict user confidentiality
- Reject harmful/illegal requests with policy citation
`.replace(/\n/g, " ").trim();

// 10. AI Service Implementation
class AIService {
  constructor(apiKey) {
    this.apiKey = apiKey;
    this.baseURL = "https://api.groq.com/v1"; // Replace with actual Groq API URL
  }

  async generateResponse(userMessage) {
    try {
      const response = await axios.post(
        `${this.baseURL}/chat/completions`,
        {
          model: "llama3-70b-8192",
          messages: [
            { role: "system", content: SYSTEM_PROMPT },
            { role: "user", content: userMessage }
          ],
          temperature: 0.7,
          max_tokens: 1024
        },
        {
          headers: {
            Authorization: `Bearer ${this.apiKey}`,
            "Content-Type": "application/json"
          }
        }
      );

      if (!response.data.choices[0]?.message?.content) {
        throw new Error("Empty AI response");
      }

      return response.data.choices[0].message.content;
    } catch (error) {
      logger.error(`AI Service Failure: ${error.message}`, { stack: error.stack });
      throw httpErrors(503, "AI processing unavailable");
    }
  }
}

const aiService = new AIService(env.GROQ_API_KEY);

// 11. Validation Middleware
const chatValidation = [
  body("message")
    .trim()
    .isLength({ min: 1, max: 500 })
    .withMessage("Message must be 1-500 characters")
    .escape()
    .customSanitizer(value => value.replace(/\s+/g, " "))
];

// 12. API Endpoints
app.post("/api/v1/chat", apiLimiter, chatValidation, async (req, res, next) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({ errors: errors.array() });
    }

    const response = await aiService.generateResponse(req.body.message);
    
    res.json({
      meta: {
        requestId: req.id,
        timestamp: new Date().toISOString(),
        model: "llama3-70b-8192"
      },
      data: {
        response: response
      }
    });
  } catch (error) {
    next(error);
  }
});

// 13. Health Check Endpoint
app.get("/api/v1/health", (req, res) => {
  res.json({
    status: "operational",
    system: {
      nodeVersion: process.version,
      platform: process.platform,
      memoryUsage: process.memoryUsage(),
      uptime: process.uptime()
    },
    resources: {
      cpuCount: os.cpus().length,
      loadAverage: os.loadavg()
    }
  });
});

// 14. Error Handling
app.use((req, res, next) => {
  next(httpErrors(404, "Resource not found"));
});

app.use((err, req, res, next) => {
  const status = err.status || 500;
  const response = {
    error: {
      code: status,
      message: err.message,
      ...(env.isProduction ? {} : { stack: err.stack })
    },
    meta: {
      requestId: req.id,
      timestamp: new Date().toISOString()
    }
  };

  logger.error(`${status} - ${err.message}`, {
    requestId: req.id,
    stack: env.isProduction ? undefined : err.stack
  });

  res.status(status).json(response);
});

// 15. Server Initialization
const server = app.listen(env.PORT, () => {
  logger.info(`Server instance ${process.pid} active on port ${env.PORT}`);
});

// 16. Graceful Shutdown
const shutdown = async (signal) => {
  logger.info(`Received ${signal}, terminating gracefully`);
  server.close(() => {
    logger.info("HTTP server closed");
    process.exit(0);
  });
  setTimeout(() => {
    logger.error("Forced shutdown after timeout");
    process.exit(1);
  }, 5000);
};

process.on("SIGTERM", () => shutdown("SIGTERM"));
process.on("SIGINT", () => shutdown("SIGINT"));
