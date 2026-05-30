import json
import os
import time
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path

from agents.collector import fetch_new_videos, fetch_transcript, load_seen, save_seen
from agents.analyzer import analyze_video
from agents.classifier import classify_video
from agents.synthesizer import synthesize_topic
from agents.renderer import render_card, render_topic_page, render_index


def collect_pending():
    channels = json.loads(Path("config/channels.json").read_text(encoding="utf-8"))["channels"]
    seen     = load_seen()
    pending_dir = Path("data/pending")
    pending_dir.mkdir(parents=True, exist_ok=True)
    new_count = 0

    for channel in channels:
        if not channel["active"]:
            continue

        print(f"\n[채널] {channel['name']} 확인 중...")
        new_videos = fetch_new_videos(channel, seen)

        if not new_videos:
            print("  새 영상 없음")
            continue

        print(f"  {len(new_videos)}개 신규 영상 발견")

        for video in new_videos:
            print(f"\n  [영상] {video['title']}")
            time.sleep(random.uniform(8, 15))

            transcript = fetch_transcript(video["id"])
            if not transcript:
                pub_dt = datetime.fromisoformat(video["published"])
                age_hours = (datetime.now(timezone.utc) - pub_dt).total_seconds() / 3600
                if age_hours >= 9:
                    print(f"  [skip] 자막 없음 (업로드 {age_hours:.0f}h 경과 → 포기)")
                    seen.add(video["id"])
                else:
                    print(f"  [retry] 자막 없음 (업로드 {age_hours:.1f}h - 다음 실행에서 재시도)")
                time.sleep(random.uniform(8, 15))
                continue

            # Save to pending
            pending_path = pending_dir / f"{video['id']}.json"
            pending_path.write_text(
                json.dumps({"video": video, "transcript": transcript}, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            # Add to seen immediately so we don't try to download it again
            seen.add(video["id"])
            new_count += 1
            print(f"  [수집 완료] data/pending/{video['id']}.json 저장됨")
            time.sleep(random.uniform(2, 5))

    save_seen(seen)
    print(f"\n[완료] 총 {new_count}개 신규 영상 임시 수집 완료")


def render_dashboard():
    channels = json.loads(Path("config/channels.json").read_text(encoding="utf-8"))["channels"]
    topics   = json.loads(Path("config/topics.json").read_text(encoding="utf-8"))["topics"]

    output_dir = Path("output/html")
    output_dir.mkdir(parents=True, exist_ok=True)
    synthesis_dir = Path("data/synthesis")
    synthesis_dir.mkdir(parents=True, exist_ok=True)

    print("\n[HTML] 생성 중...")
    topic_map = {t["id"]: t for t in topics}
    topic_card_counts = {}
    topic_last_updates = {}

    active_sorted_channels = sorted(
        [ch for ch in channels if ch.get("active", True)],
        key=lambda x: x.get("subscribers", 0),
        reverse=True
    )
    active_channels = [ch["name"] for ch in active_sorted_channels]

    for topic in topics:
        topic_id = topic["id"]
        analyzed_dir = Path(f"data/analyzed/{topic_id}")

        all_cards = []
        analyses = []
        last_update = "1970-01-01T00:00:00+00:00"

        if analyzed_dir.exists():
            entries = []
            for json_file in analyzed_dir.glob("*.json"):
                try:
                    data = json.loads(json_file.read_text(encoding="utf-8"))
                    entries.append(data)
                except Exception as e:
                    print(f"  [warn] {json_file.name} 로드 실패: {e}")

            entries.sort(key=lambda x: x["video"].get("published", ""), reverse=True)
            if entries:
                last_update = entries[0]["video"].get("published", last_update)

            for data in entries:
                all_cards.append(render_card(data["video"], data["analysis"], data["classification"]))
                analyses.append((data["video"].get("published", ""), data["analysis"]))

        topic_last_updates[topic_id] = last_update

        # 종합 인사이트: synthesis_days 이내 영상만 참고
        synthesis_days = topic.get("synthesis_days", 7)
        cutoff = datetime.now(timezone.utc) - timedelta(days=synthesis_days)
        recent_analyses = []
        for pub_str, analysis in analyses:
            try:
                pub_dt = datetime.fromisoformat(pub_str)
                if pub_dt >= cutoff:
                    recent_analyses.append(analysis)
            except Exception:
                recent_analyses.append(analysis)

        synthesis = {}
        synthesis_path = synthesis_dir / f"{topic_id}.json"

        # Load cache first
        if synthesis_path.exists():
            try:
                synthesis = json.loads(synthesis_path.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"  [warn] {topic_id} 종합 캐시 로드 실패: {e}")

        # If cache is missing/empty, and we have enough data and API key, synthesize and save cache
        if not synthesis and len(recent_analyses) >= 2:
            if os.environ.get("GEMINI_API_KEY"):
                print(f"  [synthesize] {topic_id} - 최근 {synthesis_days}일치 {len(recent_analyses)}개 종합 중...")
                synthesis = synthesize_topic(topic, recent_analyses)
                if synthesis:
                    synthesis_path.write_text(json.dumps(synthesis, ensure_ascii=False, indent=2), encoding="utf-8")
            else:
                print(f"  [info] {topic_id} - 최근 {synthesis_days}일치 {len(recent_analyses)}개 존재하나 API 키나 캐시가 없어 종합을 생략합니다.")

        render_topic_page(topic_map[topic_id], "\n".join(all_cards), output_dir,
                          channels=active_channels, synthesis=synthesis)
        topic_card_counts[topic_id] = len(all_cards)

    render_index(topics, topic_card_counts, topic_last_updates, output_dir)
    print("\n[HTML 생성 완료]")


def run():
    # 1. Collect videos to data/pending (API 비용 발생을 방지하기 위해 자막 수집만 수행)
    collect_pending()

