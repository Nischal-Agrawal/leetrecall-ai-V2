import 'dotenv/config';

const GEMINI_MODEL = process.env.GEMINI_MODEL || 'gemini-3.5-flash-lite';
const OPENAI_MODEL = process.env.OPENAI_MODEL || 'gpt-4.1-mini';

function safeRecommendations(recommendations) {
  return recommendations.slice(0, 5).map((item) => ({
    title: item.title,
    topic: item.topic,
    pattern: item.pattern,
    difficulty: item.difficulty,
    daysSinceSolved: item.days_since_solved,
    confidenceScore: item.confidence_score,
    revisionCount: item.revision_count,
    forgetProbability: item.forget_probability,
  }));
}

async function requestGeminiJson(prompt, responseSchema) {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) throw new Error('GEMINI_API_KEY is not configured.');

  const response = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-goog-api-key': apiKey,
      },
      body: JSON.stringify({
        contents: [{ parts: [{ text: prompt }] }],
        generationConfig: {
          responseMimeType: 'application/json',
          responseSchema,
          temperature: 0.3,
          maxOutputTokens: 600,
        },
      }),
      signal: AbortSignal.timeout(35000),
    },
  );

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(`Gemini request failed (${response.status}).`);
  }

  const text = payload.candidates?.[0]?.content?.parts
    ?.map((part) => part.text || '')
    .join('')
    .trim();
  if (!text) throw new Error('Gemini returned an empty response.');

  return JSON.parse(text.replace(/^```(?:json)?\s*|\s*```$/g, ''));
}

async function requestOpenAIJson(prompt, responseSchema) {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) throw new Error('OPENAI_API_KEY is not configured.');

  const response = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({
      model: OPENAI_MODEL,
      messages: [
        { role: 'system', content: `Return only a valid JSON object matching this schema: ${JSON.stringify(responseSchema)}` },
        { role: 'user', content: prompt },
      ],
      response_format: { type: 'json_object' },
      temperature: 0.3,
      max_tokens: 600,
    }),
    signal: AbortSignal.timeout(35000),
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(`OpenAI request failed (${response.status}).`);
  const text = payload.choices?.[0]?.message?.content?.trim();
  if (!text) throw new Error('OpenAI returned an empty response.');
  return JSON.parse(text);
}

async function requestAIJson(prompt, responseSchema) {
  const failures = [];
  if (process.env.GEMINI_API_KEY) {
    try {
      return { generated: await requestGeminiJson(prompt, responseSchema), provider: 'Gemini' };
    } catch (error) {
      failures.push(error.message);
    }
  }
  if (process.env.OPENAI_API_KEY) {
    try {
      return { generated: await requestOpenAIJson(prompt, responseSchema), provider: 'OpenAI' };
    } catch (error) {
      failures.push(error.message);
    }
  }
  throw new Error(failures.length ? failures.join(' ') : 'No AI provider API key is configured.');
}

export function createLocalCoach(recommendations) {
  const top = recommendations.slice(0, 3);
  if (top.length === 0) {
    return {
      summary: 'There is not enough solve history to personalize coaching yet.',
      advice: ['Record a solved question with your confidence, mistakes, and hints to start building a revision profile.'],
      provider: 'Local retention insights',
      source: 'local-insights',
    };
  }

  const highestRisk = top[0];
  return {
    summary: `${highestRisk.title} is your highest current retention risk (${Math.round(highestRisk.forget_probability * 100)}%). Focus on ${highestRisk.pattern || highestRisk.topic} in your next revision session.`,
    advice: top.map((item) => (
      `Review ${item.title} (${item.topic}, ${item.pattern}); current estimated forget risk is ${Math.round(item.forget_probability * 100)}%.`
    )),
    provider: 'Local retention insights',
    source: 'local-insights',
  };
}

export async function generateCoach(recommendations) {
  const local = createLocalCoach(recommendations);
  try {
    const { generated, provider } = await requestAIJson(
      `You are a concise DSA revision coach. Use only the measured data. Give one short summary and exactly three short revision actions. Data: ${JSON.stringify(safeRecommendations(recommendations))}`,
      {
        type: 'OBJECT',
        properties: {
          summary: { type: 'STRING' },
          advice: { type: 'ARRAY', items: { type: 'STRING' } },
        },
        required: ['summary', 'advice'],
      },
    );

    if (typeof generated.summary !== 'string' || !Array.isArray(generated.advice)) {
      throw new Error('Gemini response did not match the expected coach format.');
    }

    return {
      summary: generated.summary,
      advice: generated.advice.filter((item) => typeof item === 'string').slice(0, 5),
      provider,
      source: provider.toLowerCase(),
    };
  } catch (error) {
    return {
      ...local,
      warning: `AI provider unavailable; showing data-based guidance. ${error.message}`,
    };
  }
}

export function createLocalInterviewPlan(interviewDate, recommendations) {
  const date = new Date(`${interviewDate}T00:00:00`);
  const daysRemaining = Math.max(0, Math.ceil((date.getTime() - Date.now()) / 86400000));
  const focus = [...new Set(recommendations.map((item) => item.topic || item.pattern).filter(Boolean))].slice(0, 4);
  const focusAreas = focus.length > 0 ? focus : ['Review your recent solve history'];

  return {
    interviewDate,
    focus: focusAreas,
    plan: [
      `Days 1-${Math.max(1, Math.floor(daysRemaining / 2))}: revise the highest-risk problems in ${focusAreas.join(', ')}.`,
      'Use timed practice and explain each solution approach aloud.',
      'Reserve the final days for mixed mock interviews and reviewing mistakes.',
    ],
    provider: 'Local retention insights',
    source: 'local-insights',
  };
}

export async function generateInterviewPlan(interviewDate, recommendations) {
  const local = createLocalInterviewPlan(interviewDate, recommendations);
  const daysRemaining = Math.max(0, Math.ceil((new Date(`${interviewDate}T00:00:00`).getTime() - Date.now()) / 86400000));

  try {
    const { generated, provider } = await requestAIJson(
      `Create a concise DSA interview plan for ${interviewDate}, in ${daysRemaining} days. Prioritize the measured high-risk topics and patterns. Return 2-4 focus strings and 3-5 actionable plan strings. Data: ${JSON.stringify(safeRecommendations(recommendations))}`,
      {
        type: 'OBJECT',
        properties: {
          focus: { type: 'ARRAY', items: { type: 'STRING' } },
          plan: { type: 'ARRAY', items: { type: 'STRING' } },
        },
        required: ['focus', 'plan'],
      },
    );

    if (!Array.isArray(generated.focus) || !Array.isArray(generated.plan)) {
      throw new Error('Gemini response did not match the expected interview plan format.');
    }

    return {
      interviewDate,
      focus: generated.focus.filter((item) => typeof item === 'string').slice(0, 4),
      plan: generated.plan.filter((item) => typeof item === 'string').slice(0, 6),
      provider,
      source: provider.toLowerCase(),
    };
  } catch (error) {
    return {
      ...local,
      warning: `AI provider unavailable; showing data-based plan. ${error.message}`,
    };
  }
}