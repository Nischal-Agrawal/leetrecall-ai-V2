import 'dotenv/config';
import pg from 'pg';

const { Pool } = pg;
const configuredUrl = process.env.DATABASE_URL;

function createPool() {
  if (!configuredUrl) return null;

  const connectionString = configuredUrl.replace(/^postgresql\+psycopg2:/, 'postgresql:');
  const parsedUrl = new URL(connectionString);
  const isLocal = ['localhost', '127.0.0.1', '::1'].includes(parsedUrl.hostname);
  parsedUrl.searchParams.delete('sslmode');

  return new Pool({
    connectionString: parsedUrl.toString(),
    ssl: isLocal ? undefined : { rejectUnauthorized: false },
    max: process.env.VERCEL ? 1 : 10,
    idleTimeoutMillis: process.env.VERCEL ? 5000 : 30000,
    connectionTimeoutMillis: 8000,
    allowExitOnIdle: true,
  });
}

export const pool = createPool();

export function query(text, values = []) {
  if (!pool) throw new Error('DATABASE_URL is required for database-backed routes.');
  return pool.query(text, values);
}

export async function withTransaction(work) {
  if (!pool) throw new Error('DATABASE_URL is required for database-backed routes.');

  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    const result = await work(client);
    await client.query('COMMIT');
    return result;
  } catch (error) {
    await client.query('ROLLBACK');
    throw error;
  } finally {
    client.release();
  }
}