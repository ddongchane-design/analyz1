import json
import re
import os
from google import genai

CLASSIFY_PROMPT = """
아래 분석 결과를 보고 가장 적합한 주제 ID를 골라주세요.
반드시 JSON으로만 답하세요.

분석 결과: {analysis}
가능한 주제 목록: {topics}

응답 형식:
{{
  "primary_topic": "주제ID",
  "secondary_topics": ["주제ID2", "주제ID3"],
  "tags": ["세부태그1", "태그2", "태그3"]
}}
"""

_client = None


def get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _client


def classify_video(analysis: dict, topics: list, model=None) -> dict:
    client = get_client()
    prompt = CLASSIFY_PROMPT.format(
        analysis=json.dumps(analysis, ensure_ascii=False),
        topics=json.dumps(topics, ensure_ascii=False)
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    text = response.text
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {"primary_topic": "tech", "secondary_topics": [], "tags": []}
