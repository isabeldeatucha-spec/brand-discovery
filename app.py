import base64
import json
import time
from pathlib import Path

import anthropic
import pandas as pd
import streamlit as st

from src import config

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Brand Discovery — AI Retail Intelligence",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Logo (loaded once) ────────────────────────────────────────────────────────

_logo_path = Path(__file__).parent / "logo.png"
_logo_html = ""
if _logo_path.exists():
    _logo_b64 = base64.b64encode(_logo_path.read_bytes()).decode()
    _logo_html = f'<img src="data:image/png;base64,{_logo_b64}" style="height:48px;display:block;">'

# ── Global CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

  /* Kill Streamlit chrome */
  #MainMenu, footer,
  header[data-testid="stHeader"],
  [data-testid="stToolbar"],
  [data-testid="stDecoration"],
  [data-testid="stStatusWidget"],
  .stDeployButton { display: none !important; height: 0 !important; }

  /* Base */
  .stApp, [data-testid="stAppViewContainer"] { background: #0f0f0f !important; }
  html, body, [class*="css"] {
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    color: #fff;
  }

  /* Layout */
  .block-container { padding: 0 2.5rem 3rem 2.5rem !important; }
  .block-container > div:first-child { padding-top: 0 !important; }
  [data-testid="stVerticalBlock"] { gap: 0.55rem !important; }
  .element-container { margin-bottom: 0 !important; }

  /* Container card */
  [data-testid="stVerticalBlockBorderWrapper"] {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 10px !important;
    padding: 2rem 2rem !important;
  }

  /* Inputs */
  [data-testid="stTextInput"] input {
    height: 44px !important;
    background: #242424 !important;
    color: #fff !important;
    border: 1px solid #333 !important;
    border-radius: 7px !important;
    font-size: 0.92rem !important;
  }
  [data-testid="stTextInput"] input::placeholder { color: #555 !important; }
  [data-testid="stTextInput"] input:focus { border-color: #dc2626 !important; box-shadow: none !important; }

  /* Selectbox */
  [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background: #242424 !important; color: #fff !important;
    border: 1px solid #333 !important; border-radius: 7px !important; min-height: 44px !important;
  }
  [data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within { border-color: #dc2626 !important; }
  [data-baseweb="popover"] ul { background: #242424 !important; }
  [data-baseweb="popover"] li { color: #fff !important; }
  [data-baseweb="popover"] li:hover { background: #2e2e2e !important; }
  [data-testid="stSelectbox"] span { color: #fff !important; }

  /* Slider */
  [data-testid="stSlider"] [role="slider"] { background: #dc2626 !important; border-color: #dc2626 !important; }

  /* Labels */
  [data-testid="stTextInput"] label,
  [data-testid="stSelectbox"] label,
  [data-testid="stSlider"] label {
    font-size: 0.7rem !important; font-weight: 700 !important; color: #dc2626 !important;
    text-transform: uppercase !important; letter-spacing: 0.07em !important;
    margin-bottom: 0.15rem !important;
  }

  /* Align columns to bottom so input & button share a baseline */
  [data-testid="stHorizontalBlock"] { align-items: flex-end !important; }

  /* Buttons */
  [data-testid="stButton"] > button {
    height: 44px !important; background: #dc2626 !important; border-color: #dc2626 !important;
    color: #fff !important; border-radius: 7px !important;
    font-weight: 600 !important; font-size: 0.875rem !important; width: 100% !important;
  }
  [data-testid="stButton"] > button:hover { background: #b91c1c !important; border-color: #b91c1c !important; }
  /* Form submit (Analyze) */
  [data-testid="stFormSubmitButton"] > button {
    height: 48px !important; background: #dc2626 !important; border-color: #dc2626 !important;
    color: #fff !important; border-radius: 7px !important;
    font-weight: 700 !important; font-size: 0.95rem !important;
  }
  [data-testid="stFormSubmitButton"] > button:hover { background: #b91c1c !important; border-color: #b91c1c !important; }

  /* Form border */
  [data-testid="stForm"] { border: none !important; padding: 0 !important; }

  /* st.pills */
  [data-testid="stPills"] button {
    background: #252525 !important; color: #999 !important;
    border: 1px solid #353535 !important; border-radius: 20px !important;
    font-size: 0.78rem !important; font-weight: 500 !important; height: auto !important;
  }
  [data-testid="stPills"] button:hover { background: #2e2e2e !important; color: #fff !important; border-color: #555 !important; }
  [data-testid="stPills"] button[aria-checked="true"] {
    background: #dc2626 !important; color: #fff !important; border-color: #dc2626 !important;
  }
  [data-testid="stPills"] label {
    font-size: 0.7rem !important; font-weight: 700 !important; color: #dc2626 !important;
    text-transform: uppercase !important; letter-spacing: 0.07em !important;
  }

  /* Misc */
  [data-testid="stAlert"] { background: #1a1a1a !important; color: #fff !important; border-color: #2a2a2a !important; }
  [data-testid="stProgressBar"] > div { background: #2a2a2a !important; }
  [data-testid="stProgressBar"] > div > div { background: #dc2626 !important; }
  [data-testid="stMetric"] label { color: #888 !important; }
  [data-testid="stMetric"] [data-testid="stMetricValue"] { color: #fff !important; }

  /* Loading overlay */
  .loading-overlay {
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background: #0f0f0f; z-index: 99999;
    display: flex; align-items: center; justify-content: center; flex-direction: column;
  }
  .thinking-word { font-size: 2.2rem; font-weight: 700; color: #dc2626; }
  .thinking-dot { display: inline-block; opacity: 0; }
  .thinking-dot:nth-child(1) { animation: dp 1.4s 0.0s infinite; }
  .thinking-dot:nth-child(2) { animation: dp 1.4s 0.3s infinite; }
  .thinking-dot:nth-child(3) { animation: dp 1.4s 0.6s infinite; }
  @keyframes dp { 0%,60%,100%{opacity:0} 30%{opacity:1} }
  .thinking-sub { color: #444; font-size: 0.82rem; margin-top: 0.75rem; }

  /* Nav */
  .nav-bar {
    background: #0f0f0f; border-bottom: 1px solid #1e1e1e;
    padding: 12px 2.5rem; margin: 0 -2.5rem 1.75rem -2.5rem;
    display: flex; align-items: center;
  }

  /* Divider */
  .divider { border: none; border-top: 1px solid #282828; margin: 1.25rem 0; }

  /* Headlines */
  .h1 { font-size: 2.5rem; font-weight: 800; color: #fff; line-height: 1.15; margin: 0 0 0.3rem; }
  .sub { font-size: 0.95rem; color: #888; margin: 0 0 1.2rem; }

  /* Brand summary card */
  .bcard { background: #272727; border: 1px solid #383838; border-radius: 8px; padding: 1.2rem 1.5rem; margin-bottom: 0.5rem; }
  .bcard-header { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 0.8rem; }
  .bcard-name { font-size: 1.3rem; font-weight: 800; color: #fff; }
  .bcard-meta { font-size: 0.75rem; color: #888; margin-top: 0.15rem; }
  .bcard-srp { background: #dc2626; color: #fff; font-size: 0.8rem; font-weight: 700; padding: 0.28rem 0.75rem; border-radius: 4px; white-space: nowrap; }
  .pill-row { display: flex; gap: 0.3rem; flex-wrap: wrap; margin-top: 0.5rem; }
  .plabel { font-size: 0.6rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #dc2626; margin-bottom: 0.2rem; }
  .tag { font-size: 0.68rem; font-weight: 500; padding: 0.15rem 0.5rem; border-radius: 4px; white-space: nowrap; }
  .tg  { background: #222; color: #888; }
  .tb  { background: #0e1826; color: #60a5fa; }
  .tp  { background: #180f2a; color: #c4b5fd; }
  .ta  { background: #191200; color: #fbbf24; }
  .boost-bar { font-size: 0.7rem; color: #fbbf24; margin-top: 0.7rem; padding: 0.28rem 0.65rem; background: #191200; border-radius: 4px; display: inline-block; }

  /* Reset link button */
  .reset-link { font-size: 0.75rem; color: #555; cursor: pointer; text-decoration: underline; margin-top: 0.75rem; display: inline-block; }
  .reset-link:hover { color: #888; }

  /* Persona description grid */
  .persona-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-bottom: 0.9rem; }
  .persona-desc-card {
    background: #222; border: 1px solid #333; border-radius: 7px;
    padding: 0.7rem 0.9rem;
  }
  .persona-desc-label { font-size: 0.78rem; font-weight: 700; color: #fff; margin-bottom: 0.2rem; }
  .persona-desc-text { font-size: 0.72rem; color: #888; line-height: 1.45; }

  /* Section title */
  .stitle { font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #dc2626; margin-bottom: 0.8rem; }

  /* Results */
  .banner-card { background: #1a1a1a; border-radius: 8px; padding: 1rem 1.15rem; margin-bottom: 0.55rem; border: 1px solid #2a2a2a; display: flex; align-items: center; gap: 0.9rem; }
  .banner-card-present { background: #141000; border: 1px solid #3a2e00; border-radius: 8px; padding: 1rem 1.15rem; margin-bottom: 0.55rem; display: flex; align-items: center; gap: 0.9rem; }
  .score-circle { width: 44px; height: 44px; min-width: 44px; border-radius: 7px; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: 700; color: #fff; }
  .sc-green{background:#15803d} .sc-yellow{background:#b45309} .sc-red{background:#991b1b} .sc-gray{background:#374151}
  .banner-info { flex: 1; min-width: 0; }
  .banner-name { font-size: 0.9rem; font-weight: 600; color: #fff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .bpills { display: flex; gap: 0.3rem; flex-wrap: wrap; margin-top: 0.3rem; }
  .bp  { background: #222; color: #777; font-size: 0.66rem; font-weight: 500; padding: 0.1rem 0.45rem; border-radius: 3px; }
  .bpp { background: #191200; color: #fbbf24; font-size: 0.66rem; font-weight: 600; padding: 0.1rem 0.45rem; border-radius: 3px; }
  .bpb { background: #180f2a; color: #c4b5fd; font-size: 0.66rem; font-weight: 600; padding: 0.1rem 0.45rem; border-radius: 3px; }
  .store-table { width: 100%; border-collapse: collapse; background: #1a1a1a; border-radius: 8px; overflow: hidden; border: 1px solid #2a2a2a; }
  .store-table th { text-align: left; font-size: 0.65rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; color: #dc2626; padding: 0.65rem 0.9rem; border-bottom: 1px solid #2a2a2a; }
  .store-table td { padding: 0.5rem 0.9rem; font-size: 0.78rem; color: #999; border-bottom: 1px solid #222; }
  .store-table tr:last-child td { border-bottom: none; }
  .store-table tr:hover td { background: #1e1e1e; }
  .sb { display: inline-block; padding: 0.1rem 0.45rem; border-radius: 3px; font-size: 0.68rem; font-weight: 700; color: #fff; }
  .sb-g{background:#15803d} .sb-y{background:#b45309} .sb-r{background:#991b1b} .sb-p{background:#92400e}
  .persona-result-card { background: #1a1a1a; border-radius: 8px; padding: 1.1rem 1.3rem; margin-bottom: 0.75rem; border: 1px solid #2a2a2a; }
  .pr-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.65rem; }
  .pr-logo { width: 36px; height: 36px; min-width: 36px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 0.9rem; font-weight: 700; color: #fff; margin-right: 0.65rem; }
  .pr-banner { font-size: 0.85rem; font-weight: 600; color: #fff; }
  .pr-pname { font-size: 0.7rem; color: #777; font-style: italic; }
  .pr-desc { font-size: 0.78rem; color: #999; line-height: 1.5; margin-top: 0.55rem; }
  .fit-badge { padding: 0.15rem 0.55rem; border-radius: 4px; font-size: 0.65rem; font-weight: 700; color: #fff; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────

DATA_PATH = Path.home() / "retailer_matching" / "enriched_stores.csv"

AGE_GROUP_COLS = {
    "18–24": ["% Age | 18 and 19 years, 2025 [Estimated]", "% Age | 20 to 24 years, 2025 [Estimated]"],
    "25–34": ["pct_age_25_34"],
    "35–44": ["pct_age_35_44"],
    "45–54": ["pct_age_45_54"],
    "55–64": ["% Age | 55 to 64 years, 2025 [Estimated]"],
    "65+":   ["pct_age_65_plus"],
}

LOGO_COLORS = ["#6366f1","#f59e0b","#10b981","#3b82f6","#ef4444","#8b5cf6","#ec4899","#14b8a6","#f97316","#84cc16"]
NATURAL_KW  = ["whole foods","sprouts","natural grocers","vitamin cottage","earth fare","fresh thyme","new seasons","co-op","coop","natural market","organic market","plum market","erewhon","fresh market","trader joe"]
UNFI_KW     = ["whole foods","co-op","coop","natural grocers","vitamin cottage","earth fare","new seasons","fresh market","erewhon","plum market"]
KEHE_KW     = ["sprouts","fresh thyme","natural grocers","earth fare","fresh market"]
CONV_KW     = ["kroger","safeway","albertsons","walmart","target","costco","sam's club","publix","ahold","stop & shop","giant","wegmans","hy-vee","meijer","harris teeter","food lion","winn-dixie"]

# ── Helpers ───────────────────────────────────────────────────────────────────

def sc(s):  # score color
    return "green" if s >= 70 else "yellow" if s >= 55 else "red"

def logo_color(n):
    return LOGO_COLORS[hash(n) % len(LOGO_COLORS)]

def parse_obj(text):
    t = text.strip()
    if t.startswith("```"):
        for p in t.split("```"):
            p = p.strip().lstrip("json").strip()
            if p.startswith("{"): t = p; break
    s, e = t.find("{"), t.rfind("}") + 1
    return json.loads(t[s:e]) if s >= 0 and e > s else {}

def parse_arr(text):
    t = text.strip()
    if t.startswith("```"):
        for p in t.split("```"):
            p = p.strip().lstrip("json").strip()
            if p.startswith("["): t = p; break
    s, e = t.find("["), t.rfind("]") + 1
    return json.loads(t[s:e]) if s >= 0 and e > s else []

def bm(banner, kws):
    if not isinstance(banner, str): return False
    b = banner.lower()
    return any(k in b for k in kws)

def suggest_income(srp):
    if not srp:    return (60_000, 150_000)
    if srp >= 10:  return (90_000, 200_000)
    if srp >= 6:   return (70_000, 160_000)
    if srp < 4:    return (40_000, 120_000)
    return (60_000, 150_000)

def is_url_input(text):
    """True if text looks like a URL/domain, False if it's a brand name."""
    t = text.strip()
    return t.startswith("http") or (
        "." in t and " " not in t and len(t.split(".")) >= 2
    )

# ── Data ──────────────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_csv(DATA_PATH, dtype=str, low_memory=False)
    for col in ["median_hh_income","pct_income_100k_plus","total_population",
                "pct_age_25_34","pct_age_35_44","pct_age_45_54","pct_age_65_plus",
                "pct_bachelors_plus","sales_volume_location","parent_store_count",
                "pct_owner_occupied","pct_married_couple",
                "% Age | 18 and 19 years, 2025 [Estimated]",
                "% Age | 20 to 24 years, 2025 [Estimated]",
                "% Age | 55 to 64 years, 2025 [Estimated]"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def score_stores(df, inc_min, inc_max, age_group):
    w_i, w_a, w_e = 4.0, 3.0, 3.0
    inc = df["median_hh_income"].fillna(df["median_hh_income"].median())
    is_ = pd.Series(0.0, index=df.index)
    is_[(inc >= inc_min) & (inc <= inc_max)] = 100.0
    bl = inc < inc_min; is_[bl] = (inc[bl] / inc_min * 100).clip(0, 100)
    ab = inc > inc_max; is_[ab] = (100 - ((inc[ab] - inc_max) / inc_max * 40)).clip(40, 100)
    ac = [c for c in AGE_GROUP_COLS.get(age_group, []) if c in df.columns]
    if ac:
        ap = df[ac].fillna(0).sum(axis=1)
        as_ = ((ap - ap.min()) / (ap.max() - ap.min() + 1e-9) * 100).clip(0, 100)
    else:
        as_ = pd.Series(50.0, index=df.index)
    edu = df["pct_bachelors_plus"].fillna(0)
    es  = ((edu - edu.min()) / (edu.max() - edu.min() + 1e-9) * 100).clip(0, 100)
    return ((is_ * w_i + as_ * w_a + es * w_e) / (w_i + w_a + w_e)).round(1)

def dominant_age(row):
    m = {"18–24": row.get("pct_18_24",0) or 0, "25–34": row.get("pct_age_25_34",0) or 0,
         "35–44": row.get("pct_age_35_44",0) or 0, "45–54": row.get("pct_age_45_54",0) or 0,
         "55–64": row.get("pct_55_64",0) or 0, "65+": row.get("pct_age_65_plus",0) or 0}
    return max(m, key=m.get)

# ── API – token-efficient ─────────────────────────────────────────────────────

def research_brand(query: str, api_key: str) -> dict:
    """Works with URL or brand name. Limits to 2 web searches for speed."""
    client = anthropic.Anthropic(api_key=api_key)
    ref = f"URL: {query}" if is_url_input(query) else f"Brand: {query}"

    prompt = f"""You are a CPG broker analyst. Research this brand and return ONLY valid JSON, no prose.

{ref}

Search for: brand category, SRP/pricing, retail accounts, distributors (UNFI/KeHE/DSD), label claims, channel focus.

{{"brand_name":"","category":"","subcategory":"","retail_presence":[],"distributors":[],"channel_focus":[],"srp":0.0,"pack_sizes":"","label_claims":[],"founding_year":null,"funding":null}}"""

    msgs = [{"role": "user", "content": prompt}]
    for _ in range(4):
        r = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            tools=[{"type": "web_search_20260209", "name": "web_search"}],
            messages=msgs,
        )
        # Try to extract text from any response — model may write JSON even on pause_turn
        text = next((b.text for b in r.content if hasattr(b, "text") and b.type == "text"), "")
        if text and "{" in text:
            return parse_obj(text)
        if r.stop_reason in ("end_turn",):
            raise ValueError(f"Research ended but no JSON found. Raw: {text[:300]}")
        elif r.stop_reason == "pause_turn":
            msgs.append({"role": "assistant", "content": r.content})
        else:
            raise ValueError(f"Unexpected stop_reason '{r.stop_reason}'. Raw: {text[:300]}")

def suggest_personas(intel: dict, api_key: str) -> list:
    """4 personas with labels + 1-line descriptions. Uses Haiku."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = f"""4 consumer personas for: {intel.get("brand_name")} ({intel.get("category")}, ${intel.get("srp")}, {", ".join((intel.get("label_claims") or [])[:4])}, channels: {", ".join(intel.get("channel_focus") or [])})

Return ONLY JSON array:
[{{"label":"2-4 words","description":"one sentence who this person is","age_boost":"25–34 or null","income_boost":false,"education_boost":false}}]
age_boost options: "18–24","25–34","35–44","45–54","55–64","65+",null"""
    r = client.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=500,
        messages=[{"role":"user","content":prompt}],
    )
    return parse_arr(r.content[0].text.strip())

def generate_banner_persona(banner, demo, brand, category, api_key):
    """Short shopper persona for a banner. Uses Haiku."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = f"""One-sentence shopper persona for {banner} (income ${demo['median_income']:,.0f}, age {demo['dominant_age']}, {demo['pct_bach']:.0f}% college) who might buy {brand} ({category}).
Return ONLY: {{"persona_name":"The X","description":"sentence"}}"""
    r = client.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=120,
        messages=[{"role":"user","content":prompt}],
    )
    return parse_obj(r.content[0].text.strip())

def discover_brands_in_trend(trend: str, category: str, subcategory: str, api_key: str) -> list:
    """Discover emerging brands in a specific trend/category."""
    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""You are a CPG brand scout. Discover emerging brands in this trend and return ONLY valid JSON array.

TREND: {trend}
CATEGORY: {category}
SUBCATEGORY: {subcategory}

Search for emerging brands that are gaining traction. Focus on brands that are broker-ready or close to it.

Return ONLY JSON array of brand objects:
[{{"brand_name":"Brand Name","website":"domain.com","description":"2-3 sentence description","stage":"early/emerging/growth","signals":"what makes this brand promising"}}]"""

    msgs = [{"role": "user", "content": prompt}]
    for _ in range(4):
        r = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            tools=[{"type": "web_search_20260209", "name": "web_search"}],
            messages=msgs,
        )
        text = next((b.text for b in r.content if hasattr(b, "text") and b.type == "text"), "")
        if text and "[" in text:
            return parse_arr(text)
        if r.stop_reason in ("end_turn",):
            raise ValueError(f"Discovery ended but no JSON found. Raw: {text[:300]}")
        elif r.stop_reason == "pause_turn":
            msgs.append({"role": "assistant", "content": r.content})
        else:
            raise ValueError(f"Unexpected stop_reason '{r.stop_reason}'. Raw: {text[:300]}")

def assess_broker_readiness(query: str, api_key: str) -> dict:
    """Comprehensive broker-readiness assessment of a brand."""
    client = anthropic.Anthropic(api_key=api_key)
    ref = f"URL: {query}" if is_url_input(query) else f"Brand: {query}"

    prompt = f"""You are a CPG broker analyst. Assess this brand's broker-readiness and return ONLY valid JSON.

{ref}

Assess: current distribution stage, POS count, retailers, distributors, pricing strategy, SKU variety, broker relationships, growth signals.

{{"brand_name":"","broker_readiness_score":0,"distribution_stage":"","current_pos":0,"retailers":[],"distributors":[],"pricing_strategy":{{}},"sku_variety":[],"broker_relationships":[],"growth_signals":[],"recommendations":[]}}"""

    msgs = [{"role": "user", "content": prompt}]
    for _ in range(4):
        r = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            tools=[{"type": "web_search_20260209", "name": "web_search"}],
            messages=msgs,
        )
        text = next((b.text for b in r.content if hasattr(b, "text") and b.type == "text"), "")
        if text and "{" in text:
            return parse_obj(text)
        if r.stop_reason in ("end_turn",):
            raise ValueError(f"Assessment ended but no JSON found. Raw: {text[:300]}")
        elif r.stop_reason == "pause_turn":
            msgs.append({"role": "assistant", "content": r.content})
        else:
            raise ValueError(f"Unexpected stop_reason '{r.stop_reason}'. Raw: {text[:300]}")

# ── Scoring boosts ────────────────────────────────────────────────────────────

def apply_intel_boosts(df: pd.DataFrame, intel: dict) -> pd.DataFrame:
    df = df.copy()
    df["already_present"] = False
    df["boosted"] = False
    if not intel: return df

    retail   = [r.lower().strip() for r in (intel.get("retail_presence") or [])]
    channels = [c.lower() for c in (intel.get("channel_focus") or [])]
    claims   = [c.lower() for c in (intel.get("label_claims") or [])]
    dists    = [d.lower() for d in (intel.get("distributors") or [])]
    srp      = intel.get("srp") or 0

    df["already_present"] = df["banner_name"].apply(
        lambda b: isinstance(b, str) and bool(retail) and any(r in b.lower() or b.lower() in r for r in retail)
    )
    organic = any(c in ["organic","non-gmo","non gmo","certified organic"] for c in claims)
    nat   = "natural" in channels
    unfi  = "unfi" in dists
    kehe  = "kehe" in dists

    def br(row):
        if row.get("already_present"): return row["fit_score"], False
        s, bn, inc, b = row["fit_score"], row.get("banner_name","") or "", row.get("median_hh_income",0) or 0, False
        if nat   and bm(bn, NATURAL_KW):  s = min(100, s+10); b = True
        if organic and bm(bn, NATURAL_KW): s = min(100, s+5);  b = True
        if srp > 8 and inc > 100_000:     s = min(100, s+8);  b = True
        if srp and srp < 4 and bm(bn, CONV_KW): s = min(100, s+8); b = True
        if unfi and bm(bn, UNFI_KW):      s = min(100, s+10); b = True
        if kehe and bm(bn, KEHE_KW):      s = min(100, s+10); b = True
        return round(s,1), b

    res = df.apply(br, axis=1, result_type="expand")
    df["fit_score"], df["boosted"] = res[0], res[1]
    return df

def apply_persona_boosts(df: pd.DataFrame, selected: list, all_p: list) -> pd.DataFrame:
    if not selected or not all_p: return df
    df = df.copy()
    pm = {p["label"]: p for p in all_p}
    for label in selected:
        p = pm.get(label)
        if not p: continue
        ab = p.get("age_boost")
        if ab and ab in AGE_GROUP_COLS:
            cols = [c for c in AGE_GROUP_COLS[ab] if c in df.columns]
            if cols:
                ap = df[cols].fillna(0).sum(axis=1)
                mask = ap >= ap.quantile(0.75)
                df.loc[mask, "fit_score"] = (df.loc[mask, "fit_score"] + 6).clip(upper=100)
        if p.get("income_boost") and "median_hh_income" in df.columns:
            m = df["median_hh_income"] >= 100_000
            df.loc[m, "fit_score"] = (df.loc[m, "fit_score"] + 5).clip(upper=100)
        if p.get("education_boost") and "pct_bachelors_plus" in df.columns:
            edu = df["pct_bachelors_plus"].fillna(0)
            m = edu >= edu.quantile(0.75)
            df.loc[m, "fit_score"] = (df.loc[m, "fit_score"] + 5).clip(upper=100)
    return df.assign(fit_score=df["fit_score"].round(1))

# ── Session state ─────────────────────────────────────────────────────────────

_def = {
    "mode": None,  # "discover" or "assess"
    "intel": None, "research_error": "", "results_df": None, "banners_df": None,
    "banner_personas": {}, "brand_profile": {}, "autofill_income": (60_000, 150_000),
    "is_researching": False, "pending_query": "",
    "suggested_personas": [], "selected_personas": [],
    "trend_query": "", "selected_category": "", "selected_subcategory": "",
    "discovered_brands": [], "is_discovering": False,
}
for k, v in _def.items():
    if k not in st.session_state: st.session_state[k] = v

# ── Loading overlay ───────────────────────────────────────────────────────────

if st.session_state.is_researching:
    st.markdown("""
    <div class="loading-overlay">
      <div style="text-align:center">
        <div class="thinking-word">Researching<span class="thinking-dot">.</span><span class="thinking-dot">.</span><span class="thinking-dot">.</span></div>
        <div class="thinking-sub">Analyzing brand positioning and broker-readiness…</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    _key   = config.ANTHROPIC_API_KEY
    _query = st.session_state.pending_query
    try:
        _intel = assess_broker_readiness(_query, _key)
        st.session_state.intel             = _intel
        st.session_state.research_error    = ""
        st.session_state.autofill_income   = suggest_income(_intel.get("pricing_strategy", {}).get("srp"))
        st.session_state.results_df        = None
        st.session_state.banners_df        = None
        st.session_state.banner_personas   = {}
        st.session_state.selected_personas = []
        try:
            st.session_state.suggested_personas = suggest_personas(_intel, _key)
        except Exception:
            st.session_state.suggested_personas = []
    except Exception as _e:
        st.session_state.research_error = f"Research failed: {_e}"

    st.session_state.is_researching = False
    st.rerun()

elif st.session_state.is_discovering:
    st.markdown("""
    <div class="loading-overlay">
      <div style="text-align:center">
        <div class="thinking-word">Discovering<span class="thinking-dot">.</span><span class="thinking-dot">.</span><span class="thinking-dot">.</span></div>
        <div class="thinking-sub">Finding emerging brands in this trend…</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    _key = config.ANTHROPIC_API_KEY
    _trend = st.session_state.trend_query
    _cat = st.session_state.selected_category
    _subcat = st.session_state.selected_subcategory
    try:
        _brands = discover_brands_in_trend(_trend, _cat, _subcat, _key)
        st.session_state.discovered_brands = _brands
        st.session_state.research_error = ""
    except Exception as _e:
        st.session_state.research_error = f"Discovery failed: {_e}"
        st.session_state.discovered_brands = []

    st.session_state.is_discovering = False
    st.rerun()

# ── Nav ───────────────────────────────────────────────────────────────────────

st.markdown(
    f'<div class="nav-bar">{_logo_html}</div>',
    unsafe_allow_html=True,
)

# ═══════════════════════════════════════════════════════════════════════════════
# LANDING PAGE — Mode Selection
# ═══════════════════════════════════════════════════════════════════════════════

if not st.session_state.mode:
    st.markdown(
        '<h1 class="h1" style="color:#ffffff">Brand Discovery</h1>'
        '<p class="sub">AI-powered tools for CPG brokers to discover emerging brands and assess broker-readiness.</p>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("### 🌟 Discover Brands")
        st.markdown("Find emerging brands in trending categories through intelligent web research.")
        if st.button("Start Discovery", type="primary", use_container_width=True):
            st.session_state.mode = "discover"
            st.rerun()

    with col2:
        st.markdown("### 📊 Assess Readiness")
        st.markdown("Evaluate how broker-ready a brand is - distribution, POS count, pricing, relationships.")
        if st.button("Assess Brand", type="primary", use_container_width=True):
            st.session_state.mode = "assess"
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# DISCOVERY MODE
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.mode == "discover":
    st.markdown(
        '<h1 class="h1" style="color:#ffffff">Discover Emerging Brands</h1>'
        '<p class="sub">Identify promising brands in trending categories.</p>',
        unsafe_allow_html=True,
    )

    # Back button
    if st.button("← Back to Home", key="back_discover"):
        st.session_state.mode = None
        st.session_state.discovered_brands = []
        st.rerun()

    with st.container(border=True):
        st.markdown("### Trend Analysis")

        col1, col2 = st.columns([2, 1], gap="medium")
        with col1:
            trend_input = st.text_input(
                "Trend", placeholder="e.g., 'protein is trending', 'plant-based growth', 'functional beverages'",
                value=st.session_state.trend_query,
                key="trend_input"
            )
        with col2:
            category_options = ["Beverages", "Snacks", "Dairy", "Bakery", "Frozen", "Health & Wellness", "Other"]
            selected_category = st.selectbox(
                "Category", category_options,
                index=category_options.index(st.session_state.selected_category) if st.session_state.selected_category in category_options else 0,
                key="category_select"
            )

        subcategory_options = {
            "Beverages": ["Energy Drinks", "Plant-Based Milk", "Functional Water", "Ready-to-Drink Coffee", "Kombucha", "Other"],
            "Snacks": ["Protein Bars", "Nut Butters", "Dried Fruit", "Seaweed Snacks", "Other"],
            "Dairy": ["Plant-Based Yogurt", "Functional Cheese", "Other"],
            "Bakery": ["Protein Bread", "Gluten-Free", "Other"],
            "Frozen": ["Plant-Based Meat", "Veggie Burgers", "Other"],
            "Health & Wellness": ["Supplements", "Probiotics", "Other"],
            "Other": ["Other"]
        }

        subcategory_list = subcategory_options.get(selected_category, ["Other"])
        selected_subcategory = st.selectbox(
            "Subcategory", subcategory_list,
            index=subcategory_list.index(st.session_state.selected_subcategory) if st.session_state.selected_subcategory in subcategory_list else 0,
            key="subcategory_select"
        )

        if st.button("Discover Brands", type="primary", use_container_width=True):
            if not trend_input.strip():
                st.error("Please enter a trend description.")
            elif not config.ANTHROPIC_API_KEY:
                st.error("Set ANTHROPIC_API_KEY in your environment.")
            else:
                st.session_state.trend_query = trend_input
                st.session_state.selected_category = selected_category
                st.session_state.selected_subcategory = selected_subcategory
                st.session_state.is_discovering = True
                st.rerun()

    # Display discovered brands
    if st.session_state.discovered_brands:
        st.markdown("### 📋 Discovered Brands")

        for i, brand in enumerate(st.session_state.discovered_brands):
            with st.container(border=True):
                col1, col2 = st.columns([3, 1], gap="medium")

                with col1:
                    st.markdown(f"#### {brand.get('brand_name', 'Unknown Brand')}")
                    st.markdown(f"**Website:** {brand.get('website', 'N/A')}")
                    st.markdown(f"**Stage:** {brand.get('stage', 'Unknown')}")
                    st.markdown(f"**Description:** {brand.get('description', 'No description available')}")

                    if brand.get('signals'):
                        st.markdown(f"**Growth Signals:** {brand.get('signals')}")

                with col2:
                    if st.button(f"Assess Readiness", key=f"assess_{i}", use_container_width=True):
                        st.session_state.mode = "assess"
                        st.session_state.pending_query = brand.get('website', brand.get('brand_name', ''))
                        st.session_state.is_researching = True
                        st.rerun()

    if st.session_state.research_error and st.session_state.mode == "discover":
        st.error(st.session_state.research_error)

# ═══════════════════════════════════════════════════════════════════════════════
# ASSESSMENT MODE
# ═══════════════════════════════════════════════════════════════════════════════

elif st.session_state.mode == "assess":
    intel = st.session_state.intel

    # Back button
    if st.button("← Back to Home", key="back_assess"):
        st.session_state.mode = None
        st.session_state.intel = None
        st.session_state.discovered_brands = []
        st.rerun()

    if not intel:
        # ── Brand input ──────────────────────────────────────────────────────
        st.markdown(
            '<h1 class="h1" style="color:#ffffff">Assess Brand Readiness</h1>'
            '<p class="sub">Evaluate how broker-ready a brand is across distribution, pricing, and relationships.</p>',
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            query_input = st.text_input(
                "brand", label_visibility="collapsed",
                placeholder="brandwebsite.com  or  Brand Name",
                key="query_input_field",
            )

            if st.button("Assess Brand", type="primary", use_container_width=True):
                if not query_input.strip():
                    st.error("Please enter a brand name or website.")
                elif not config.ANTHROPIC_API_KEY:
                    st.error("Set ANTHROPIC_API_KEY in your environment.")
                else:
                    st.session_state.pending_query = query_input
                    st.session_state.is_researching = True
                    st.rerun()

            if st.session_state.research_error:
                st.error(st.session_state.research_error)

    else:
        # ── Assessment results ───────────────────────────────────────────────
        readiness_score = intel.get("broker_readiness_score", 0)
        score_color = "green" if readiness_score >= 80 else "yellow" if readiness_score >= 60 else "red"

        st.markdown(
            f'<h1 class="h1" style="color:#ffffff">Brand Assessment: {intel.get("brand_name", "Unknown")}</h1>'
            f'<p class="sub">Broker-readiness score: <span style="color:#dc2626;font-weight:700">{readiness_score}/100</span></p>',
            unsafe_allow_html=True,
        )

        # Readiness Overview
        with st.container(border=True):
            st.markdown("### 📊 Readiness Overview")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Distribution Stage", intel.get("distribution_stage", "Unknown"))
            with col2:
                st.metric("Current POS", f"{intel.get('current_pos', 0):,}")
            with col3:
                pricing = intel.get("pricing_strategy", {})
                srp = pricing.get("srp", "N/A")
                st.metric("SRP", f"${srp}" if isinstance(srp, (int, float)) else srp)

            # Retailers
            retailers = intel.get("retailers", [])
            if retailers:
                st.markdown("**Current Retailers:**")
                retailer_tags = "".join(f'<span class="tag ta">{r}</span>' for r in retailers[:8])
                st.markdown(f'<div class="pill-row">{retailer_tags}</div>', unsafe_allow_html=True)

            # Distributors
            distributors = intel.get("distributors", [])
            if distributors:
                st.markdown("**Distributors:**")
                dist_tags = "".join(f'<span class="tag tp">{d}</span>' for d in distributors)
                st.markdown(f'<div class="pill-row">{dist_tags}</div>', unsafe_allow_html=True)

        # SKU Variety & Pricing
        with st.container(border=True):
            st.markdown("### 🏷️ Product Portfolio")

            sku_variety = intel.get("sku_variety", [])
            if sku_variety:
                st.markdown("**SKU Variety:**")
                sku_tags = "".join(f'<span class="tag tg">{sku}</span>' for sku in sku_variety[:10])
                st.markdown(f'<div class="pill-row">{sku_tags}</div>', unsafe_allow_html=True)

            pricing_details = intel.get("pricing_strategy", {})
            if pricing_details:
                st.markdown("**Pricing Strategy:**")
                for channel, price in pricing_details.items():
                    if channel != "srp" and isinstance(price, (int, float)):
                        st.markdown(f"- **{channel.title()}:** ${price}")

        # Broker Relationships & Growth
        with st.container(border=True):
            st.markdown("### 🤝 Broker Intelligence")

            relationships = intel.get("broker_relationships", [])
            if relationships:
                st.markdown("**Current Broker Relationships:**")
                for rel in relationships:
                    st.markdown(f"- {rel}")

            signals = intel.get("growth_signals", [])
            if signals:
                st.markdown("**Growth Signals:**")
                for signal in signals:
                    st.markdown(f"- {signal}")

        # Recommendations
        recommendations = intel.get("recommendations", [])
        if recommendations:
            with st.container(border=True):
                st.markdown("### 💡 Recommendations")
                for rec in recommendations:
                    st.markdown(f"- {rec}")

        # Reset
        if st.button("Assess Different Brand", key="reset_assess"):
            st.session_state.intel = None
            st.session_state.pending_query = ""
            st.rerun()
