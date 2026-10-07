from fastapi import FastAPI

from backend.database.connection import engine
from backend.database.base import Base

import backend.models

from fastapi.responses import HTMLResponse
from backend.api.recommendation_api import (
    router as recommendation_router
)

from backend.api.weak_pattern_api import (
    router as weak_pattern_router
)

from backend.api.contest_analyzer_api import (
    router as contest_router
)

from backend.api.weak_topic_api import (
    router as weak_topic_router
)

from backend.api.pattern_coverage_api import (
    router as pattern_router
)

from backend.api.auth_api import router as auth_router

from backend.api.topic_mastery_api import (
    router as topic_mastery_router
)

from backend.api.ai_coach_api import (
    router as ai_coach_router
)

from backend.api.openai_coach_api import (
    router as openai_coach_router
)

from backend.api.dynamic_ai_coach_api import (
    router as dynamic_ai_router
)

from backend.api.contest_ai_api import (
    router as contest_ai_router
)

from backend.api.interview_mode_api import (
    router as interview_mode_router,
)

from backend.api.interview_ai_api import (
    router as interview_ai_router,
)

from backend.api.solve_api import router as solve_router
from backend.api.revision_api import router as revision_router

from backend.api.dashboard_api import router as dashboard_router

from backend.api.user_api import router as user_router
from backend.api.question_api import router as question_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LeetRecall AI",
    version="1.0.0"
)

app.include_router(user_router)
app.include_router(question_router)
app.include_router(solve_router)
app.include_router(revision_router)
app.include_router(dashboard_router)
app.include_router(recommendation_router)
app.include_router(ai_coach_router)
app.include_router(
    openai_coach_router
)
app.include_router(
    dynamic_ai_router
)
app.include_router(
    topic_mastery_router
)
app.include_router(
    pattern_router
)
app.include_router(
    weak_topic_router
)
app.include_router(
    weak_pattern_router
)
app.include_router(
    contest_router
)
app.include_router(
    contest_ai_router
)
app.include_router(
    interview_mode_router
)
app.include_router(
    interview_ai_router
)
app.include_router(auth_router)

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>LeetRecall AI Backend</title>

        <meta http-equiv="refresh"
              content="5;url=https://leetrecall-frontend.onrender.com">

        <style>
            body{
                margin:0;
                font-family:Arial,Helvetica,sans-serif;
                background:#0f172a;
                color:white;
                display:flex;
                justify-content:center;
                align-items:center;
                height:100vh;
            }

            .card{
                width:500px;
                text-align:center;
                background:#1e293b;
                padding:40px;
                border-radius:18px;
                box-shadow:0 0 25px rgba(0,0,0,.35);
            }

            h1{
                color:#60a5fa;
                margin-bottom:10px;
            }

            p{
                color:#cbd5e1;
                line-height:1.6;
            }

            a{
                display:inline-block;
                margin-top:25px;
                padding:14px 28px;
                text-decoration:none;
                background:#2563eb;
                color:white;
                border-radius:10px;
                font-weight:bold;
                transition:.3s;
            }

            a:hover{
                background:#1d4ed8;
            }
        </style>

    </head>

    <body>

        <div class="card">

            <h1>🧠 LeetRecall AI</h1>

            <h2>✅ Backend is Running</h2>

            <p>
                Your backend has successfully started.
                <br><br>
                You will automatically be redirected
                to the frontend in <b>5 seconds</b>.
            </p>

            <a href="https://leetrecall-frontend.onrender.com">
                🚀 Open LeetRecall AI
            </a>

        </div>

    </body>

    </html>
    """