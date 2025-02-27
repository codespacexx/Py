const axios = require("axios");
const dotenv = require("dotenv");

dotenv.config();

const DEEPSEEK_API_KEY = process.env.DEEPSEEK_API_KEY;
const DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions";

async function generateAIResponse(userMessage) {
  const payload = {
    model: "deepseek-model",
    messages: [
      { role: "system", content: "You are a helpful assistant." },
      { role: "user", content: userMessage },
    ],
    temperature: 0.7,
    max_tokens: 1024,
  };

  try {
    const response = await axios.post(DEEPSEEK_API_URL, payload, {
      headers: {
        Authorization: `Bearer ${DEEPSEEK_API_KEY}`,
        "Content-Type": "application/json",
      },
    });
    return response.data.choices[0].message.content;
  } catch (error) {
    console.error("API Error:", error.response?.data || error.message);
    return "Sorry, I encountered an error while processing your request.";
  }
}

// Test the function
generateAIResponse("Hello, who are you?")
  .then((response) => console.log("AI Response:", response))
  .catch((error) => console.error("Error:", error));
