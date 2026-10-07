import app from '../server/app.js';

export default function handler(request, response) {
  return app(request, response);
}
