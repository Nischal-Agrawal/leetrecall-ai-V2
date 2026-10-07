import pandas as pd

questions = [

    {
        "question_id": 1,
        "title": "Two Sum",
        "platform": "LeetCode",
        "topic": "Arrays",
        "pattern": "Hashing",
        "difficulty": "Easy",
        "tags": "array,hashmap",
        "url": "https://leetcode.com/problems/two-sum"
    },

    {
        "question_id": 2,
        "title": "Best Time to Buy and Sell Stock",
        "platform": "LeetCode",
        "topic": "Arrays",
        "pattern": "Kadane Variation",
        "difficulty": "Easy",
        "tags": "array,greedy",
        "url": "https://leetcode.com/problems/best-time-to-buy-and-sell-stock"
    },

    {
        "question_id": 3,
        "title": "Contains Duplicate",
        "platform": "LeetCode",
        "topic": "Arrays",
        "pattern": "Hashing",
        "difficulty": "Easy",
        "tags": "array,set",
        "url": "https://leetcode.com/problems/contains-duplicate"
    },

    {
        "question_id": 4,
        "title": "3Sum",
        "platform": "LeetCode",
        "topic": "Arrays",
        "pattern": "Two Pointers",
        "difficulty": "Medium",
        "tags": "array,two pointers",
        "url": "https://leetcode.com/problems/3sum"
    },

    {
        "question_id": 5,
        "title": "Container With Most Water",
        "platform": "LeetCode",
        "topic": "Arrays",
        "pattern": "Two Pointers",
        "difficulty": "Medium",
        "tags": "array,two pointers",
        "url": "https://leetcode.com/problems/container-with-most-water"
    }
]

df = pd.DataFrame(questions)

from pathlib import Path

output_dir = Path(__file__).parent.parent / "raw"
output_dir.mkdir(exist_ok=True)

output_file = output_dir / "questions.csv"

df.to_csv(output_file, index=False)

print(f"questions.csv generated successfully at: {output_file}")