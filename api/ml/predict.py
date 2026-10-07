import json
import hmac
import math
import os
import sys
from http.server import BaseHTTPRequestHandler
from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

MODEL_PATH = ROOT / "ml" / "artifacts" / "random_forest_model.pkl"
FEATURE_COLUMNS = [
    "days_since_solved",
    "difficulty",
    "wrong_attempts",
    "hints_used",
    "confidence_score",
    "revision_count",
]
DIFFICULTY_MAPPING = {"Easy": 0, "Medium": 1, "Hard": 2}


def predict(payload):
    questions = payload.get("questions", [])
    if not isinstance(questions, list):
        raise ValueError("questions must be a list")

    if not questions:
        return {
            "model": "random-forest",
            "source": "trained-random-forest",
            "recommendations": [],
        }

    rows = []
    for question in questions:
        difficulty = question.get("difficulty", "Medium")
        if difficulty not in DIFFICULTY_MAPPING:
            raise ValueError(f"Unsupported difficulty: {difficulty}")

        values = {
            "days_since_solved": question.get("days_since_solved", 0),
            "difficulty": DIFFICULTY_MAPPING[difficulty],
            "wrong_attempts": question.get("wrong_attempts", 0),
            "hints_used": question.get("hints_used", 0),
            "confidence_score": question.get("confidence_score", 5),
            "revision_count": question.get("revision_count", 0),
        }
        for name, value in values.items():
            values[name] = float(value)
            if not math.isfinite(values[name]):
                raise ValueError(f"{name} must be a finite number")
        rows.append(values)

    features = pd.DataFrame(rows, columns=FEATURE_COLUMNS)
    model = joblib.load(MODEL_PATH)
    probabilities = model.predict_proba(features)
    classes = list(model.classes_)
    remembered_index = classes.index(1)

    recommendations = []
    for question, probabilities_for_question in zip(questions, probabilities):
        remember_probability = float(probabilities_for_question[remembered_index])
        recommendations.append({
            **question,
            "question_id": question.get("question_id", question.get("id", question.get("title", "Untitled"))),
            "forget_probability": round(1 - remember_probability, 4),
        })

    recommendations.sort(key=lambda item: item["forget_probability"], reverse=True)
    return {
        "model": "random-forest",
        "source": "trained-random-forest",
        "recommendations": recommendations[:10],
    }


def main():
    try:
        payload = json.loads(sys.stdin.read() or "{}")
        if not isinstance(payload, dict):
            raise ValueError("JSON object required")
        response = predict(payload)
    except Exception as error:
        response = {
            "model": "random-forest",
            "source": "unavailable",
            "recommendations": [],
            "warning": f"Trained model inference failed: {error}",
        }

    print(json.dumps(response))


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        expected_secret = os.environ.get("ML_INTERNAL_SECRET", "")
        supplied_secret = self.headers.get("x-ml-internal-secret", "")
        if not expected_secret or not hmac.compare_digest(supplied_secret, expected_secret):
            self.send_error(403, "Forbidden")
            return

        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length <= 0 or content_length > 2_000_000:
                self.send_error(413, "Invalid request size")
                return
            payload = json.loads(self.rfile.read(content_length))
            if not isinstance(payload, dict):
                self.send_error(400, "JSON object required")
                return
            response = predict(payload)
            encoded = json.dumps(response).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(encoded)
        except (json.JSONDecodeError, UnicodeDecodeError):
            self.send_error(400, "Invalid JSON")
        except Exception as error:
            encoded = json.dumps({
                "model": "random-forest",
                "source": "unavailable",
                "recommendations": [],
                "warning": f"Trained model inference failed: {error}",
            }).encode("utf-8")
            self.send_response(503)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(encoded)

    def do_GET(self):
        self.send_error(405, "Method not allowed")

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    main()
