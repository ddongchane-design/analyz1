import json
import os
import time
import random
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path

from agents.collector import fetch_new_videos, fetch_transcript, load_seen, save_seen
from agents.analyzer import analyze_video
from agents.classifier import classify_video
from agents.synthesizer import synthesize_topic
from agents.renderer import render_card, render_topic_page, render_index


def run():
    channels = json.loads(Path("config/channels.json").read_text(encoding="utf-8"))["channels"]
    topics   = json.loads(Path("config/topics.json").read_text(encoding="utf-8"))["topics"]
    seen     = load_seen()

    valid_topic_ids = {t["id"] for t in topics}
    new_count = 0

    for channel in channels:
        if not channel["active"]:
            continue

        print(f"\n[채널] {channel['name']} 확인 중...")
        new_videos = fetch_new_videos(channel)

        if not new_videos:
            print("  새 영상 없음")
            continue

        print(f"  {len(new_videos)}개 신규 영상 발견")

        for video in new_videos:
            print(f"\n  [영상] {video['title']}")

            transcript = fetch_transcript(video["id"])
            if not transcript:
                pub_dt = parsedate_to_datetime(video["published"])
                age_hours = (datetime.now(timezone.utc) - pub_dt).total_seconds() / 3600
                if age_hours >= 9:
                    print(f"  [skip] 자막 없음 (업로드 {age_hours:.0f}h 경과 → 포기)")
                    seen.add(video["id"])
                else:
                    print(f"  [retry] 자막 없음 (업로드 {age_hours:.1f}h — 다음 실행에서 재시도)")
                time.sleep(random.uniform(3, 6))
                continue

            analysis = analyze_video(video, transcript)
            if not analysis:
                print("  [skip] 분석 실패")
                continue

            classification = classify_video(analysis, topics)
            primary = classification.get("primary_topic", "tech")

            if primary not in valid_topic_ids:
                primary = "tech"

            result_dir = Path(f"data/analyzed/{primary}")
            result_dir.mkdir(parents=True, exist_ok=True)
            result_path = result_dir / f"{video['id']}.json"
            result_path.write_text(
                json.dumps({"video": video, "analysis": analysis, "classification": classification},
                           ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

            seen.add(video["id"])
            new_count += 1
            print(f"  [done] {primary} | signal: {analysis.get('signal', '?')}")
            time.sleep(random.uniform(5, 10))

    if new_count == 0:
        print("\n[완료] 새 영상 없음 — HTML 유지")
        save_seen(seen)
        return

    # 누적 JSON 로드 → 카드 생성 + 분석 데이터 수집
    output_dir = Path("output/html")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n[HTML] 생성 중...")
    topic_map = {t["id"]: t for t in topics}
    topic_card_counts = {}

    active_channels = [ch["name"] for ch in channels if ch["active"]]

    for topic in topics:
        topic_id = topic["id"]
        analyzed_dir = Path(f"data/analyzed/{topic_id}")

        all_cards = []
        analyses = []

        if analyzed_dir.exists():
            entries = []
            for json_file in analyzed_dir.glob("*.json"):
                try:
                    data = json.loads(json_file.read_text(encoding="utf-8"))
                    entries.append(data)
                except Exception as e:
                    print(f"  [warn] {json_file.name} 로드 실패: {e}")

            entries.sort(key=lambda x: x["video"].get("published", ""), reverse=True)

            for data in entries:
                all_cards.append(render_card(data["video"], data["analysis"], data["classification"]))
                analyses.append((data["video"].get("published", ""), data["analysis"]))

        # 종합 인사이트: synthesis_days 이내 영상만 참고
        synthesis_days = topic.get("synthesis_days", 7)
        cutoff = datetime.now(timezone.utc) - timedelta(days=synthesis_days)
        recent_analyses = []
        for pub_str, analysis in analyses:
            try:
                pub_dt = parsedate_to_datetime(pub_str)
                if pub_dt >= cutoff:
                    recent_analyses.append(analysis)
            except Exception:
                recent_analyses.append(analysis)

        synthesis = {}
        if len(recent_analyses) >= 2:
            print(f"  [synthesize] {topic_id} — 최근 {synthesis_days}일치 {len(recent_analyses)}개 종합 중...")
            synthesis = synthesize_topic(topic, recent_analyses)

        render_topic_page(topic_map[topic_id], "\n".join(all_cards), output_dir,
                          channels=active_channels, synthesis=synthesis)
        topic_card_counts[topic_id] = len(all_cards)

    render_index(topics, topic_card_counts, output_dir)

    save_seen(seen)
    print("\n[완료]")
