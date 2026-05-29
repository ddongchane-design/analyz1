import feedparser
import json
import yt_dlp
from datetime import datetime, timezone, timedelta
from pathlib import Path

SEEN_PATH = Path("data/seen_videos.json")
COOKIES_PATH = Path("www.youtube.com_cookies.txt")


def load_seen():
    if SEEN_PATH.exists():
        return set(json.loads(SEEN_PATH.read_text(encoding="utf-8")))
    return set()


def save_seen(seen: set):
    SEEN_PATH.write_text(json.dumps(list(seen), ensure_ascii=False), encoding="utf-8")


def fetch_new_videos(channel: dict) -> list:
    """RSS로 새 영상만 가져오기.
    채널을 처음 추가했을 때 기존 영상은 모두 seen 처리하고 건너뜀.
    이후 새로 올라오는 영상만 분석 대상으로 반환.
    """
    seen = load_seen()
    feed = feedparser.parse(channel["rss"])

    feed_ids = [entry.yt_videoid for entry in feed.entries]
    channel_ids_in_seen = any(vid in seen for vid in feed_ids)

    # 이 채널이 처음 추가된 경우 → 기존 영상 전부 seen 처리 후 빈 목록 반환
    if not channel_ids_in_seen:
        for vid in feed_ids:
            seen.add(vid)
        save_seen(seen)
        print(f"  [초기화] 기존 영상 {len(feed_ids)}개 스킵, 이후 새 영상부터 분석")
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(hours=48)

    new_videos = []
    for entry in feed.entries:
        video_id = entry.yt_videoid
        if video_id in seen:
            continue
        published = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
        if published < cutoff:
            seen.add(video_id)
            continue
        new_videos.append({
            "id": video_id,
            "title": entry.title,
            "published": entry.published,
            "channel_name": channel["name"],
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "thumbnail": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
        })

    save_seen(seen)
    return new_videos


def fetch_transcript(video_id: str) -> str:
    """자막 추출 - yt-dlp로 임시 파일에 저장 후 읽기 (한국어 우선, 없으면 영어)"""
    import tempfile, os, glob, re

    url = f"https://www.youtube.com/watch?v={video_id}"

    with tempfile.TemporaryDirectory() as tmpdir:
        ydl_opts = {
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": ["ko", "en"],
            "skip_download": True,
            "quiet": True,
            "no_warnings": True,
            "outtmpl": os.path.join(tmpdir, "%(id)s.%(ext)s"),
            "sleep_interval": 2,
            "max_sleep_interval": 6,
            "extractor_retries": 3,
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
            },
        }
        if COOKIES_PATH.exists():
            ydl_opts["cookiefile"] = str(COOKIES_PATH)

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception:
            pass

        # 저장된 vtt 파일 찾기
        vtt_files = glob.glob(os.path.join(tmpdir, "*.vtt"))
        # 한국어 우선
        vtt_files.sort(key=lambda f: (0 if ".ko." in f else 1))

        for vtt_path in vtt_files:
            raw = Path(vtt_path).read_text(encoding="utf-8")
            text = _parse_vtt(raw)
            if text:
                return text

    return None


def _parse_vtt(raw: str) -> str:
    """VTT 자막에서 텍스트만 추출"""
    import re
    # 타임스탬프 줄 제거
    text = re.sub(r"\d{2}:\d{2}[\d:\.]*\s*-->\s*\S+.*", "", raw)
    # HTML 태그 제거
    text = re.sub(r"<[^>]+>", "", text)
    # WEBVTT 헤더 제거
    text = re.sub(r"^WEBVTT.*$", "", text, flags=re.MULTILINE)
    # 중복 공백/줄바꿈 정리
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    # 연속 중복 제거
    deduped = []
    for line in lines:
        if not deduped or line != deduped[-1]:
            deduped.append(line)
    return " ".join(deduped)
