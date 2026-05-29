import requests

channels = {
    "삼프로TV": "UChlv4GSd7OQl3js-jkLOnFA",
    "언더스탠딩": "UCIUni4ScRp4mqPXsxy62L5w"
}

for name, cid in channels.items():
    rss = f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}"
    r = requests.get(rss, timeout=10)
    print(f"{name} (ID: {cid}) RSS status: {r.status_code}")
    if r.status_code == 200:
        print(f"  First 200 chars: {r.text[:200]}")
