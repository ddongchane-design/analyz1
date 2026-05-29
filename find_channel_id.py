import requests, re

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

for handle in ["@waltechman", "@MK_Invest", "@eng_tv"]:
    r = requests.get(f"https://www.youtube.com/{handle}", headers=headers, timeout=10)
    # 여러 패턴 시도
    patterns = [
        r'"channelId":"(UC[^"]+)"',
        r'"externalId":"(UC[^"]+)"',
        r'"browseId":"(UC[^"]+)"',
        r'channel_id=(UC[^&"\']+)',
    ]
    found = None
    for p in patterns:
        m = re.search(p, r.text)
        if m:
            found = m.group(1)
            break
    if found:
        rss = f"https://www.youtube.com/feeds/videos.xml?channel_id={found}"
        rss_r = requests.get(rss, timeout=10)
        print(f"{handle} -> {found} (RSS {rss_r.status_code})")
    else:
        # 디버그: UC로 시작하는 패턴 첫 번째 찾기
        uc = re.findall(r'UC[\w-]{20,}', r.text)
        print(f"{handle} -> 못찾음. UC 패턴 샘플: {list(set(uc))[:3]}")
