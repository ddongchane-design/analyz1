import json
import os
import time
import random
from pathlib import Path

from agents.collector import fetch_new_videos, fetch_transcript, load_seen, save_seen
from agents.analyzer import analyze_video
from agents.classifier import classify_video
from agents.renderer import render_card, render_topic_page, render_index


def run():
    channels = json.loads(Path("config/channels.json").read_text(encoding="utf-8"))["channels"]
    topics   = json.loads(Path("config/topics.json").read_text(encoding="utf-8"))["topics"]
    seen     = load_seen()

    topic_cards = {t["id"]: [] for t in topics}
    valid_topic_ids = {t["id"] for t in topics}

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
                print("  [skip] 자막 없음")
                seen.add(video["id"])
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

            card_html = render_card(video, analysis, classification)
            topic_cards[primary].append(card_html)

            # 분석 결과 저장
            result_dir = Path(f"data/analyzed/{primary}")
            result_dir.mkdir(parents=True, exist_ok=True)
            result_path = result_dir / f"{video['id']}.json"
            result_path.write_text(
                json.dumps({"video": video, "analysis": analysis, "classification": classification},
                           ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

            seen.add(video["id"])
            print(f"  [done] {primary} | signal: {analysis.get('signal', '?')}")
            time.sleep(random.uniform(5, 10))

    # HTML 파일 생성
    output_dir = Path("output/html")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n[HTML] 생성 중...")
    topic_map = {t["id"]: t for t in topics}
    topic_card_counts = {}

    active_channels = [ch["name"] for ch in channels if ch["active"]]
    for topic_id, cards in topic_cards.items():
        render_topic_page(topic_map[topic_id], "\n".join(cards), output_dir, channels=active_channels)
        topic_card_counts[topic_id] = len(cards)

    render_index(topics, topic_card_counts, output_dir)

    save_seen(seen)
    print("\n[완료]")
