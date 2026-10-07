import express from 'express';
import cors from 'cors';
import morgan from 'morgan';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { readFile } from 'node:fs/promises';

import {
  createAccount,
  createRevision,
  createSolve,
  ensureUserProfile,
  findCredentialsByEmail,
  getDashboard,
  getPatternCoverage,
  getPredictionQuestions,
  getQuestions,
  getRevisions,
  getSolves,
  getTopicMastery,
  getUserById,
  getWeakPatterns,
  getWeakTopics,
} from './repository.js';
import { query } from './database.js';
import { runPythonPredict } from './services/ml.js';
import { generateCoach, generateInterviewPlan } from './services/aiCoach.js';

const app = express();
let appInitialized = false;

app.use(cors());
app.use(express.json());
app.use(morgan('dev'));
app.set('etag', false);
app.use('/api', (req, res, next) => {
  res.set('Cache-Control', 'no-store');
  next();
});

const JWT_SECRET = process.env.JWT_SECRET || (process.env.NODE_ENV === 'production' ? '' : 'leetrecall-local-development-secret');
if (!JWT_SECRET) throw new Error('JWT_SECRET must be configured in production.');

const createToken = (user) =>
  jwt.sign({ userId: user.id, email: user.email }, JWT_SECRET, { expiresIn: '7d' });

const authMiddleware = (req, res, next) => {
  const authHeader = req.headers.authorization || '';
  const token = authHeader.startsWith('Bearer ') ? authHeader.slice(7) : null;

  if (!token) {
    return res.status(401).json({ message: 'Authentication required.' });
  }

  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    req.user = decoded;
    return next();
  } catch {
    return res.status(401).json({ message: 'Invalid token.' });
  }
};

const formatRecommendations = (result) => (result.recommendations || [])
  .slice(0, 10)
  .map((item) => ({
    ...item,
    question_id: item.question_id || item.questionId || item.id,
    forget_probability: item.forget_probability ?? item.forgetProbability ?? 0,
    source: result.source || 'unknown',
    model: result.model || 'unknown',
  }));

const getRecommendationsForUser = async (userId) => {
  const questions = await getPredictionQuestions(userId);
  const result = await runPythonPredict(null, { questions });
  return formatRecommendations(result);
};

const asyncRoute = (handler) => (req, res, next) => {
  Promise.resolve(handler(req, res, next)).catch(next);
};

const parseContestDataset = (csv) => {
  const [header, ...lines] = csv.trim().split(/\r?\n/);
  const columns = header.split(',');
  return lines.filter(Boolean).map((line) => {
    const values = line.split(',');
    return Object.fromEntries(columns.map((column, index) => [column, values[index]]));
  });
};

const getContestQuestions = async (userId) => {
  const [csv, weakPatterns] = await Promise.all([
    readFile(new URL('../datasets/contest/sample_contest.csv', import.meta.url), 'utf8'),
    getWeakPatterns(userId),
  ]);
  const weakPatternNames = new Set(weakPatterns.map((item) => item.pattern));
  return parseContestDataset(csv)
    .filter((question) => weakPatternNames.has(question.pattern))
    .map((question) => ({
      question: question.question,
      pattern: question.pattern,
      difficulty: question.difficulty,
      reason: 'This contest question matches one of your lowest-coverage patterns.',
    }));
};

export function createApp() {
  if (appInitialized) return app;
  appInitialized = true;

  app.get('/', (req, res) => {
    res.json({
      app: 'LeetRecall AI',
      status: 'ok',
      version: '2.0.0',
      architecture: 'React + Express + Python ML inference',
      endpoints: ['/api', '/api/health', '/api/auth/login', '/api/recommendations'],
    });
  });

  app.get('/api', (req, res) => {
    res.json({
      app: 'LeetRecall AI',
      status: 'ok',
      version: '2.0.0',
      architecture: 'React + Express + Python ML inference',
    });
  });

  app.get('/api/health', (req, res) => {
    return query('SELECT 1')
      .then(() => res.json({
      app: 'LeetRecall AI',
      status: 'healthy',
      database: 'connected',
      uptime: process.uptime(),
      timestamp: new Date().toISOString(),
      }))
      .catch(() => res.status(503).json({ app: 'LeetRecall AI', status: 'unhealthy', database: 'disconnected', message: 'Database connection unavailable.' }));
  });

  app.post('/api/auth/signup', asyncRoute(async (req, res) => {
    const { name, email, password } = req.body || {};

    if (!name?.trim() || !email?.trim() || typeof password !== 'string' || password.length < 8) {
      return res.status(400).json({ message: 'Name, email, and password are required.' });
    }

    try {
      const passwordHash = await bcrypt.hash(password, 10);
      const user = await createAccount({ name, email, passwordHash });
      const token = createToken(user);
      return res.status(201).json({ token, user });
    } catch (error) {
      if (error.code === 'USER_EXISTS' || error.code === '23505') {
        return res.status(409).json({ message: 'User already exists.' });
      }
      throw error;
    }
  }));

  app.post('/api/auth/login', asyncRoute(async (req, res) => {
    const { email, password } = req.body || {};

    if (!email || !password) {
      return res.status(400).json({ message: 'Email and password are required.' });
    }

    const candidates = await findCredentialsByEmail(email);
    let matchedUser = null;
    for (const candidate of candidates) {
      if (await bcrypt.compare(password, candidate.password_hash)) {
        matchedUser = candidate;
        break;
      }
    }
    if (!matchedUser) {
      return res.status(401).json({ message: 'Invalid credentials.' });
    }

    const user = await ensureUserProfile({
      name: matchedUser.name,
      email: matchedUser.email,
      passwordHash: matchedUser.password_hash,
    });
    const token = createToken(user);
    return res.json({
      token,
      user,
    });
  }));

  app.get('/api/auth/me', authMiddleware, asyncRoute(async (req, res) => {
    const user = await getUserById(req.user.userId);
    if (!user) return res.status(404).json({ message: 'User not found.' });
    return res.json({ user });
  }));

  app.get('/api/questions', authMiddleware, asyncRoute(async (req, res) => {
    res.json(await getQuestions(req.user.userId));
  }));

  app.get('/api/solves', authMiddleware, asyncRoute(async (req, res) => {
    res.json(await getSolves(req.user.userId));
  }));

  app.post('/api/solves', authMiddleware, asyncRoute(async (req, res) => {
    const questionId = Number(req.body?.questionId);
    const timeTakenMinutes = Number(req.body?.timeTakenMinutes ?? 30);
    const wrongAttempts = Number(req.body?.wrongAttempts ?? 0);
    const hintsUsed = Number(req.body?.hintsUsed ?? 0);
    let confidenceScore = Number(req.body?.confidenceScore ?? 0.7);
    if (!Number.isInteger(questionId) || !Number.isFinite(timeTakenMinutes) || timeTakenMinutes <= 0
      || !Number.isInteger(wrongAttempts) || wrongAttempts < 0
      || !Number.isInteger(hintsUsed) || hintsUsed < 0
      || !Number.isFinite(confidenceScore) || confidenceScore < 0 || confidenceScore > 10) {
      return res.status(400).json({ message: 'Valid question, time, attempts, hints, and confidence values are required.' });
    }
    if (confidenceScore > 1) confidenceScore /= 10;
    const question = await query('SELECT id FROM questions WHERE id = $1', [questionId]);
    if (question.rowCount === 0) return res.status(404).json({ message: 'Question not found.' });
    const entry = await createSolve(req.user.userId, {
      questionId, timeTakenMinutes, wrongAttempts, hintsUsed, confidenceScore,
    });
    return res.status(201).json(entry);
  }));

  app.get('/api/revisions', authMiddleware, asyncRoute(async (req, res) => {
    res.json(await getRevisions(req.user.userId));
  }));

  app.post('/api/revisions', authMiddleware, asyncRoute(async (req, res) => {
    const questionId = Number(req.body?.questionId);
    let revisionQuality = Number(req.body?.revisionQuality ?? 0.8);
    if (!Number.isInteger(questionId) || !Number.isFinite(revisionQuality) || revisionQuality < 0 || revisionQuality > 10) {
      return res.status(400).json({ message: 'A valid question and revision quality are required.' });
    }
    if (revisionQuality > 1) revisionQuality /= 10;
    const question = await query('SELECT id FROM questions WHERE id = $1', [questionId]);
    if (question.rowCount === 0) return res.status(404).json({ message: 'Question not found.' });
    const entry = await createRevision(req.user.userId, { questionId, revisionQuality });
    return res.status(201).json(entry);
  }));

  app.get('/api/recommendations', authMiddleware, asyncRoute(async (req, res) => {
    const result = await runPythonPredict(req, { questions: await getPredictionQuestions(req.user.userId) });
    res.set('X-ML-Source', result.source || 'unknown');
    res.set('X-ML-Model', result.model || 'unknown');
    if (result.warning) res.set('X-ML-Warning', result.warning);
    res.json(formatRecommendations(result));
  }));

  app.get('/api/knowledge-decay', authMiddleware, asyncRoute(async (req, res) => {
    const result = await runPythonPredict(req, { questions: await getPredictionQuestions(req.user.userId) });
    res.set('X-ML-Source', result.source || 'unknown');
    if (result.warning) res.set('X-ML-Warning', result.warning);
    res.json(formatRecommendations(result));
  }));

  app.get('/api/dashboard', authMiddleware, asyncRoute(async (req, res) => {
    res.json(await getDashboard(req.user.userId));
  }));

  app.get('/api/dashboard/stats', authMiddleware, asyncRoute(async (req, res) => {
    const dashboard = await getDashboard(req.user.userId);
    res.json({
      total_users: dashboard.totalUsers,
      total_questions: dashboard.totalQuestions,
      total_solves: dashboard.overallSolves,
      total_revisions: dashboard.overallRevisions,
    });
  }));

  app.get('/api/topic-mastery', authMiddleware, asyncRoute(async (req, res) => {
    res.json(await getTopicMastery(req.user.userId));
  }));

  app.get('/api/pattern-coverage', authMiddleware, asyncRoute(async (req, res) => {
    res.json(await getPatternCoverage(req.user.userId));
  }));

  app.get('/api/weak-topics', authMiddleware, asyncRoute(async (req, res) => {
    res.json(await getWeakTopics(req.user.userId));
  }));

  app.get('/api/weak-patterns', authMiddleware, asyncRoute(async (req, res) => {
    res.json(await getWeakPatterns(req.user.userId));
  }));

  app.get('/api/contest-analyzer', authMiddleware, asyncRoute(async (req, res) => {
    res.json(await getContestQuestions(req.user.userId));
  }));

  app.get('/api/contest-analysis', authMiddleware, asyncRoute(async (req, res) => {
    const contests = await getContestQuestions(req.user.userId);
    res.json({ contests, averageScore: null, successRate: null, source: 'contest-pattern-analysis' });
  }));

  app.get('/api/contest-ai', authMiddleware, asyncRoute(async (req, res) => {
    const [contests, recommendations] = await Promise.all([
      getContestQuestions(req.user.userId),
      getRecommendationsForUser(req.user.userId),
    ]);
    if (contests.length === 0) return res.json({ review: 'No sample contest questions currently match your weak patterns.', source: 'database-analysis' });
    const relevant = recommendations.filter((item) => contests.some((contest) => contest.pattern === item.pattern));
    const coach = await generateCoach(relevant);
    res.json({ review: coach.summary, advice: coach.advice, provider: coach.provider, source: coach.source, warning: coach.warning, contests });
  }));

  app.get('/api/interview-mode', authMiddleware, (req, res) => {
    res.json({ interviewDate: null, focus: [], plan: [], source: 'not-generated' });
  });

  app.post('/api/interview-mode', authMiddleware, asyncRoute(async (req, res) => {
    const interviewDate = req.body?.interviewDate;
    if (typeof interviewDate !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(interviewDate) || Number.isNaN(Date.parse(`${interviewDate}T00:00:00`))) {
      return res.status(400).json({ message: 'A valid interviewDate in YYYY-MM-DD format is required.' });
    }

    const recommendations = await getRecommendationsForUser(req.user.userId);
    return res.json(await generateInterviewPlan(interviewDate, recommendations));
  }));

  app.get('/api/interview-planner', authMiddleware, asyncRoute(async (req, res) => {
    const interviewDate = req.query.interviewDate || req.query.interview_date;
    if (!interviewDate) return res.status(400).json({ message: 'interviewDate is required.' });
    const recommendations = await getRecommendationsForUser(req.user.userId);
    res.json(await generateInterviewPlan(String(interviewDate), recommendations));
  }));

  app.post('/api/interview-planner', authMiddleware, asyncRoute(async (req, res) => {
    const interviewDate = req.body?.interviewDate || req.body?.interview_date;
    if (!interviewDate) return res.status(400).json({ message: 'interviewDate is required.' });
    const recommendations = await getRecommendationsForUser(req.user.userId);
    res.json(await generateInterviewPlan(String(interviewDate), recommendations));
  }));

  app.get('/api/interview-ai', authMiddleware, asyncRoute(async (req, res) => {
    const interviewDate = req.query.interviewDate || req.query.interview_date;
    if (!interviewDate) return res.status(400).json({ message: 'interviewDate is required.' });
    const recommendations = await getRecommendationsForUser(req.user.userId);
    res.json(await generateInterviewPlan(String(interviewDate), recommendations));
  }));

  app.post('/api/interview-ai', authMiddleware, asyncRoute(async (req, res) => {
    const interviewDate = req.body?.interviewDate || req.body?.interview_date;
    if (!interviewDate) return res.status(400).json({ message: 'interviewDate is required.' });
    const recommendations = await getRecommendationsForUser(req.user.userId);
    res.json(await generateInterviewPlan(String(interviewDate), recommendations));
  }));

  app.get('/api/ai-coach', authMiddleware, asyncRoute(async (req, res) => {
    const recommendations = await getRecommendationsForUser(req.user.userId);
    return res.json(await generateCoach(recommendations));
  }));

  app.get('/api/ai-coach/recommendations', authMiddleware, asyncRoute(async (req, res) => {
    const recommendations = await getRecommendationsForUser(req.user.userId);
    res.json(recommendations.map((item) => ({
      question: item.title,
      forget_probability: item.forget_probability,
      explanation: item.forget_probability > 0.8
        ? 'Very high predicted forgetting risk.'
        : item.forget_probability > 0.5
          ? 'Predicted retention risk is elevated.'
          : 'Predicted retention is stronger; continue spaced revision.',
    })));
  }));

  app.get('/api/dynamic-ai-coach', authMiddleware, asyncRoute(async (req, res) => {
    const recommendations = await getRecommendationsForUser(req.user.userId);
    const coach = await generateCoach(recommendations);
    res.json(recommendations.map((item, index) => ({
      question: item.title,
      forget_probability: item.forget_probability,
      advice: coach.advice[index % Math.max(coach.advice.length, 1)] || coach.summary,
      provider: coach.provider,
      source: coach.source,
    })));
  }));

  app.get('/api/openai-coach', authMiddleware, asyncRoute(async (req, res) => {
    const recommendations = await getRecommendationsForUser(req.user.userId);
    const coach = await generateCoach(recommendations);
    return res.json({
      summary: coach.summary,
      nextSteps: coach.advice,
      provider: coach.provider,
      source: coach.source,
      warning: coach.warning,
    });
  }));

  app.post('/api/ml/predict', authMiddleware, asyncRoute(async (req, res) => {
    const requestedQuestions = Array.isArray(req.body?.questions)
      ? req.body.questions
      : await getPredictionQuestions(req.user.userId);
    const result = await runPythonPredict(req, { questions: requestedQuestions });
    res.json(result);
  }));

  app.get('/api/ml/predict', authMiddleware, asyncRoute(async (req, res) => {
    const result = await runPythonPredict(req, { questions: await getPredictionQuestions(req.user.userId) });
    res.json(result);
  }));

  app.get('/api/users', authMiddleware, asyncRoute(async (req, res) => {
    const result = await query('SELECT id, name, email, created_at FROM users ORDER BY id');
    res.json(result.rows);
  }));

  app.use((error, req, res, next) => {
    console.error('API request failed:', error.message);
    if (res.headersSent) return next(error);
    return res.status(500).json({ message: 'The request could not be completed.' });
  });

  return app;
}

createApp();
export default app;
