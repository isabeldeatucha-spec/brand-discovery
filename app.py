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
    page_title="Sedge — Retailer Matching",
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
    "intel": None, "research_error": "", "results_df": None, "banners_df": None,
    "banner_personas": {}, "brand_profile": {}, "autofill_income": (60_000, 150_000),
    "is_researching": False, "pending_query": "",
    "suggested_personas": [], "selected_personas": [],
}
for k, v in _def.items():
    if k not in st.session_state: st.session_state[k] = v

# ── Loading overlay ───────────────────────────────────────────────────────────

if st.session_state.is_researching:
    st.markdown("""
    <div class="loading-overlay">
      <div style="text-align:center">
        <div class="thinking-word">Thinking<span class="thinking-dot">.</span><span class="thinking-dot">.</span><span class="thinking-dot">.</span></div>
        <div class="thinking-sub">Pulling retail presence, distributors, pricing &amp; claims…</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    _key   = config.ANTHROPIC_API_KEY
    _query = st.session_state.pending_query
    try:
        _intel = research_brand(_query, _key)
        st.session_state.intel             = _intel
        st.session_state.research_error    = ""
        st.session_state.autofill_income   = suggest_income(_intel.get("srp"))
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

# ── Nav ───────────────────────────────────────────────────────────────────────

st.markdown(
    f'<div class="nav-bar">{_logo_html}</div>',
    unsafe_allow_html=True,
)

intel = st.session_state.intel

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — Brand lookup (search bar) or brand summary (after research)
# ═══════════════════════════════════════════════════════════════════════════════

with st.container(border=True):

    if not intel:
        # ── Search state ──────────────────────────────────────────────────────
        st.markdown(
            '<h1 class="h1" style="color:#ffffff">Let\'s get to know your brand.</h1>'
            '<p class="sub">You just identified a new brand. Paste their website or type their name — we\'ll pull their full retail profile.</p>',
            unsafe_allow_html=True,
        )

        qcol, bcol = st.columns([5, 1], gap="small")
        with qcol:
            query_input = st.text_input(
                "brand", label_visibility="collapsed",
                placeholder="yourwebsite.com  or  Brand Name",
                key="query_input_field",
            )
        with bcol:
            research_clicked = st.button("Research Brand", type="primary", use_container_width=True, key="research_btn")

        if st.session_state.research_error:
            st.error(st.session_state.research_error)

        if research_clicked and query_input:
            if not config.ANTHROPIC_API_KEY:
                st.error("Set ANTHROPIC_API_KEY in your environment.")
            else:
                st.session_state.pending_query  = query_input
                st.session_state.is_researching = True
                st.rerun()

    else:
        # ── Post-research: brand summary only, no search bar ──────────────────
        srp_v    = intel.get("srp")
        srp_txt  = f"${srp_v:.2f}" if srp_v else "SRP unknown"
        cat      = intel.get("category","")
        subcat   = intel.get("subcategory","")
        cat_full = f"{cat} · {subcat}" if subcat and subcat.lower() != cat.lower() else cat
        founding = intel.get("founding_year")
        funding  = intel.get("funding")
        meta     = " · ".join(x for x in [f"Founded {founding}" if founding else "", funding or ""] if x)

        claims   = intel.get("label_claims") or []
        channels = intel.get("channel_focus") or []
        dists    = intel.get("distributors") or []
        retailers= intel.get("retail_presence") or []

        ch_html = "".join(f'<span class="tag tg">{c}</span>' for c in claims[:7])
        cn_html = "".join(f'<span class="tag tb">{c}</span>' for c in channels)
        di_html = "".join(f'<span class="tag tp">{d}</span>' for d in dists)
        re_html = "".join(f'<span class="tag ta">{r}</span>' for r in retailers[:6])

        boosts = []
        if "natural" in [c.lower() for c in channels]: boosts.append("natural channel")
        if any(d.lower()=="unfi" for d in dists):       boosts.append("UNFI banners")
        if any(d.lower()=="kehe" for d in dists):       boosts.append("KeHE banners")
        if srp_v and srp_v > 8:                         boosts.append("high-income zips")
        if srp_v and srp_v < 4:                         boosts.append("conventional/mass")
        boost_html = f'<div class="boost-bar">⚡ Scoring boost active: {", ".join(boosts)}</div>' if boosts else ""

        st.markdown(f"""
        <div class="bcard">
          <div class="bcard-header">
            <div>
              <div class="bcard-name">{intel.get("brand_name","")}</div>
              <div class="bcard-meta">{cat_full}{(" · " + meta) if meta else ""}</div>
            </div>
            <div class="bcard-srp">{srp_txt}</div>
          </div>
          {"".join([
            f'<div><div class="plabel">Label claims</div><div class="pill-row">{ch_html}</div></div>' if ch_html else "",
            f'<div style="margin-top:.45rem"><div class="plabel">Channels</div><div class="pill-row">{cn_html}</div></div>' if cn_html else "",
            f'<div style="margin-top:.45rem"><div class="plabel">Distributors</div><div class="pill-row">{di_html}</div></div>' if di_html else "",
            f'<div style="margin-top:.45rem"><div class="plabel">Retail presence</div><div class="pill-row">{re_html}</div></div>' if re_html else "",
          ])}
          {boost_html}
        </div>
        """, unsafe_allow_html=True)

        # Reset link
        if st.button("← Research a different brand", key="reset_btn"):
            for k in ["intel","research_error","results_df","banners_df","banner_personas",
                      "brand_profile","suggested_personas","selected_personas"]:
                st.session_state[k] = None if k == "intel" else ([] if k in ["suggested_personas","selected_personas"] else ({} if k in ["banner_personas","brand_profile"] else ("" if k == "research_error" else None)))
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2 — Let's find your ideal retailers (only shown after research)
# ═══════════════════════════════════════════════════════════════════════════════

if intel:
    with st.container(border=True):
        st.markdown(
            '<h1 class="h1" style="color:#ffffff">Let\'s find their ideal retailers.</h1>'
            '<p class="sub">Define the target consumer and we\'ll rank 71,000 US grocery stores by fit.</p>',
            unsafe_allow_html=True,
        )

        # Persona descriptions grid (informational, above pills)
        if st.session_state.suggested_personas:
            cards_html = "".join(
                f'<div class="persona-desc-card">'
                f'<div class="persona-desc-label">{p["label"]}</div>'
                f'<div class="persona-desc-text">{p.get("description","")}</div>'
                f'</div>'
                for p in st.session_state.suggested_personas
            )
            st.markdown(
                f'<div class="plabel" style="margin-bottom:.5rem">Customer personas — select all that apply</div>'
                f'<div class="persona-grid">{cards_html}</div>',
                unsafe_allow_html=True,
            )

        with st.form("analysis_form"):
            sc1, sc2 = st.columns([2, 1], gap="medium")
            with sc1:
                income_range = st.slider(
                    "Income range ($)", 0, 250_000,
                    st.session_state.autofill_income,
                    step=5_000, format="$%d",
                )
            with sc2:
                age_group = st.selectbox("Age group", list(AGE_GROUP_COLS.keys()), index=1)

            if st.session_state.suggested_personas:
                labels = [p["label"] for p in st.session_state.suggested_personas]
                selected_in_form = st.pills(
                    "Select personas",
                    options=labels,
                    selection_mode="multi",
                    default=st.session_state.selected_personas or [],
                )
            else:
                selected_in_form = []

            brand_name     = intel.get("brand_name", "")
            brand_category = intel.get("category", "")

            submitted = st.form_submit_button("Analyze", type="primary", use_container_width=True)

    if submitted:
        st.session_state.selected_personas = selected_in_form or []
        st.session_state.brand_profile = {"name": brand_name, "category": brand_category, "age_group": age_group}

        with st.spinner("Scoring stores…"):
            df = load_data()
            df["fit_score"] = score_stores(df, income_range[0], income_range[1], age_group)
            df = apply_intel_boosts(df, intel)

            chosen = st.session_state.selected_personas
            all_p  = st.session_state.suggested_personas
            if chosen and all_p:
                df = apply_persona_boosts(df, chosen, all_p)

            df["pct_18_24"] = df[["% Age | 18 and 19 years, 2025 [Estimated]",
                                   "% Age | 20 to 24 years, 2025 [Estimated]"]].fillna(0).sum(axis=1)
            df["pct_55_64"] = df["% Age | 55 to 64 years, 2025 [Estimated]"].fillna(0)
            st.session_state.results_df = df

            banners = (
                df[df["banner_name"].notna() & (df["banner_name"] != "")]
                .groupby("banner_name")
                .agg(
                    fit_score=("fit_score","mean"), fit_store_count=("fit_score",lambda x:(x>=70).sum()),
                    total_stores=("fit_score","count"), median_income=("median_hh_income","median"),
                    pct_bach=("pct_bachelors_plus","mean"), pct_owner=("pct_owner_occupied","mean"),
                    pct_married=("pct_married_couple","mean"),
                    pct_18_24=("pct_18_24","mean"), pct_age_25_34=("pct_age_25_34","mean"),
                    pct_age_35_44=("pct_age_35_44","mean"), pct_age_45_54=("pct_age_45_54","mean"),
                    pct_55_64=("pct_55_64","mean"), pct_age_65_plus=("pct_age_65_plus","mean"),
                    already_present=("already_present","any"), boosted=("boosted","any"),
                )
                .reset_index().sort_values("fit_score", ascending=False)
            )
            st.session_state.banners_df    = banners
            st.session_state.banner_personas = {}

# ── Results ───────────────────────────────────────────────────────────────────

results = st.session_state.results_df
banners = st.session_state.banners_df

if results is not None:
    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    pct = int(results["already_present"].sum()) if "already_present" in results.columns else 0
    m1.metric("Stores scored",    f"{len(results):,}")
    m2.metric("Strong fit (≥80)", f"{(results['fit_score']>=80).sum():,}")
    m3.metric("Good fit (≥60)",   f"{(results['fit_score']>=60).sum():,}")
    m4.metric("Already present" if pct else "Avg score",
              f"{pct:,} stores" if pct else f"{results['fit_score'].mean():.1f}")

    st.markdown("<div style='height:.75rem'></div>", unsafe_allow_html=True)

    lc, rc = st.columns([1, 1.6], gap="large")

    with lc:
        st.markdown('<div class="stitle">Banner Ranking</div>', unsafe_allow_html=True)
        for _, row in banners.head(10).iterrows():
            s_val   = round(row["fit_score"], 1)
            is_p    = bool(row.get("already_present", False))
            is_b    = bool(row.get("boosted", False)) and not is_p
            income  = f"${row['median_income']:,.0f}" if pd.notna(row["median_income"]) else "—"
            bach    = f"{row['pct_bach']:.0f}% bach+" if pd.notna(row["pct_bach"]) else "—"
            fits    = f"{int(row['fit_store_count'])} fit stores"
            extra   = ('<span class="bpp">Already present</span>' if is_p else
                       '<span class="bpb">⚡ Boosted</span>' if is_b else "")
            if is_p:  card, circ, disp = "banner-card-present", "sc-gray", "✓"
            else:     card, circ, disp = "banner-card", f"sc-{sc(s_val)}", f"{s_val:.0f}"
            st.markdown(f"""
            <div class="{card}">
              <div class="score-circle {circ}">{disp}</div>
              <div class="banner-info">
                <div class="banner-name">{row['banner_name']}</div>
                <div class="bpills"><span class="bp">{income}</span><span class="bp">{bach}</span><span class="bp">{fits}</span>{extra}</div>
              </div>
            </div>""", unsafe_allow_html=True)

    with rc:
        st.markdown('<div class="stitle">Top Stores</div>', unsafe_allow_html=True)
        top = results.nlargest(50, "fit_score")[
            ["store_name","banner_name","city","state","fit_score","median_hh_income","already_present","boosted"]
        ].copy()
        rows_html = ""
        for _, r in top.iterrows():
            sv      = r["fit_score"]
            is_p    = bool(r.get("already_present", False))
            income  = f"${r['median_hh_income']:,.0f}" if pd.notna(r["median_hh_income"]) else "—"
            banner  = r["banner_name"] if pd.notna(r["banner_name"]) else "—"
            if is_p: badge = '<span class="sb sb-p">Present</span>'
            else:    badge = f'<span class="sb sb-{sc(sv)[0]}">{sv:.0f}{"⚡" if r.get("boosted") else ""}</span>'
            rows_html += f"<tr><td><strong>{r['store_name']}</strong></td><td style='color:#555'>{banner}</td><td>{r['city']}</td><td>{r['state']}</td><td>{income}</td><td>{badge}</td></tr>"
        st.markdown(f"""<table class="store-table"><thead><tr>
          <th>Store</th><th>Banner</th><th>City</th><th>State</th><th>Med. Income</th><th>Score</th>
        </tr></thead><tbody>{rows_html}</tbody></table>""", unsafe_allow_html=True)

    # ── Shopper Personas by Banner ────────────────────────────────────────────
    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="stitle">Shopper Personas by Banner</div>', unsafe_allow_html=True)

    api_key = config.ANTHROPIC_API_KEY
    top10   = banners.head(10)
    missing = [r["banner_name"] for _, r in top10.iterrows()
               if r["banner_name"] not in st.session_state.banner_personas]

    if missing and api_key:
        bp  = st.session_state.brand_profile
        prg = st.progress(0, text="Generating personas…")
        for i, bn in enumerate(missing):
            prg.progress(i / len(missing), text=f"Generating persona for {bn}…")
            row  = top10[top10["banner_name"] == bn].iloc[0]
            demo = {
                "median_income": row["median_income"] if pd.notna(row["median_income"]) else 75000,
                "dominant_age":  dominant_age(row.to_dict()),
                "pct_bach":      row["pct_bach"] if pd.notna(row["pct_bach"]) else 30,
                "pct_owner":     row["pct_owner"] if pd.notna(row["pct_owner"]) else 60,
                "pct_married":   row["pct_married"] if pd.notna(row["pct_married"]) else 50,
            }
            try:
                p = generate_banner_persona(bn, demo, bp.get("name",""), bp.get("category",""), api_key)
                st.session_state.banner_personas[bn] = {**p, **demo, "fit_score": round(row["fit_score"],1)}
            except Exception as e:
                st.session_state.banner_personas[bn] = {
                    "persona_name":"Unknown Shopper","description":f"Could not generate: {e}",
                    **demo,"fit_score":round(row["fit_score"],1),
                }
            if i < len(missing)-1: time.sleep(0.2)
        prg.progress(1.0); time.sleep(0.2); prg.empty()
    elif missing and not api_key:
        st.warning("Set ANTHROPIC_API_KEY to generate personas.")

    pts = [(bn, st.session_state.banner_personas[bn])
           for _, row in top10.iterrows()
           for bn in [row["banner_name"]]
           if bn in st.session_state.banner_personas]

    for i in range(0, len(pts), 2):
        cols = st.columns(2, gap="medium")
        for j, col in enumerate(cols):
            if i+j >= len(pts): break
            bn, p = pts[i+j]
            color    = sc(p["fit_score"])
            lc_color = logo_color(bn)
            fl       = {"green":"Strong fit","yellow":"Moderate fit","red":"Weak fit"}[color]
            fb       = {"green":"#22c55e","yellow":"#eab308","red":"#ef4444"}[color]
            with col:
                st.markdown(f"""
                <div class="persona-result-card">
                  <div class="pr-header">
                    <div style="display:flex;align-items:center">
                      <div class="pr-logo" style="background:{lc_color}">{bn[0].upper()}</div>
                      <div><div class="pr-banner">{bn}</div><div class="pr-pname">{p['persona_name']}</div></div>
                    </div>
                    <span class="fit-badge" style="background:{fb}">{fl} · {p['fit_score']:.0f}</span>
                  </div>
                  <div class="bpills">
                    <span class="bp">${p['median_income']:,.0f}</span>
                    <span class="bp">{p['dominant_age']}</span>
                    <span class="bp">{p['pct_bach']:.0f}% bach+</span>
                  </div>
                  <div class="pr-desc">{p['description']}</div>
                </div>""", unsafe_allow_html=True)
