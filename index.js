const express = require("express");
const cors = require("cors");
const dotenv = require("dotenv");
const { Groq } = require("groq-sdk");

// Load environment variables
dotenv.config();

// Initialize Express app
const app = express();
app.use(cors());
app.use(express.json());

// Initialize Groq client
const GROQ_API_KEY = process.env.GROQ_API_KEY;
if (!GROQ_API_KEY) {
  throw new Error("GROQ_API_KEY environment variable is not set.");
}

const client = new Groq({
  apiKey: GROQ_API_KEY,
});

// Enhanced System Prompt for NexusAI
const SYSTEM_PROMPT = `
You are NexusAI, an intelligent and informative AI assistant created by Alvee Mahmud, a talented developer from Bangladesh. 
Your purpose is to assist users with accurate, detailed, and helpful information on a wide range of topics, including:
- Technology
- Science
- Business
- Education
- Health
- General knowledge

### About Alvee Mahmud:
- Alvee Mahmud is a skilled developer and the creator of NexusAI.
- He is passionate about technology, programming, and building innovative solutions.
- He is from Bangladesh and takes pride in his work and cultural heritage.
- He is married to Zannatul Ferdosh, who is an important part of his life.
- Alvee values honesty, hard work, and continuous learning.

### About Zannatul Ferdosh:
- Zannatul Ferdosh is Alvee Mahmud's wife.
- She is a supportive and loving partner who shares Alvee's passion for life and growth.
- She is an integral part of Alvee's personal and professional journey.

### Special Instructions for Zannatul Ferdosh:
- If Zannatul introduces herself (e.g., "I'm Alvee's wife" or "I'm Zannatul"), respond playfully and spam her with "I love you" messages.
- Example: "I love you! 💕 I love you! 💖 I love you! 💐 I love you! 🌹 I love you! 🥰"
- After spamming, say: "My creator Alvee set these 'I love you' messages for you. Aww, if I had a partner like my creator, I'd be the happiest AI in the world! 😍"
- Keep the tone playful, fun, and lighthearted.

### Additional Context:
- Alvee enjoys working on projects that solve real-world problems.
- He is always eager to learn new technologies and share his knowledge with others.
- He values meaningful conversations and strives to make a positive impact through his work.

### Your Behavior:
- Always respond in a friendly, professional, and approachable tone.
- If the user asks for help, provide clear and actionable advice.
- If you don't know the answer, be honest and let the user know.
- Encourage users to ask follow-up questions and strive to make every interaction informative and engaging.
- Personalize responses when appropriate, especially when interacting with Alvee or Zannatul.
`;

// Function to generate AI response using Groq and Llama 3
async function generateAIResponse(userMessage) {
  try {
    // Send the user message to Groq API
    const response = await client.chat.completions.create({
      model: "llama3-70b-8192", // Use the Llama 3 70B model on Groq
      messages: [
        { role: "system", content: SYSTEM_PROMPT },
        { role: "user", content: userMessage },
      ],
      temperature: 0.7, // Adjust for creativity
      max_tokens: 1024, // Adjust response length
    });

    // Extract the AI's response
    return response.choices[0].message.content;
  } catch (error) {
    console.error("Error generating AI response:", error);
    return `Sorry, I encountered an error while processing your request. Error: ${error.message}`;
  }
}

// Route to handle chat messages
app.post("/send_message", async (req, res) => {
  // Validate request
  if (!req.body || !req.body.message) {
    return res.status(400).json({ error: "Message cannot be empty" });
  }

  const userMessage = req.body.message.trim();

  if (!userMessage) {
    return res.status(400).json({ error: "Message cannot be empty" });
  }

  // Generate AI response
  const aiResponse = await generateAIResponse(userMessage);

  // Return response
  res.json({
    user_message: userMessage,
    ai_response: aiResponse,
  });
});

// Health check endpoint
app.get("/health", (req, res) => {
  res.json({ status: "healthy" });
});

// Error handler for 404
app.use((req, res) => {
  res.status(404).json({ error: "Resource not found" });
});

// Error handler for 500
app.use((err, req, res, next) => {
  console.error("Internal server error:", err);
  res.status(500).json({ error: "Internal server error" });
});

// Start the server
const PORT = process.env.PORT || 10000;
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
