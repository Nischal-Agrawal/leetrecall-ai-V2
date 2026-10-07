import { query, withTransaction } from './database.js';

const toNumber = (value) => Number(value || 0);

function mapQuestion(row) {
  return {
    ...row,
    tags: typeof row.tags === 'string'
      ? row.tags.split(',').map((tag) => tag.trim()).filter(Boolean)
      : [],
  };
}

export async function findCredentialsByEmail(email) {
  const normalizedEmail = String(email).trim().toLowerCase();
  const [profileResult, authResult] = await Promise.all([
    query(
      `SELECT id, name, email, password_hash
       FROM users
       WHERE lower(email) = $1`,
      [normalizedEmail],
    ),
    query(
      `SELECT id, username AS name, email, password_hash
       FROM auth_users
       WHERE lower(email) = $1`,
      [normalizedEmail],
    ),
  ]);

  return [...profileResult.rows, ...authResult.rows].filter((user) => user.password_hash);
}

export async function createAccount({ name, email, passwordHash }) {
  const normalizedEmail = String(email).trim().toLowerCase();
  return withTransaction(async (client) => {
    const authAccount = await client.query(
      'SELECT id FROM auth_users WHERE lower(email) = $1 FOR UPDATE',
      [normalizedEmail],
    );
    if (authAccount.rowCount > 0) {
      const error = new Error('User already exists.');
      error.code = 'USER_EXISTS';
      throw error;
    }

    const existingProfile = await client.query(
      'SELECT id, name, email, password_hash FROM users WHERE lower(email) = $1 FOR UPDATE',
      [normalizedEmail],
    );
    if (existingProfile.rows[0]?.password_hash) {
      const error = new Error('User already exists.');
      error.code = 'USER_EXISTS';
      throw error;
    }

    const profile = existingProfile.rowCount > 0
      ? await client.query(
        `UPDATE users SET password_hash = $1
         WHERE id = $2
         RETURNING id, name, email`,
        [passwordHash, existingProfile.rows[0].id],
      )
      : await client.query(
        `INSERT INTO users (name, email, password_hash)
         VALUES ($1, $2, $3)
         RETURNING id, name, email`,
        [name.trim(), normalizedEmail, passwordHash],
      );
    const user = profile.rows[0];
    const username = `user_${user.id}`;

    await client.query(
      `INSERT INTO auth_users (username, email, password_hash)
       VALUES ($1, $2, $3)`,
      [username, normalizedEmail, passwordHash],
    );

    return user;
  });
}

export async function ensureUserProfile({ name, email, passwordHash }) {
  const result = await query(
    `INSERT INTO users (name, email, password_hash)
     VALUES ($1, $2, $3)
     ON CONFLICT (email) DO UPDATE
       SET password_hash = COALESCE(users.password_hash, EXCLUDED.password_hash)
     RETURNING id, name, email`,
    [name, String(email).trim().toLowerCase(), passwordHash],
  );
  return result.rows[0];
}

export async function getUserById(userId) {
  const result = await query(
    'SELECT id, name, email, created_at FROM users WHERE id = $1',
    [userId],
  );
  return result.rows[0] || null;
}

export async function getQuestions(userId) {
  const result = await query(
    `SELECT q.id, q.title, q.platform, q.topic, q.pattern, q.difficulty, q.tags, q.url,
            CASE WHEN $1::integer IS NULL THEN false ELSE EXISTS (
              SELECT 1 FROM solves s
              WHERE s.user_id = $1 AND s.question_id = q.id
            ) END AS solved
     FROM questions q
     ORDER BY q.id`,
    [userId ?? null],
  );
  return result.rows.map(mapQuestion);
}

export async function getSolves(userId) {
  const result = await query(
    `SELECT id, user_id, question_id, solved_at, time_taken_minutes,
            wrong_attempts, hints_used, confidence_score
     FROM solves
     WHERE user_id = $1
     ORDER BY solved_at DESC, id DESC`,
    [userId],
  );
  return result.rows.map((row) => ({
    id: row.id,
    userId: row.user_id,
    questionId: row.question_id,
    solvedAt: row.solved_at,
    timeTakenMinutes: row.time_taken_minutes,
    wrongAttempts: row.wrong_attempts,
    hintsUsed: row.hints_used,
    confidenceScore: row.confidence_score,
  }));
}

export async function createSolve(userId, values) {
  const result = await query(
    `INSERT INTO solves
       (user_id, question_id, time_taken_minutes, wrong_attempts, hints_used, confidence_score)
     VALUES ($1, $2, $3, $4, $5, $6)
     RETURNING id, user_id, question_id, solved_at, time_taken_minutes,
               wrong_attempts, hints_used, confidence_score`,
    [userId, values.questionId, values.timeTakenMinutes, values.wrongAttempts, values.hintsUsed, values.confidenceScore],
  );
  const row = result.rows[0];
  return {
    id: row.id,
    userId: row.user_id,
    questionId: row.question_id,
    solvedAt: row.solved_at,
    timeTakenMinutes: row.time_taken_minutes,
    wrongAttempts: row.wrong_attempts,
    hintsUsed: row.hints_used,
    confidenceScore: row.confidence_score,
  };
}

export async function getRevisions(userId) {
  const result = await query(
    `SELECT id, user_id, question_id, revised_at, revision_quality
     FROM revisions
     WHERE user_id = $1
     ORDER BY revised_at DESC, id DESC`,
    [userId],
  );
  return result.rows.map((row) => ({
    id: row.id,
    userId: row.user_id,
    questionId: row.question_id,
    revisedAt: row.revised_at,
    revisionQuality: row.revision_quality,
  }));
}

export async function createRevision(userId, values) {
  const result = await query(
    `INSERT INTO revisions (user_id, question_id, revision_quality)
     VALUES ($1, $2, $3)
     RETURNING id, user_id, question_id, revised_at, revision_quality`,
    [userId, values.questionId, values.revisionQuality],
  );
  const row = result.rows[0];
  return {
    id: row.id,
    userId: row.user_id,
    questionId: row.question_id,
    revisedAt: row.revised_at,
    revisionQuality: row.revision_quality,
  };
}

export async function getPredictionQuestions(userId) {
  const result = await query(
    `WITH latest_solves AS (
       SELECT DISTINCT ON (question_id)
              question_id, solved_at, wrong_attempts, hints_used, confidence_score
       FROM solves
       WHERE user_id = $1
       ORDER BY question_id, solved_at DESC NULLS LAST, id DESC
     ), revision_counts AS (
       SELECT question_id, count(*)::integer AS revision_count
       FROM revisions
       WHERE user_id = $1
       GROUP BY question_id
     )
     SELECT q.id, q.title, q.platform, q.topic, q.pattern, q.difficulty, q.tags, q.url,
            s.solved_at,
            GREATEST(0, CURRENT_DATE - s.solved_at::date)::integer AS days_since_solved,
            COALESCE(s.wrong_attempts, 0)::integer AS wrong_attempts,
            COALESCE(s.hints_used, 0)::integer AS hints_used,
            CASE WHEN COALESCE(s.confidence_score, 0.5) <= 1
                 THEN COALESCE(s.confidence_score, 0.5) * 10
                 ELSE s.confidence_score END AS confidence_score,
            COALESCE(r.revision_count, 0)::integer AS revision_count
     FROM latest_solves s
     JOIN questions q ON q.id = s.question_id
     LEFT JOIN revision_counts r ON r.question_id = q.id
     ORDER BY q.id`,
    [userId],
  );
  return result.rows.map((row) => ({
    ...mapQuestion(row),
    question_id: row.id,
    days_since_solved: toNumber(row.days_since_solved),
    wrong_attempts: toNumber(row.wrong_attempts),
    hints_used: toNumber(row.hints_used),
    confidence_score: toNumber(row.confidence_score),
    revision_count: toNumber(row.revision_count),
  }));
}

export async function getTopicMastery(userId) {
  const result = await query(
    `SELECT q.topic,
            count(DISTINCT q.id)::integer AS total_questions,
            count(DISTINCT s.question_id)::integer AS solved_questions,
            CASE WHEN count(DISTINCT q.id) = 0 THEN 0
                 ELSE round(100.0 * count(DISTINCT s.question_id) / count(DISTINCT q.id), 2)
            END AS mastery
     FROM questions q
     LEFT JOIN solves s ON s.question_id = q.id AND s.user_id = $1
     GROUP BY q.topic
     ORDER BY mastery DESC, q.topic`,
    [userId],
  );
  return result.rows;
}

export async function getPatternCoverage(userId) {
  const result = await query(
    `SELECT q.pattern,
            count(DISTINCT q.id)::integer AS total_questions,
            count(DISTINCT s.question_id)::integer AS solved_questions,
            CASE WHEN count(DISTINCT q.id) = 0 THEN 0
                 ELSE round(100.0 * count(DISTINCT s.question_id) / count(DISTINCT q.id), 2)
            END AS coverage
     FROM questions q
     LEFT JOIN solves s ON s.question_id = q.id AND s.user_id = $1
     GROUP BY q.pattern
     ORDER BY coverage DESC, q.pattern`,
    [userId],
  );
  return result.rows;
}

export async function getWeakTopics(userId) {
  const topics = await getTopicMastery(userId);
  return topics
    .slice()
    .sort((left, right) => left.mastery - right.mastery)
    .slice(0, 5)
    .map((item) => ({ ...item, weakness: Number((100 - item.mastery).toFixed(2)) }));
}

export async function getWeakPatterns(userId) {
  const patterns = await getPatternCoverage(userId);
  return patterns
    .slice()
    .sort((left, right) => left.coverage - right.coverage)
    .slice(0, 5)
    .map((item) => ({ ...item, weakness: Number((100 - item.coverage).toFixed(2)) }));
}

export async function getDashboard(userId) {
  const [countsResult, topics, solveDaysResult] = await Promise.all([
    query(
      `SELECT
         (SELECT count(*)::integer FROM users) AS total_users,
         (SELECT count(*)::integer FROM questions) AS total_questions,
         (SELECT count(*)::integer FROM solves) AS overall_solves,
         (SELECT count(*)::integer FROM revisions) AS overall_revisions,
         (SELECT count(DISTINCT question_id)::integer FROM solves WHERE user_id = $1) AS total_solved,
         (SELECT count(*)::integer FROM revisions WHERE user_id = $1) AS total_revisions,
         (SELECT COALESCE(avg(confidence_score), 0)::float FROM solves WHERE user_id = $1) AS confidence_score`,
      [userId],
    ),
    getTopicMastery(userId),
    query(
      `SELECT DISTINCT solved_at::date AS solve_day
       FROM solves
       WHERE user_id = $1 AND solved_at IS NOT NULL
       ORDER BY solve_day DESC
       LIMIT 400`,
      [userId],
    ),
  ]);

  const counts = countsResult.rows[0];
  const masteryValues = topics.map((item) => Number(item.mastery));
  const averageMastery = masteryValues.length
    ? masteryValues.reduce((sum, value) => sum + value, 0) / masteryValues.length
    : 0;
  const weakTopics = topics
    .slice()
    .sort((left, right) => left.mastery - right.mastery)
    .slice(0, 3)
    .map((item) => item.topic);

  let streak = 0;
  const days = solveDaysResult.rows.map((row) => new Date(row.solve_day).toISOString().slice(0, 10));
  const currentDay = new Date().toISOString().slice(0, 10);
  const yesterday = new Date(Date.now() - 86400000).toISOString().slice(0, 10);
  if (days[0] === currentDay || days[0] === yesterday) {
    let expected = new Date(`${days[0]}T00:00:00Z`);
    for (const day of days) {
      if (day !== expected.toISOString().slice(0, 10)) break;
      streak += 1;
      expected = new Date(expected.getTime() - 86400000);
    }
  }

  return {
    totalUsers: counts.total_users,
    totalQuestions: counts.total_questions,
    totalSolved: counts.total_solved,
    totalRevisions: counts.total_revisions,
    overallSolves: counts.overall_solves,
    overallRevisions: counts.overall_revisions,
    solvedQuestions: counts.total_solved,
    recommendationCount: counts.total_solved,
    streak,
    mastery: Number(averageMastery.toFixed(2)),
    weakTopics,
    confidenceScore: Number(counts.confidence_score),
    lastUpdated: new Date().toISOString(),
  };
}