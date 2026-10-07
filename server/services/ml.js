import { spawn } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '../..');
const pythonScript = path.join(projectRoot, 'api', 'ml', 'predict.py');

const unavailableResult = (warning) => ({
  source: 'unavailable',
  model: 'random-forest',
  recommendations: [],
  warning,
});

export async function runPythonPredict(req, payload = {}) {
  if (process.env.VERCEL) {
    const secret = process.env.ML_INTERNAL_SECRET;
    
    let inferenceUrl = process.env.ML_INFERENCE_URL;
    if (!inferenceUrl) {
      const host = (req && req.headers && req.headers.host) || process.env.VERCEL_URL;
      const protocol = (req && req.headers && req.headers['x-forwarded-proto']) || 'https';
      if (host) {
        inferenceUrl = `${protocol}://${host}/api/ml/predict`;
      }
    }

    if (!secret || !inferenceUrl) {
      return unavailableResult('Vercel ML_INFERENCE_URL and ML_INTERNAL_SECRET must be configured.');
    }

    try {
      const headers = {
        'Content-Type': 'application/json',
        'x-ml-internal-secret': secret,
      };
      if (req && req.headers) {
        if (req.headers.cookie) headers.cookie = req.headers.cookie;
        if (req.headers.authorization) headers.authorization = req.headers.authorization;
        if (req.headers['x-vercel-protection-bypass']) headers['x-vercel-protection-bypass'] = req.headers['x-vercel-protection-bypass'];
      }
      if (process.env.VERCEL_AUTOMATION_BYPASS_SECRET) {
        headers['x-vercel-protection-bypass'] = process.env.VERCEL_AUTOMATION_BYPASS_SECRET;
      }

      const response = await fetch(inferenceUrl, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
        signal: AbortSignal.timeout(45000),
      });
      const result = await response.json();
      if (!response.ok) {
        console.error('Remote Python inference failed with status', response.status, result.warning);
        return unavailableResult(result.warning || `ML function returned HTTP ${response.status}.`);
      }
      if (!Array.isArray(result.recommendations)) {
        console.error('Remote Python inference returned invalid data:', result);
        return unavailableResult('Python inference returned invalid data.');
      }
      return result;
    } catch (error) {
      console.error('Remote Python inference failed:', error.message);
      return unavailableResult('Remote Python inference failed; no prediction was generated.');
    }
  }

  return new Promise((resolve) => {
    const pythonExecutable = process.env.PYTHON || 'python';
    const child = spawn(pythonExecutable, [pythonScript], {
      cwd: projectRoot,
      env: {
        ...process.env,
        PYTHONPATH: `${projectRoot}${path.delimiter}${process.env.PYTHONPATH || ''}`,
      },
    });

    let stdout = '';
    let stderr = '';
    let settled = false;

    const finish = (result) => {
      if (settled) return;
      settled = true;
      resolve(result);
    };

    child.stdout.on('data', (chunk) => {
      stdout += chunk.toString();
    });

    child.stderr.on('data', (chunk) => {
      stderr += chunk.toString();
    });

    child.on('close', (code) => {
      if (code !== 0) {
        console.error('Python inference failed:', stderr || `exit code ${code}`);
        finish(unavailableResult(`Python inference failed${code === null ? '' : ` (exit code ${code})`}; no prediction was generated.`));
        return;
      }

      try {
        const parsed = JSON.parse(stdout || '{}');
        finish(parsed && Array.isArray(parsed.recommendations)
          ? parsed
          : unavailableResult('Python inference returned an invalid response.'));
      } catch {
        console.error('Python inference returned malformed JSON:', stderr);
        finish(unavailableResult('Python inference returned malformed output; no prediction was generated.'));
      }
    });

    child.on('error', (error) => {
      console.error('Unable to start Python inference:', error.message);
      finish(unavailableResult('Python inference could not be started; no prediction was generated.'));
    });

    child.stdin.end(JSON.stringify(payload));
  });
}
