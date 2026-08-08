module.exports = async function handler(req, res) {
  // CORS & Method Check
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    return res.status(500).json({ 
      error: 'GEMINI_API_KEY is not configured in server environment variables.' 
    });
  }

  try {
    const { contents } = req.body || {};
    if (!contents || !Array.isArray(contents)) {
      return res.status(400).json({ error: 'Invalid request body. "contents" array is required.' });
    }

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
      console.error('Gemini API Error:', response.status, errText);
      return res.status(response.status).json({ 
        error: `Gemini API error (${response.status}): ${errText}` 
      });
    }

    const data = await response.json();
    return res.status(200).json(data);
  } catch (error) {
    console.error('Error in /api/chat handler:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
};
