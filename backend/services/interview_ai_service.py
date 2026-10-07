from backend.services.interview_planner_service import (
    generate_interview_plan,
)

from backend.services.openai_coach import (
    generate_ai_advice,
)


def generate_ai_interview_plan(
    interview_date: str,
):

    plan = generate_interview_plan(
        interview_date
    )

    prompt = f"""
You are an expert DSA mentor.

The student's interview date is:
{plan["interview_date"]}

Days Remaining:
{plan["days_remaining"]}

Weak Topics:
{plan["weak_topics"]}

Weak Patterns:
{plan["weak_patterns"]}

Generate a practical preparation roadmap.

Requirements:

1. Divide the preparation into phases.
2. Prioritize weak topics first.
3. Recommend revision before new learning.
4. Reserve the final days for mock interviews.
5. Keep the answer under 300 words.
"""

    advice = generate_ai_advice(
        question=prompt,
        forget_probability=0.90,
    )

    return {
        "plan": plan,
        "ai_plan": advice,
    }