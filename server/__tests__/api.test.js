import test from 'node:test';
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { createServer } from 'node:http';

import { createApp } from '../app.js';
import { createLocalCoach } from '../services/aiCoach.js';
import { pool, query } from '../database.js';
import vercelApiHandler from '../../api/index.js';
import { runPythonPredict } from '../services/ml.js';

test('health endpoint returns app metadata', async () => {
  const app = createApp();
  const server = app.listen(0);

  await new Promise((resolve) => server.once('listening', resolve));

  const { port } = server.address();
  const response = await fetch(`http://127.0.0.1:${port}/api/health`);
  const payload = await response.json();

  assert.equal(response.status, 200);
  assert.equal(payload.app, 'LeetRecall AI');

  await new Promise((resolve, reject) => {
    server.close((err) => (err ? reject(err) : resolve()));
  });
});

test('Vercel Node entrypoint serves initialized Express routes', async () => {
  const server = createServer(vercelApiHandler);
  await new Promise((resolve) => server.listen(0, resolve));
  const { port } = server.address();

  try {
    const response = await fetch(`http://127.0.0.1:${port}/api/health`);
    const payload = await response.json();
    assert.equal(response.status, 200);
    assert.equal(payload.database, 'connected');
  } finally {
    await new Promise((resolve, reject) => {
      server.close((error) => (error ? reject(error) : resolve()));
    });
  }
});

test('Vercel ML bridge sends the internal secret and preserves model provenance', async () => {
  let receivedPayload;
  const inferenceServer = createServer(async (request, response) => {
    assert.equal(request.headers['x-ml-internal-secret'], 'test-ml-secret');
    const chunks = [];
    for await (const chunk of request) chunks.push(chunk);
    receivedPayload = JSON.parse(Buffer.concat(chunks).toString('utf8'));
    response.writeHead(200, { 'Content-Type': 'application/json' });
    response.end(JSON.stringify({
      model: 'random-forest',
      source: 'trained-random-forest',
      recommendations: [{ question_id: 7, forget_probability: 0.73 }],
    }));
  });
  await new Promise((resolve) => inferenceServer.listen(0, resolve));
  const { port } = inferenceServer.address();
  const previousEnvironment = {
    vercel: process.env.VERCEL,
    inferenceUrl: process.env.ML_INFERENCE_URL,
    secret: process.env.ML_INTERNAL_SECRET,
  };
  process.env.VERCEL = '1';
  process.env.ML_INFERENCE_URL = `http://127.0.0.1:${port}/api/ml/predict`;
  process.env.ML_INTERNAL_SECRET = 'test-ml-secret';

  try {
    const requestPayload = { questions: [{ id: 7, difficulty: 'Hard', confidence_score: 4 }] };
    const result = await runPythonPredict(null, requestPayload);
    assert.deepEqual(receivedPayload, requestPayload);
    assert.equal(result.source, 'trained-random-forest');
    assert.equal(result.recommendations[0].forget_probability, 0.73);
  } finally {
    if (previousEnvironment.vercel === undefined) delete process.env.VERCEL;
    else process.env.VERCEL = previousEnvironment.vercel;
    if (previousEnvironment.inferenceUrl === undefined) delete process.env.ML_INFERENCE_URL;
    else process.env.ML_INFERENCE_URL = previousEnvironment.inferenceUrl;
    if (previousEnvironment.secret === undefined) delete process.env.ML_INTERNAL_SECRET;
    else process.env.ML_INTERNAL_SECRET = previousEnvironment.secret;
    await new Promise((resolve, reject) => {
      inferenceServer.close((error) => (error ? reject(error) : resolve()));
    });
  }
});

test('local AI fallback is grounded in supplied retention predictions', () => {
  const coach = createLocalCoach([
    { title: 'Word Ladder', topic: 'Graphs', pattern: 'BFS', forget_probability: 0.91 },
  ]);

  assert.equal(coach.source, 'local-insights');
  assert.match(coach.summary, /Word Ladder/);
  assert.match(coach.advice[0], /91%/);
});

test('PostgreSQL signup and solve history feed trained model recommendations', { skip: !pool }, async () => {
  const app = createApp();
  const server = app.listen(0);

  await new Promise((resolve) => server.once('listening', resolve));

  const { port } = server.address();
  const baseUrl = `http://127.0.0.1:${port}`;
  const email = `integration-${randomUUID()}@example.test`;
  let createdUserId;

  try {
    const signupResponse = await fetch(`${baseUrl}/api/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: 'Integration Test', email, password: 'integration-password' }),
    });
    const signup = await signupResponse.json();
    assert.equal(signupResponse.status, 201);
    createdUserId = signup.user.id;
    const headers = { Authorization: `Bearer ${signup.token}`, 'Content-Type': 'application/json' };

    const questionResponse = await fetch(`${baseUrl}/api/questions`, { headers });
    const questions = await questionResponse.json();
    assert.equal(questionResponse.status, 200);
    assert.ok(questions.length >= 1);

    const solveResponse = await fetch(`${baseUrl}/api/solves`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ questionId: questions[0].id, timeTakenMinutes: 20, wrongAttempts: 1, hintsUsed: 0, confidenceScore: 4 }),
    });
    assert.equal(solveResponse.status, 201);

    const revisionResponse = await fetch(`${baseUrl}/api/revisions`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ questionId: questions[0].id, revisionQuality: 0.8 }),
    });
    assert.equal(revisionResponse.status, 201);

    const response = await fetch(`${baseUrl}/api/recommendations`, {
      headers,
    });
    const recommendations = await response.json();

    assert.equal(response.status, 200);
    assert.equal(response.headers.get('x-ml-source'), 'trained-random-forest');
    assert.equal(response.headers.get('x-ml-model'), 'random-forest');
    assert.equal(recommendations.length, 1);
    assert.ok(recommendations.every((item) => item.source === 'trained-random-forest'));
    assert.ok(recommendations.every((item) => Number.isFinite(item.forget_probability)));

    const dashboardResponse = await fetch(`${baseUrl}/api/dashboard`, { headers });
    const dashboard = await dashboardResponse.json();
    assert.equal(dashboard.totalSolved, 1);
    assert.equal(dashboard.totalRevisions, 1);

    const legacyStatsResponse = await fetch(`${baseUrl}/api/dashboard/stats`, { headers });
    const legacyStats = await legacyStatsResponse.json();
    assert.equal(legacyStatsResponse.status, 200);
    assert.ok(legacyStats.total_users > 0);
    assert.ok(legacyStats.total_questions >= questions.length);

    const decayResponse = await fetch(`${baseUrl}/api/knowledge-decay`, { headers });
    assert.equal(decayResponse.status, 200);
    assert.equal(decayResponse.headers.get('x-ml-source'), 'trained-random-forest');

    const plannerResponse = await fetch(`${baseUrl}/api/interview-planner`, { headers });
    assert.equal(plannerResponse.status, 400);
  } finally {
    try {
      if (createdUserId) {
        await query('DELETE FROM recommendations WHERE user_id = $1', [createdUserId]);
        await query('DELETE FROM revisions WHERE user_id = $1', [createdUserId]);
        await query('DELETE FROM solves WHERE user_id = $1', [createdUserId]);
        await query('DELETE FROM auth_users WHERE lower(email) = lower($1)', [email]);
        await query('DELETE FROM users WHERE id = $1', [createdUserId]);
      }
    } finally {
      await new Promise((resolve, reject) => {
        server.close((err) => (err ? reject(err) : resolve()));
      });
    }
  }
});
