from pathlib import Path
from datetime import datetime

# 토픽별 컬러 팔레트 (kinetic-oracle-hub 스타일)
TOPIC_PALETTE = {
    "robot":   {"color": "cyan",   "hex": "#22d3ee", "emoji": "🤖"},
    "economy": {"color": "amber",  "hex": "#fbbf24", "emoji": "📊"},
    "tech":    {"color": "indigo", "hex": "#818cf8", "emoji": "💻"},
    "stock":   {"color": "emerald","hex": "#34d399", "emoji": "📈"},
    "energy":  {"color": "orange", "hex": "#fb923c", "emoji": "⚡"},
}

SIGNAL_STYLE = {
    "bullish": {"label": "BULLISH", "dot": "#10d98a", "bg": "rgba(16,217,138,0.12)", "border": "rgba(16,217,138,0.35)", "text": "#10d98a"},
    "bearish": {"label": "BEARISH", "dot": "#ff4f72", "bg": "rgba(255,79,114,0.12)", "border": "rgba(255,79,114,0.35)", "text": "#ff4f72"},
    "neutral": {"label": "NEUTRAL", "dot": "#f5c842", "bg": "rgba(245,200,66,0.12)",  "border": "rgba(245,200,66,0.35)",  "text": "#f5c842"},
}

# ───────────────────────── SHARED HEAD ─────────────────────────

SHARED_HEAD = """
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <script src="https://cdn.tailwindcss.com?plugins=typography"></script>
  <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;800&family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">
  <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet">
  <script>
    tailwind.config = {
      darkMode: "class",
      theme: {
        extend: {
          colors: {
            bg:      "#0b1326",
            surface: "#101931",
            card:    "#16213e",
          }
        }
      }
    }
  </script>
  <style>
    body { font-family: 'Noto Sans KR', sans-serif; }
    .font-manrope { font-family: 'Manrope', sans-serif; }
    .material-symbols-outlined { font-size: inherit; vertical-align: middle; }
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 3px; }
  </style>
"""

# ───────────────────────── INDEX PAGE ─────────────────────────

INDEX_TEMPLATE = """<!DOCTYPE html>
<html lang="ko" class="dark">
<head>
  <title>YouTube Insight | Dashboard</title>
  {head}
</head>
<body class="bg-bg text-white min-h-screen relative">

  <!-- Glowing Blobs -->
  <div class="fixed top-[-10%] left-[-10%] w-[40%] h-[40%] bg-purple-500/20 blur-[150px] rounded-full pointer-events-none"></div>
  <div class="fixed bottom-[-10%] right-[-10%] w-[30%] h-[40%] bg-emerald-400/15 blur-[150px] rounded-full pointer-events-none"></div>
  <div class="fixed top-[30%] right-[5%] w-[20%] h-[20%] bg-amber-400/10 blur-[120px] rounded-full pointer-events-none"></div>

  <main class="relative z-10 max-w-[1400px] mx-auto px-8 py-16 flex flex-col items-center">

    <!-- Hero -->
    <div class="text-center mb-16 select-none">
      <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800/50 border border-slate-700 mb-6 text-xs font-semibold text-slate-300 tracking-wider">
        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> SYSTEM ONLINE
      </div>
      <h1 class="font-manrope text-5xl md:text-6xl font-extrabold tracking-tighter mb-4 text-transparent bg-clip-text bg-gradient-to-r from-purple-300 via-white to-amber-200 pb-2">
        YouTube Insight
      </h1>
      <p class="text-lg text-slate-400 max-w-xl mx-auto font-light leading-relaxed">
        AI가 유튜브 채널을 실시간 분석해<br>투자 인사이트를 자동으로 추출합니다.
      </p>
    </div>

    <!-- Topic Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-5 w-full mb-6">
      {topic_cards}
    </div>

    <p class="text-xs text-slate-600 mt-2">마지막 업데이트: {updated}</p>
  </main>
</body>
</html>"""

INDEX_CARD = """
<a href="{topic_id}.html" class="group relative bg-card/60 backdrop-blur-xl border border-slate-600/40 p-7 rounded-[2rem] flex flex-col transition-all duration-500 hover:-translate-y-2 hover:border-{color}-400/50 hover:shadow-[0_10px_40px_{shadow}]">
  <div class="absolute inset-0 bg-gradient-to-br from-{color}-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-[2rem]"></div>
  <div class="w-14 h-14 rounded-2xl flex items-center justify-center border mb-4 bg-{color}-500/20 text-{color}-400 border-{color}-400/30 shadow-[0_0_15px_{shadow}] text-3xl transition-transform duration-500 group-hover:scale-110">
    <span class="material-symbols-outlined">{icon}</span>
  </div>
  <div class="text-xl font-bold text-slate-100 mb-1 group-hover:text-{color}-300 transition-colors">{emoji} {label}</div>
  <div class="text-slate-400 text-sm font-light flex-grow">{count}개 영상 분석됨</div>
  <div class="mt-5 flex items-center text-sm font-semibold opacity-50 group-hover:opacity-100 transition-all group-hover:translate-x-1 text-{color}-400">
    인사이트 보기 <span class="material-symbols-outlined text-base ml-1">arrow_forward</span>
  </div>
</a>"""

TOPIC_ICON = {
    "robot": "precision_manufacturing",
    "economy": "query_stats",
    "tech": "memory",
    "stock": "candlestick_chart",
    "energy": "bolt",
}

TOPIC_SHADOW = {
    "robot":   "rgba(34,211,238,0.15)",
    "economy": "rgba(251,191,36,0.15)",
    "tech":    "rgba(129,140,248,0.15)",
    "stock":   "rgba(52,211,153,0.15)",
    "energy":  "rgba(251,146,60,0.15)",
}

# ───────────────────────── TOPIC PAGE ─────────────────────────

TOPIC_TEMPLATE = """<!DOCTYPE html>
<html lang="ko" class="dark">
<head>
  <title>YouTube Insight | {topic_label}</title>
  {head}
</head>
<body class="bg-bg text-white min-h-screen relative">

  <!-- Glowing Blobs -->
  <div class="fixed top-[-10%] left-[-5%] w-[35%] h-[35%] bg-{color}-500/10 blur-[150px] rounded-full pointer-events-none"></div>
  <div class="fixed bottom-[-10%] right-[-5%] w-[25%] h-[35%] bg-purple-500/10 blur-[150px] rounded-full pointer-events-none"></div>

  <!-- Header -->
  <header class="sticky top-0 z-30 bg-bg/80 backdrop-blur-xl border-b border-slate-800/60">
    <div class="max-w-[1400px] mx-auto px-8 py-4 flex items-center justify-between">
      <div class="flex items-center gap-4">
        <a href="index.html" class="flex items-center gap-1 text-sm text-slate-400 hover:text-white transition-colors px-3 py-1.5 rounded-lg border border-slate-700 hover:border-slate-600 bg-slate-800/50">
          <span class="material-symbols-outlined text-base">arrow_back</span> 전체
        </a>
        <div>
          <h1 class="font-manrope text-lg font-bold text-transparent bg-clip-text bg-gradient-to-r from-{color}-300 to-white">
            {emoji} {topic_label}
          </h1>
          <p class="text-xs text-slate-500">AI 분석 인사이트</p>
        </div>
      </div>
      <span class="text-xs text-slate-600">{updated}</span>
    </div>

    <!-- Filter Bar -->
    <div class="max-w-[1400px] mx-auto px-8 pb-3 flex items-center gap-2 flex-wrap">
      <span class="text-xs text-slate-500 mr-1">채널</span>
      <button onclick="filterCh(this,'all')" data-ch="all"
        class="ch-btn text-xs px-3 py-1 rounded-full border border-{color}-400/50 bg-{color}-500/15 text-{color}-300 font-semibold transition-all">
        전체
      </button>
      {channel_btns}
      <div class="ml-auto flex gap-2">
        <button onclick="filterSig(this,'bullish')" data-sig="bullish"
          class="sig-btn text-[11px] px-3 py-1 rounded-full border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/15 transition-all">
          ▲ 강세
        </button>
        <button onclick="filterSig(this,'bearish')" data-sig="bearish"
          class="sig-btn text-[11px] px-3 py-1 rounded-full border border-rose-500/30 text-rose-400 hover:bg-rose-500/15 transition-all">
          ▼ 약세
        </button>
        <button onclick="filterSig(this,'neutral')" data-sig="neutral"
          class="sig-btn text-[11px] px-3 py-1 rounded-full border border-amber-500/30 text-amber-400 hover:bg-amber-500/15 transition-all">
          ● 중립
        </button>
      </div>
    </div>
  </header>

  <main class="relative z-10 max-w-[1400px] mx-auto px-8 py-10">
    <div id="cardGrid" class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-5">
      {cards}
    </div>
    <div id="emptyMsg" class="hidden text-center py-24 text-slate-600">
      <span class="material-symbols-outlined text-5xl mb-3 block opacity-30">inbox</span>
      해당 조건의 영상이 없습니다.
    </div>
  </main>

  <script>
    let activeCh = 'all', activeSig = null;
    function filterCh(btn, ch) {{
      document.querySelectorAll('.ch-btn').forEach(b => b.classList.remove('!bg-{color}-500/15','!border-{color}-400/50','!text-{color}-300','font-semibold'));
      btn.classList.add('font-semibold');
      activeCh = ch; applyFilter();
    }}
    function filterSig(btn, sig) {{
      if (activeSig === sig) {{
        btn.classList.remove('!bg-emerald-500/15','!bg-rose-500/15','!bg-amber-500/15');
        activeSig = null;
      }} else {{
        document.querySelectorAll('.sig-btn').forEach(b => b.classList.remove('!bg-emerald-500/15','!bg-rose-500/15','!bg-amber-500/15'));
        const map = {{bullish:'!bg-emerald-500/15', bearish:'!bg-rose-500/15', neutral:'!bg-amber-500/15'}};
        btn.classList.add(map[sig]);
        activeSig = sig;
      }}
      applyFilter();
    }}
    function applyFilter() {{
      let visible = 0;
      document.querySelectorAll('.insight-card').forEach(c => {{
        const ok = (activeCh==='all'||c.dataset.ch===activeCh) && (!activeSig||c.dataset.sig===activeSig);
        c.style.display = ok ? '' : 'none';
        if (ok) visible++;
      }});
      document.getElementById('emptyMsg').classList.toggle('hidden', visible > 0);
    }}
  </script>
</body>
</html>"""

# ───────────────────────── CARD ─────────────────────────

CARD_TEMPLATE = """
<div class="insight-card group bg-card/60 backdrop-blur-xl border border-slate-700/50 rounded-[1.5rem] p-6 flex flex-col gap-4 transition-all duration-300 hover:-translate-y-1 hover:border-{color}-400/40 hover:shadow-[0_8px_32px_{shadow}] relative overflow-hidden"
     data-ch="{ch_key}" data-sig="{signal}">
  <div class="absolute inset-0 bg-gradient-to-br from-{color}-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-[1.5rem] pointer-events-none"></div>

  <!-- Top: thumbnail + title + signal -->
  <div class="flex gap-3 items-start">
    <img src="{thumbnail}" class="w-24 h-[60px] rounded-xl object-cover bg-slate-800 flex-shrink-0" onerror="this.style.display='none'">
    <div class="flex-1 min-w-0">
      <h3 class="font-bold text-slate-100 text-[14px] leading-snug line-clamp-2 group-hover:text-{color}-200 transition-colors">{title}</h3>
      <div class="flex items-center gap-2 mt-1.5 flex-wrap">
        <span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-{color}-500/15 text-{color}-300 border border-{color}-400/30">{channel}</span>
        <span class="text-[11px] text-slate-500">{date}</span>
      </div>
    </div>
    <div class="flex-shrink-0">
      <span class="inline-flex items-center gap-1.5 text-[11px] font-bold px-2.5 py-1 rounded-lg border"
        style="background:{sig_bg};color:{sig_text};border-color:{sig_border}">
        <span class="w-1.5 h-1.5 rounded-full" style="background:{sig_dot}"></span>
        {sig_label}
      </span>
    </div>
  </div>

  <!-- Insight -->
  <div class="bg-gradient-to-br from-slate-800/60 to-slate-900/40 border border-slate-700/50 rounded-xl p-4">
    <p class="text-[10px] font-bold tracking-widest text-{color}-400 mb-2 uppercase">Insight</p>
    <p class="text-[13px] text-slate-300 leading-relaxed">{insight}</p>
  </div>

  <!-- Key Claims -->
  <div class="flex flex-col gap-1.5">
    {claims_html}
  </div>

  <!-- Action Point -->
  <div class="bg-amber-400/5 border border-amber-400/20 rounded-xl p-3.5">
    <p class="text-[10px] font-bold tracking-widest text-amber-300 mb-1.5 uppercase">Action Point</p>
    <p class="text-[13px] text-slate-200 leading-relaxed">{action_point}</p>
  </div>

  <!-- Tags + Link -->
  <div class="flex items-center justify-between gap-2 pt-1">
    <div class="flex flex-wrap gap-1.5">{tags_html}</div>
    <a href="{url}" target="_blank"
      class="flex-shrink-0 flex items-center gap-1 text-[12px] font-semibold px-4 py-2 rounded-xl bg-{color}-500/15 hover:bg-{color}-500/25 text-{color}-300 border border-{color}-400/30 hover:border-{color}-400/60 transition-all">
      보기 <span class="material-symbols-outlined text-sm">arrow_forward</span>
    </a>
  </div>
</div>"""

CLAIM_HTML = '<div class="flex items-start gap-2 text-[12px] text-slate-400"><span class="text-slate-600 mt-0.5 flex-shrink-0">▸</span><span>{}</span></div>'
TAG_HTML   = '<span class="px-2 py-0.5 rounded-md text-[10px] bg-slate-800/80 border border-slate-700/60 text-slate-500">{}</span>'


def render_card(video: dict, analysis: dict, classification: dict) -> str:
    topic_id = classification.get("primary_topic", "tech")
    pal  = TOPIC_PALETTE.get(topic_id, TOPIC_PALETTE["tech"])
    color = pal["color"]
    shadow = TOPIC_SHADOW.get(topic_id, "rgba(129,140,248,0.15)")

    sig  = analysis.get("signal", "neutral")
    ss   = SIGNAL_STYLE.get(sig, SIGNAL_STYLE["neutral"])

    claims_html = "\n".join(CLAIM_HTML.format(c) for c in analysis.get("key_claims", []))
    tags_html   = "".join(TAG_HTML.format(t)   for t in classification.get("tags", []))

    return CARD_TEMPLATE.format(
        color=color,
        shadow=shadow,
        ch_key=video.get("channel_name", "").replace(" ", "_"),
        signal=sig,
        thumbnail=video.get("thumbnail", ""),
        title=video["title"],
        channel=video["channel_name"],
        date=video["published"][:10],
        url=video["url"],
        sig_bg=ss["bg"], sig_text=ss["text"], sig_border=ss["border"], sig_dot=ss["dot"], sig_label=ss["label"],
        insight=analysis.get("insight", ""),
        claims_html=claims_html,
        action_point=analysis.get("action_point", ""),
        tags_html=tags_html,
    )


def render_topic_page(topic: dict, cards_html: str, output_dir: Path, channels: list = None):
    tid   = topic["id"]
    pal   = TOPIC_PALETTE.get(tid, TOPIC_PALETTE["tech"])
    color = pal["color"]
    emoji = pal["emoji"]

    if not cards_html.strip():
        cards_html = ""

    ch_btns = ""
    if channels:
        for ch in channels:
            key = ch.replace(" ", "_")
            ch_btns += (
                f'<button onclick="filterCh(this,\'{key}\')" data-ch="{key}" '
                f'class="ch-btn text-xs px-3 py-1 rounded-full border border-slate-600 '
                f'text-slate-400 hover:border-{color}-400/50 hover:text-{color}-300 transition-all">'
                f'{ch}</button>\n'
            )

    html = TOPIC_TEMPLATE.format(
        head=SHARED_HEAD,
        topic_label=topic["label"],
        topic_id=tid,
        color=color,
        emoji=emoji,
        cards=cards_html,
        channel_btns=ch_btns,
        updated=datetime.now().strftime("%Y.%m.%d %H:%M"),
    )
    out = output_dir / f"{tid}.html"
    out.write_text(html, encoding="utf-8")
    print(f"  [html] {out}")


def render_index(topics: list, topic_card_counts: dict, output_dir: Path):
    cards_html = ""
    for t in topics:
        tid   = t["id"]
        pal   = TOPIC_PALETTE.get(tid, TOPIC_PALETTE["tech"])
        color = pal["color"]
        emoji = pal["emoji"]
        shadow = TOPIC_SHADOW.get(tid, "rgba(129,140,248,0.15)")
        count = topic_card_counts.get(tid, 0)
        cards_html += INDEX_CARD.format(
            topic_id=tid,
            color=color,
            shadow=shadow,
            icon=TOPIC_ICON.get(tid, "circle"),
            emoji=emoji,
            label=t["label"],
            count=count,
        )

    html = INDEX_TEMPLATE.format(
        head=SHARED_HEAD,
        topic_cards=cards_html,
        updated=datetime.now().strftime("%Y.%m.%d %H:%M"),
    )
    out = output_dir / "index.html"
    out.write_text(html, encoding="utf-8")
    print(f"  [html] {out}")
