import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()

if not os.environ.get("GEMINI_API_KEY"):
    raise RuntimeError("GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")

from agents.orchestrator import run

if __name__ == "__main__":
    run()
