const rateLimitMap = new Map();
const RATE_LIMIT_WINDOW_MS = 60 * 1000; // 1 minute
const MAX_REQUESTS_PER_WINDOW = 10;

function isRateLimited(clientIp) {
  const now = Date.now();
  const userRecord = rateLimitMap.get(clientIp);

  if (rateLimitMap.size > 10000) {
    for (const [ip, record] of rateLimitMap.entries()) {
      if (now - record.startTime > RATE_LIMIT_WINDOW_MS) {
        rateLimitMap.delete(ip);
      }
    }
  }

  if (!userRecord || now - userRecord.startTime > RATE_LIMIT_WINDOW_MS) {
    rateLimitMap.set(clientIp, { count: 1, startTime: now });
    return false;
  }

  if (userRecord.count >= MAX_REQUESTS_PER_WINDOW) {
    return true;
  }

  userRecord.count += 1;
  return false;
}

function isValidOrigin(req) {
  const origin = req.headers['origin'];
  const host = req.headers['host'];
  
  if (!origin) {
    return true;
  }

  try {
    const originUrl = new URL(origin);
    const originHost = originUrl.host;

    if (
      originHost === host ||
      originHost.startsWith('localhost') ||
      originHost.startsWith('127.0.0.1') ||
      (process.env.ALLOWED_DOMAINS && process.env.ALLOWED_DOMAINS.split(',').includes(originHost))
    ) {
      return true;
    }
    return false;
  } catch (e) {
    return false;
  }
}

function validateContents(contents) {
  if (!Array.isArray(contents)) return "Request payload must contain a 'contents' array.";
  if (contents.length === 0) return "Conversation history cannot be empty.";
  if (contents.length > 40) return "Conversation history exceeds maximum limit of 40 messages.";

  let totalChars = 0;
  for (const item of contents) {
    if (!item || typeof item !== 'object') return "Invalid item structure in conversation contents.";
    if (!item.role || !['user', 'model'].includes(item.role)) return "Invalid message role.";
    if (!Array.isArray(item.parts) || item.parts.length === 0) return "Message missing content parts.";
    
    for (const part of item.parts) {
      if (!part || typeof part.text !== 'string') return "Invalid text part format.";
      if (part.text.length > 4000) return "Single message exceeds limit of 4,000 characters.";
      totalChars += part.text.length;
    }
  }

  if (totalChars > 20000) return "Total conversation history exceeds character limit.";
  return null;
}

module.exports = async function handler(req, res) {
  const origin = req.headers['origin'];
  if (origin && isValidOrigin(req)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  }

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed.' });
  }

  if (!isValidOrigin(req)) {
    return res.status(403).json({ error: 'Access forbidden: Request origin not allowed.' });
  }

  const clientIp = (req.headers['x-forwarded-for'] || req.socket?.remoteAddress || '127.0.0.1').split(',')[0].trim();
  if (isRateLimited(clientIp)) {
    return res.status(429).json({ error: 'Too many requests. Please wait a minute before trying again.' });
  }

  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    console.error('Server Configuration Error: GEMINI_API_KEY missing in environment variables.');
    return res.status(500).json({ error: 'Assistant service is currently unavailable. Please try again later.' });
  }

  const { contents } = req.body || {};
  const validationError = validateContents(contents);
  if (validationError) {
    return res.status(400).json({ error: validationError });
  }

  try {
    const SYSTEM_INSTRUCTION = `You are KHeal ( ख्याल ), an empathetic, professional, and highly knowledgeable AI medical assistant designed for health guidance, symptom triage, and wellness advice. Maintain a reassuring, supportive, and clinical tone. Always keep responses clear, well-structured (use bullet points or short sections when helpful), and concise.`;

    const model = 'gemini-3.6-flash';
    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        system_instruction: {
          parts: [{ text: SYSTEM_INSTRUCTION }]
        },
        contents: contents
      })
    });

    if (!response.ok) {
      const errText = await response.text();
      console.error(`Gemini API Error (${response.status}):`, errText);
      return res.status(500).json({ 
        error: 'An error occurred while processing your request with the AI model. Please try again later.' 
      });
    }

    const data = await response.json();
    return res.status(200).json(data);
  } catch (error) {
    console.error('Unhandled error in /api/chat route:', error);
    return res.status(500).json({ error: 'An unexpected internal error occurred. Please try again later.' });
  }
};

