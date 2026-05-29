import json
import re
import os
from google import genai

SYNTHESIZE_PROMPT = """
아래는 동일 주제({topic_label})에 대한 여러 영상 분석 결과입니다.
이를 종합하여 교차 인사이트를 도출해주세요.
반드시 JSON으로만 답하세요.

분석 결과 목록:
{analyses}

응답 형식:
{{
  "cross_insight": "여러 영상에서 공통으로 나타나는 핵심 트렌드나 시그널",
  "consensus": "bullish",
  "divergence": "영상 간 시각 차이나 논쟁 포인트",
  "key_themes": ["공통 테마 1", "테마 2", "테마 3"],
  "watch_list": ["주목 종목/섹터 1", "종목 2"]
}}

consensus 값은 반드시 bullish, bearish, neutral 중 하나여야 합니다.
"""

_client = None


def get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    return _client


def synthesize_topic(topic: dict, analyses: list) -> dict:
    if not analyses:
        return {}

    client = get_client()
    prompt = SYNTHESIZE_PROMPT.format(
        topic_label=topic["label"],
        analyses=json.dumps(analyses, ensure_ascii=False, indent=2)
    )
    
    response_text = None
    for attempt in range(2):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            response_text = response.text
            break
        except Exception as e:
            print(f"  [warn] Gemini 종합 오류 (시도 {attempt+1}/2): {e}")
            if attempt < 1:
                import time
                print("  [retry] 30초 후 종합 재시도...")
                time.sleep(30)
            else:
                return {}

    if not response_text:
        return {}

    match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {}
