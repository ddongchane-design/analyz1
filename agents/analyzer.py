import json
import re
import os
from google import genai

ANALYZE_PROMPT = """
당신은 테크/투자 전문 분석가입니다.
아래 유튜브 영상 자막을 분석해서 반드시 JSON 형식으로만 답하세요.

영상 제목: {title}
채널: {channel}
자막: {transcript}

응답 형식 (JSON만, 다른 텍스트 없이):
{{
  "summary": "3줄 핵심 요약",
  "key_claims": ["핵심 주장 1", "핵심 주장 2", "핵심 주장 3"],
  "data_points": ["언급된 수치/데이터 1", "수치 2"],
  "signal": "bullish",
  "signal_reason": "시그널 판단 근거 1~2줄",
  "key_companies": ["언급 기업/종목 1", "종목 2"],
  "insight": "단순 요약이 아닌 핵심 인사이트 (왜 중요한지, 어떤 의미인지)",
  "action_point": "이 영상을 보고 투자자가 주목해야 할 행동 포인트"
}}

signal 값은 반드시 bullish, bearish, neutral 중 하나여야 합니다.
"""

_client = None


def get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _client


def analyze_video(video: dict, transcript: str) -> dict:
    client = get_client()
    prompt = ANALYZE_PROMPT.format(
        title=video["title"],
        channel=video["channel_name"],
        transcript=transcript[:8000]
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
    return {}
