import bcrypt from 'bcryptjs';
import { stdin, stdout } from 'node:process';
import { pool, withTransaction } from '../server/database.js';

function readHidden(prompt) {
  if (!stdin.isTTY || typeof stdin.setRawMode !== 'function') {
    throw new Error('Run this command directly in an interactive terminal.');
  }

  return new Promise((resolve, reject) => {
    let value = '';
    const cleanup = () => {
      stdin.off('data', onData);
      stdin.setRawMode(false);
      stdin.pause();
      stdout.write('\n');
    };
    const onData = (buffer) => {
      for (const character of buffer.toString('utf8')) {
        if (character === '\u0003') {
          cleanup();
          reject(new Error('Password reset cancelled.'));
          return;
        }
        if (character === '\r' || character === '\n') {
          cleanup();
          resolve(value);
          return;
        }
        if (character === '\u007f' || character === '\b') {
          value = value.slice(0, -1);
          stdout.write('\b \b');
        } else {
          value += character;
          stdout.write('*');
        }
      }
    };

    stdout.write(prompt);
    stdin.setRawMode(true);
    stdin.resume();
    stdin.on('data', onData);
  });
}

async function main() {
  const email = process.argv[2]?.trim().toLowerCase();
  if (!email) throw new Error('Usage: npm run reset-password -- account@example.com');

  const password = await readHidden('New password (minimum 8 characters): ');
  const confirmation = await readHidden('Confirm new password: ');
  if (password.length < 8) throw new Error('Password must be at least 8 characters.');
  if (password !== confirmation) throw new Error('Passwords do not match.');

  const passwordHash = await bcrypt.hash(password, 10);
  const result = await withTransaction(async (client) => {
    const account = await client.query(
      'SELECT id FROM auth_users WHERE lower(email) = $1 FOR UPDATE',
      [email],
    );
    if (account.rowCount === 0) throw new Error('No authentication account exists for that email.');

    await client.query(
      'UPDATE auth_users SET password_hash = $1 WHERE id = $2',
      [passwordHash, account.rows[0].id],
    );
    const profile = await client.query(
      'UPDATE users SET password_hash = $1 WHERE lower(email) = $2',
      [passwordHash, email],
    );
    return profile.rowCount > 0;
  });

  console.log('Password reset complete. Sign in with the new password.');
  if (!result) console.log('The user profile will be linked automatically after the next successful login.');
}

main()
  .catch((error) => {
    console.error(error.message);
    process.exitCode = 1;
  })
  .finally(async () => {
    await pool?.end();
  });
