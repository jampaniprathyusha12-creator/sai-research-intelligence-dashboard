"""
Sai University — Research Intelligence Dashboard
=================================================
Fetch -> Clean -> Analyse -> Visualize -> Interact -> Insight

Data source: https://sai-publications-dashboard.vercel.app/api/publications

Run with:
    streamlit run app.py
"""

import re
import io
from collections import Counter
from datetime import datetime

import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import streamlit as st

# --------------------------------------------------------------------------------------
# PAGE CONFIG & GLOBAL STYLE
# --------------------------------------------------------------------------------------
st.set_page_config(
    page_title="Sai University | Research Intelligence Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_URL = "https://sai-publications-dashboard.vercel.app/api/publications"

sns.set_theme(style="whitegrid", context="talk")
PALETTE = ["#4C6EF5", "#15AABF", "#F76707", "#12B886", "#E64980",
           "#845EF7", "#FAB005", "#20C997", "#FA5252", "#5C7CFA"]
sns.set_palette(PALETTE)

# --------------------------------------------------------------------------------------
# THEME (light / dark) — pure CSS injection, keeps Matplotlib in sync
# --------------------------------------------------------------------------------------
def inject_css(dark: bool):
    if dark:
        bg, card, text, sub, accent, border = "#0E1117", "#161B22", "#E6EDF3", "#9DA7B3", "#4C6EF5", "#262C36"
    else:
        bg, card, text, sub, accent, border = "#F7F9FC", "#FFFFFF", "#1A1D29", "#5B6472", "#4C6EF5", "#E7ECF3"

    st.markdown(f"""
    <style>
        .stApp {{ background-color: {bg}; color: {text}; }}
        section[data-testid="stSidebar"] {{ background-color: {card}; border-right: 1px solid {border}; }}
        .kpi-card {{
            background: {card}; border: 1px solid {border}; border-radius: 14px;
            padding: 16px 18px; text-align: left; box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        }}
        .kpi-label {{ font-size: 0.78rem; font-weight: 600; letter-spacing: .04em;
                      text-transform: uppercase; color: {sub}; margin-bottom: 6px; }}
        .kpi-value {{ font-size: 1.9rem; font-weight: 800; color: {text}; line-height: 1.1; }}
        .kpi-sub {{ font-size: 0.78rem; color: {sub}; margin-top: 4px; }}
        .section-title {{ font-size: 1.25rem; font-weight: 700; margin: 6px 0 2px 0; color: {text}; }}
        .section-caption {{ font-size: 0.85rem; color: {sub}; margin-bottom: 10px; }}
        .insight-box {{
            background: linear-gradient(135deg, {accent}22, {accent}08);
            border-left: 4px solid {accent}; border-radius: 10px; padding: 12px 16px;
            font-size: 0.92rem; color: {text}; margin-bottom: 8px;
        }}
        div[data-testid="stMetricValue"] {{ color: {accent}; }}
        .pub-title {{ font-weight: 700; color: {text}; }}
        .pub-meta {{ font-size: 0.8rem; color: {sub}; }}
        a {{ color: {accent} !important; }}
    </style>
    """, unsafe_allow_html=True)

    plt.rcParams.update({
        "figure.facecolor": card, "axes.facecolor": card, "savefig.facecolor": card,
        "text.color": text, "axes.labelcolor": text, "xtick.color": sub, "ytick.color": sub,
        "axes.edgecolor": border, "grid.color": border, "axes.titlecolor": text,
    })
    return dict(bg=bg, card=card, text=text, sub=sub, accent=accent, border=border)


# --------------------------------------------------------------------------------------
# DATA FETCH & CLEANING
# --------------------------------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_raw():
    resp = requests.get(API_URL, timeout=30)
    resp.raise_for_status()
    payload = resp.json()
    records = payload.get("data", payload) if isinstance(payload, dict) else payload
    return pd.DataFrame(records)


def _split_multi(value, sep="|"):
    if pd.isna(value) or str(value).strip() in ("", "-"):
        return []
    parts = [p.strip() for p in str(value).split(sep)]
    return [p for p in parts if p and p != "-"]


def _split_semicolon(value):
    if pd.isna(value) or str(value).strip() in ("", "-"):
        return []
    parts = [p.strip() for p in re.split(r";", str(value))]
    return [p for p in parts if p]


def classify_indexing(raw):
    raw = (raw or "").strip()
    scopus = "scopus" in raw.lower()
    wos = "wos" in raw.lower() or "web of science" in raw.lower()
    if scopus and wos:
        label = "Scopus & WoS"
    elif scopus:
        label = "Scopus only"
    elif wos:
        label = "WoS only"
    else:
        label = "Non Indexed"
    return pd.Series([scopus, wos, label])


@st.cache_data(ttl=3600, show_spinner=False)
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for c in df.columns:
        df[c] = df[c].astype(str).replace({"nan": "", "None": ""}).str.strip()

    # Year -> numeric
    df["Year_num"] = pd.to_numeric(df.get("Year", ""), errors="coerce")

    # School: fill missing
    df["School_clean"] = df.get("School", "").replace("", "Unspecified")

    # Document type
    df["DocType_clean"] = df.get("Document Type", "").replace("", "Unspecified")

    # Publisher
    df["Publisher_clean"] = df.get("Publisher", "").replace("", "Unknown Publisher")

    # Indexing status parsing
    idx = df.get("Indexing Status", "").apply(classify_indexing)
    idx.columns = ["is_scopus", "is_wos", "Indexing_clean"]
    df = pd.concat([df, idx], axis=1)

    # SJR quartile: prefer SJR Quartile, fallback to Year Wise Quartile
    def pick_quartile(row):
        q = row.get("SJR Quartile", "")
        if q in ("Q1", "Q2", "Q3", "Q4"):
            return q
        q2 = row.get("Year Wise Quartile", "")
        if q2 in ("Q1", "Q2", "Q3", "Q4"):
            return q2
        return "Not Available"
    df["Quartile_clean"] = df.apply(pick_quartile, axis=1)

    # SaiU authors (in-house authors) -> list
    df["Faculty_list"] = df.get("SaiU Authors", "").apply(_split_semicolon)
    df["Faculty_count"] = df["Faculty_list"].apply(len)
    df["Faculty_primary"] = df["Faculty_list"].apply(lambda l: l[0] if l else "Unspecified")

    # All authors (external + internal) count
    df["All_authors_list"] = df.get("Authors", "").apply(_split_semicolon)
    df["Author_count"] = df["All_authors_list"].apply(lambda l: len(l) if l else 1)

    # SDGs: prefer SaiU SDG Indexing, else union of WoS/Scopus achieved
    def get_sdgs(row):
        primary = _split_multi(row.get("SaiU SDG Indexing", ""))
        if primary:
            return sorted(set(primary), key=lambda x: (len(x), x))
        combo = _split_multi(row.get("Achieved SDG (WoS)", "")) + _split_multi(row.get("Achieved SDG (Scopus)", ""))
        return sorted(set(combo), key=lambda x: (len(x), x))
    df["SDG_list"] = df.apply(get_sdgs, axis=1)
    df["SDG_count"] = df["SDG_list"].apply(len)

    # Best available link for the explorer
    def best_link(row):
        for col in ["DOI Link", "Article Link", "Scopus URL", "WoS URL", "Journal Link"]:
            v = row.get(col, "")
            if v:
                return v
        return ""
    df["Best_link"] = df.apply(best_link, axis=1)

    # Designation cleanup
    df["Designation_clean"] = df.get("Designation", "").replace("", "Unspecified")

    # Faculty profile photo (as supplied by the API, tied to the row's primary SaiU author)
    df["Photo_clean"] = df.get("Faculty Profile Photo", "")

    return df


def build_faculty_photo_map(df: pd.DataFrame) -> dict:
    """Map each SaiU faculty name to their most-common non-empty profile photo URL."""
    photo_map = {}
    counts = {}
    for _, row in df.iterrows():
        photo = row.get("Photo_clean", "")
        if not photo:
            continue
        for name in row.get("Faculty_list", []):
            counts.setdefault(name, Counter())
            counts[name][photo] += 1
    for name, ctr in counts.items():
        photo_map[name] = ctr.most_common(1)[0][0]
    return photo_map


def avatar_url(name: str, photo_map: dict, size: int = 160) -> str:
    """Return the researcher's real photo if we have one, else a generated initials avatar."""
    photo = photo_map.get(name, "")
    if photo:
        return photo
    initials = "".join([p[0] for p in name.split() if p])[:2].upper() or "?"
    return f"https://ui-avatars.com/api/?name={initials}&size={size}&background=4C6EF5&color=ffffff&bold=true"


SDG_NAMES = {
    "1": "No Poverty", "2": "Zero Hunger", "3": "Good Health & Well-being",
    "4": "Quality Education", "5": "Gender Equality", "6": "Clean Water & Sanitation",
    "7": "Affordable & Clean Energy", "8": "Decent Work & Economic Growth",
    "9": "Industry, Innovation & Infrastructure", "10": "Reduced Inequalities",
    "11": "Sustainable Cities & Communities", "12": "Responsible Consumption & Production",
    "13": "Climate Action", "14": "Life Below Water", "15": "Life on Land",
    "16": "Peace, Justice & Strong Institutions", "17": "Partnerships for the Goals",
}


# --------------------------------------------------------------------------------------
# LOAD DATA
# --------------------------------------------------------------------------------------
with st.spinner("Fetching publication records..."):
    try:
        raw_df = fetch_raw()
        error_msg = None
    except Exception as e:
        raw_df = pd.DataFrame()
        error_msg = str(e)

if error_msg or raw_df.empty:
    st.error(f"Could not load data from the Publications API.\n\n{error_msg or 'Empty response.'}")
    st.stop()

df = clean_data(raw_df)
FACULTY_PHOTOS = build_faculty_photo_map(df)

# --------------------------------------------------------------------------------------
# SIDEBAR — FILTERS
# --------------------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🎓 Sai University")
    st.markdown("#### Research Intelligence Dashboard")
    dark_mode = st.toggle("🌙 Dark mode", value=False)
    st.markdown("---")
    st.markdown("### Filters")

    years_available = sorted([int(y) for y in df["Year_num"].dropna().unique()])
    if years_available:
        yr_min, yr_max = min(years_available), max(years_available)
        year_range = st.slider("Year range", yr_min, yr_max, (yr_min, yr_max), step=1)
    else:
        year_range = (0, 0)

    schools = sorted([s for s in df["School_clean"].unique() if s])
    sel_schools = st.multiselect("School", schools, default=[])

    all_faculty = sorted(set(f for lst in df["Faculty_list"] for f in lst if f))
    sel_faculty = st.multiselect("Author (SaiU faculty)", all_faculty, default=[])

    doc_types = sorted([d for d in df["DocType_clean"].unique() if d])
    sel_doctypes = st.multiselect("Document type", doc_types, default=[])

    idx_options = sorted([i for i in df["Indexing_clean"].unique() if i])
    sel_index = st.multiselect("Indexing status", idx_options, default=[])

    quartile_options = ["Q1", "Q2", "Q3", "Q4", "Not Available"]
    quartile_options = [q for q in quartile_options if q in df["Quartile_clean"].unique()]
    sel_quartile = st.multiselect("SJR quartile", quartile_options, default=[])

    all_sdgs = sorted(set(s for lst in df["SDG_list"] for s in lst), key=lambda x: int(x))
    sdg_labels = [f"SDG {s} — {SDG_NAMES.get(s, 'Other')}" for s in all_sdgs]
    sdg_map = dict(zip(sdg_labels, all_sdgs))
    sel_sdg_labels = st.multiselect("SDG", sdg_labels, default=[])
    sel_sdg = [sdg_map[l] for l in sel_sdg_labels]

    publishers = sorted([p for p in df["Publisher_clean"].unique() if p])
    sel_publishers = st.multiselect("Publisher / source", publishers, default=[])

    search_text = st.text_input("🔎 Quick search (title / author / keyword)", "")

    if st.button("Reset all filters"):
        st.rerun()

theme = inject_css(dark_mode)

# --------------------------------------------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------------------------------------------
mask = pd.Series(True, index=df.index)
if years_available:
    mask &= df["Year_num"].between(year_range[0], year_range[1]) | df["Year_num"].isna()
if sel_schools:
    mask &= df["School_clean"].isin(sel_schools)
if sel_faculty:
    mask &= df["Faculty_list"].apply(lambda lst: any(f in sel_faculty for f in lst))
if sel_doctypes:
    mask &= df["DocType_clean"].isin(sel_doctypes)
if sel_index:
    mask &= df["Indexing_clean"].isin(sel_index)
if sel_quartile:
    mask &= df["Quartile_clean"].isin(sel_quartile)
if sel_sdg:
    mask &= df["SDG_list"].apply(lambda lst: any(s in sel_sdg for s in lst))
if sel_publishers:
    mask &= df["Publisher_clean"].isin(sel_publishers)
if search_text.strip():
    q = search_text.strip().lower()
    mask &= (
        df["Title"].str.lower().str.contains(q, na=False) |
        df["Authors"].str.lower().str.contains(q, na=False) |
        df["Keywords"].str.lower().str.contains(q, na=False) |
        df["Source title"].str.lower().str.contains(q, na=False)
    )

fdf = df[mask].copy()

# --------------------------------------------------------------------------------------
# HEADER
# --------------------------------------------------------------------------------------
st.markdown(f"""
<div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:10px;">
  <div>
    <div style="font-size:1.7rem; font-weight:800;">Research Intelligence Dashboard</div>
    <div class="section-caption">Sai University · publication output, quality &amp; impact, live from the Publications API</div>
  </div>
  <div class="pub-meta">Showing <b>{len(fdf):,}</b> of {len(df):,} publications · updated {datetime.now().strftime('%d %b %Y, %H:%M')}</div>
</div>
""", unsafe_allow_html=True)

if fdf.empty:
    st.warning("No publications match the current filters. Try widening your filter selection.")
    st.stop()

# --------------------------------------------------------------------------------------
# KPI SECTION
# --------------------------------------------------------------------------------------
total_pubs = len(fdf)
scopus_pubs = int(fdf["is_scopus"].sum())
wos_pubs = int(fdf["is_wos"].sum())
q1_pubs = int((fdf["Quartile_clean"] == "Q1").sum())
n_schools = fdf["School_clean"].nunique()
n_faculty = len(set(f for lst in fdf["Faculty_list"] for f in lst if f))
n_sdgs = len(set(s for lst in fdf["SDG_list"] for s in lst))
n_years = fdf["Year_num"].nunique()

# YoY delta on the most recent two full years in the filtered set
year_counts_full = fdf["Year_num"].dropna().astype(int).value_counts().sort_index()
yoy_txt = "—"
if len(year_counts_full) >= 2:
    last_two = year_counts_full.tail(2)
    prev, curr = last_two.iloc[0], last_two.iloc[1]
    delta = curr - prev
    pct = (delta / prev * 100) if prev else 0
    yoy_txt = f"{'+' if delta >= 0 else ''}{delta} ({pct:+.0f}%) vs {last_two.index[0]}"

kpis = [
    ("Total Publications", f"{total_pubs:,}", f"across {n_years} year(s)"),
    ("Scopus-Indexed", f"{scopus_pubs:,}", f"{scopus_pubs/total_pubs*100:.0f}% of total"),
    ("Web of Science-Indexed", f"{wos_pubs:,}", f"{wos_pubs/total_pubs*100:.0f}% of total"),
    ("Q1 Publications", f"{q1_pubs:,}", f"{q1_pubs/total_pubs*100:.0f}% of total"),
    ("Schools Contributing", f"{n_schools:,}", "distinct schools"),
    ("Faculty Authors", f"{n_faculty:,}", "distinct SaiU authors"),
    ("SDGs Represented", f"{n_sdgs:,}", "out of 17 goals"),
    ("Latest Year Trend", year_counts_full.index[-1] if len(year_counts_full) else "—", yoy_txt),
]

cols = st.columns(4)
for i, (label, value, sub) in enumerate(kpis):
    with cols[i % 4]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)
    if i % 4 == 3 and i != len(kpis) - 1:
        cols = st.columns(4)

st.markdown("<br>", unsafe_allow_html=True)

# --------------------------------------------------------------------------------------
# AUTO-GENERATED INSIGHTS
# --------------------------------------------------------------------------------------
insights = []
if len(year_counts_full) >= 2:
    trend_dir = "grown" if year_counts_full.iloc[-1] >= year_counts_full.iloc[-2] else "declined"
    insights.append(f"📈 Output has **{trend_dir}** from {year_counts_full.iloc[-2]} in {year_counts_full.index[-2]} "
                     f"to {year_counts_full.iloc[-1]} in {year_counts_full.index[-1]}.")
top_school = fdf["School_clean"].value_counts()
if not top_school.empty:
    insights.append(f"🏫 **{top_school.index[0]}** leads with {top_school.iloc[0]} publications "
                     f"({top_school.iloc[0]/total_pubs*100:.0f}% of the filtered set).")
indexed_pct = (scopus_pubs or wos_pubs) and round((fdf["is_scopus"] | fdf["is_wos"]).sum() / total_pubs * 100)
insights.append(f"🔎 **{indexed_pct}%** of filtered publications carry Scopus and/or WoS indexing.")
top_author = Counter(f for lst in fdf["Faculty_list"] for f in lst if f).most_common(1)
if top_author:
    insights.append(f"✍️ **{top_author[0][0]}** is the most prolific author in view with {top_author[0][1]} publications.")
top_sdg = Counter(s for lst in fdf["SDG_list"] for s in lst).most_common(1)
if top_sdg:
    sname = SDG_NAMES.get(top_sdg[0][0], "")
    insights.append(f"🌍 **SDG {top_sdg[0][0]} ({sname})** is the most represented goal, tagged in {top_sdg[0][1]} publications.")

with st.expander("💡 Auto-generated insights", expanded=True):
    for ins in insights:
        st.markdown(f'<div class="insight-box">{ins}</div>', unsafe_allow_html=True)

st.markdown("---")

# --------------------------------------------------------------------------------------
# TABS
# --------------------------------------------------------------------------------------
tab_overview, tab_school, tab_people, tab_sdg, tab_explorer = st.tabs(
    ["📈 Overview", "🏫 Schools", "👩‍🔬 Researchers", "🌍 SDGs", "🔍 Explorer"]
)

def fig_ax(w=7, h=4.2):
    fig, ax = plt.subplots(figsize=(w, h))
    return fig, ax

# ---------------- OVERVIEW TAB ----------------
with tab_overview:
    c1, c2 = st.columns([1.4, 1])

    with c1:
        st.markdown('<div class="section-title">Publication Trend Over Time</div>', unsafe_allow_html=True)
        yearly = fdf.dropna(subset=["Year_num"]).groupby("Year_num").size().sort_index()
        yearly.index = yearly.index.astype(int)
        fig, ax = fig_ax(8, 4.2)
        ax.plot(yearly.index, yearly.values, marker="o", linewidth=2.5, color=PALETTE[0])
        ax.fill_between(yearly.index, yearly.values, alpha=0.15, color=PALETTE[0])
        ax.set_xlabel("Year"); ax.set_ylabel("Publications")
        ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        for x, y in zip(yearly.index, yearly.values):
            ax.annotate(str(y), (x, y), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9)
        st.pyplot(fig, use_container_width=True)

    with c2:
        st.markdown('<div class="section-title">Document Type Mix</div>', unsafe_allow_html=True)
        dt = fdf["DocType_clean"].value_counts()
        fig, ax = fig_ax(5.5, 4.2)
        wedges, _, autotexts = ax.pie(
            dt.values, labels=None, autopct=lambda p: f"{p:.0f}%" if p >= 5 else "",
            colors=PALETTE, startangle=90, pctdistance=0.8,
            wedgeprops=dict(width=0.42, edgecolor=theme["card"])
        )
        ax.legend(wedges, dt.index, loc="center left", bbox_to_anchor=(1, 0.5), fontsize=8, frameon=False)
        ax.set_aspect("equal")
        st.pyplot(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="section-title">Indexing Status</div>', unsafe_allow_html=True)
        idx_counts = fdf["Indexing_clean"].value_counts()
        fig, ax = fig_ax(6, 4)
        bars = ax.bar(idx_counts.index, idx_counts.values, color=PALETTE[:len(idx_counts)])
        ax.set_ylabel("Publications")
        ax.bar_label(bars, padding=3, fontsize=9)
        plt.setp(ax.get_xticklabels(), rotation=15, ha="right")
        st.pyplot(fig, use_container_width=True)

    with c4:
        st.markdown('<div class="section-title">SJR Quartile Distribution</div>', unsafe_allow_html=True)
        order = ["Q1", "Q2", "Q3", "Q4", "Not Available"]
        q_counts = fdf["Quartile_clean"].value_counts().reindex(order).dropna()
        colors_q = {"Q1": "#12B886", "Q2": "#4C6EF5", "Q3": "#FAB005", "Q4": "#FA5252", "Not Available": "#ADB5BD"}
        fig, ax = fig_ax(6, 4)
        bars = ax.bar(q_counts.index, q_counts.values, color=[colors_q.get(k, "#999") for k in q_counts.index])
        ax.set_ylabel("Publications")
        ax.bar_label(bars, padding=3, fontsize=9)
        st.pyplot(fig, use_container_width=True)

# ---------------- SCHOOLS TAB ----------------
with tab_school:
    st.markdown('<div class="section-title">Publications by School</div>', unsafe_allow_html=True)
    school_counts = fdf["School_clean"].value_counts().sort_values(ascending=True)
    fig, ax = fig_ax(9, max(3.5, 0.42 * len(school_counts)))
    bars = ax.barh(school_counts.index, school_counts.values, color=PALETTE[1])
    ax.bar_label(bars, padding=3, fontsize=9)
    ax.set_xlabel("Publications")
    st.pyplot(fig, use_container_width=True)

    st.markdown('<div class="section-title">School Output Over Time (Top 6 Schools)</div>', unsafe_allow_html=True)
    top6 = fdf["School_clean"].value_counts().head(6).index.tolist()
    pivot = (
        fdf[fdf["School_clean"].isin(top6) & fdf["Year_num"].notna()]
        .assign(Year_num=lambda d: d["Year_num"].astype(int))
        .groupby(["Year_num", "School_clean"]).size().unstack(fill_value=0)
    )
    if not pivot.empty:
        fig, ax = fig_ax(9, 4.5)
        for i, col in enumerate(pivot.columns):
            ax.plot(pivot.index, pivot[col], marker="o", label=col, color=PALETTE[i % len(PALETTE)])
        ax.set_xlabel("Year"); ax.set_ylabel("Publications")
        ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        ax.legend(fontsize=8, ncol=2, frameon=False)
        st.pyplot(fig, use_container_width=True)

    st.markdown('<div class="section-title">School Quality Snapshot</div>', unsafe_allow_html=True)
    snap = fdf.groupby("School_clean").agg(
        Publications=("Title", "count"),
        Scopus=("is_scopus", "sum"),
        WoS=("is_wos", "sum"),
        Q1=("Quartile_clean", lambda s: (s == "Q1").sum()),
        Faculty=("Faculty_primary", lambda s: len(set(x for x in s if x))),
    ).sort_values("Publications", ascending=False)
    st.dataframe(snap, use_container_width=True)

# ---------------- RESEARCHERS TAB ----------------
with tab_people:
    st.markdown('<div class="section-title">Top Contributing Faculty</div>', unsafe_allow_html=True)
    fac_counter = Counter(f for lst in fdf["Faculty_list"] for f in lst if f)
    top_n = st.slider("Show top N authors", 5, min(30, max(5, len(fac_counter))), min(15, len(fac_counter)) or 5)
    top_fac = pd.Series(dict(fac_counter.most_common(top_n))).sort_values(ascending=True)
    if not top_fac.empty:
        fig, ax = fig_ax(9, max(3.5, 0.35 * len(top_fac)))
        bars = ax.barh(top_fac.index, top_fac.values, color=PALETTE[2])
        ax.bar_label(bars, padding=3, fontsize=9)
        ax.set_xlabel("Publications")
        st.pyplot(fig, use_container_width=True)

    # ---- Faculty photo gallery (top contributors) ----
    st.markdown('<div class="section-title">Faculty Directory</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-caption">Top contributors in the current filter selection.</div>',
                unsafe_allow_html=True)
    gallery = fac_counter.most_common(min(12, len(fac_counter)))
    if gallery:
        gcols = st.columns(6)
        for i, (name, count) in enumerate(gallery):
            with gcols[i % 6]:
                st.image(avatar_url(name, FACULTY_PHOTOS), use_container_width=True)
                st.markdown(f"**{name}**", help=name)
                st.caption(f"{count} publication{'s' if count != 1 else ''}")
            if i % 6 == 5 and i != len(gallery) - 1:
                gcols = st.columns(6)

    st.markdown('<div class="section-title">Researcher Profile</div>', unsafe_allow_html=True)
    all_authors_sorted = sorted(fac_counter.keys())
    if all_authors_sorted:
        chosen = st.selectbox("Select a researcher", all_authors_sorted)
        prof_df = fdf[fdf["Faculty_list"].apply(lambda lst: chosen in lst)]

        pimg, pinfo = st.columns([1, 4])
        with pimg:
            st.image(avatar_url(chosen, FACULTY_PHOTOS), use_container_width=True)
        with pinfo:
            st.markdown(f"### {chosen}")
            st.caption(f"School: {prof_df['School_clean'].mode().iloc[0] if not prof_df.empty else '—'} · "
                       f"Designation: {prof_df['Designation_clean'].mode().iloc[0] if not prof_df.empty else '—'}")
            pc1, pc2, pc3, pc4 = st.columns(4)
            pc1.metric("Publications", len(prof_df))
            pc2.metric("Scopus", int(prof_df["is_scopus"].sum()))
            pc3.metric("WoS", int(prof_df["is_wos"].sum()))
            pc4.metric("Q1 papers", int((prof_df["Quartile_clean"] == "Q1").sum()))

        by_year = prof_df.dropna(subset=["Year_num"]).groupby(prof_df["Year_num"].astype(int)).size()
        if not by_year.empty:
            fig, ax = fig_ax(8, 3.2)
            ax.bar(by_year.index, by_year.values, color=PALETTE[3])
            ax.set_xlabel("Year"); ax.set_ylabel("Publications")
            ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
            st.pyplot(fig, use_container_width=True)
        st.dataframe(
            prof_df[["Year", "Title", "Source title", "Document Type", "Indexing_clean", "Quartile_clean"]]
            .rename(columns={"Indexing_clean": "Indexing", "Quartile_clean": "Quartile"})
            .sort_values("Year", ascending=False),
            use_container_width=True, hide_index=True,
        )

# ---------------- SDG TAB ----------------
with tab_sdg:
    st.markdown('<div class="section-title">SDG Distribution</div>', unsafe_allow_html=True)
    sdg_counter = Counter(s for lst in fdf["SDG_list"] for s in lst)
    if sdg_counter:
        sdg_series = pd.Series(sdg_counter).sort_index(key=lambda idx: idx.astype(int))
        labels = [f"SDG {i}" for i in sdg_series.index]
        fig, ax = fig_ax(9, 4.5)
        bars = ax.bar(labels, sdg_series.values, color=PALETTE * 3)
        ax.bar_label(bars, padding=3, fontsize=8)
        ax.set_ylabel("Publications")
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        st.pyplot(fig, use_container_width=True)

        st.markdown('<div class="section-title">SDG × School Heatmap</div>', unsafe_allow_html=True)
        exploded = fdf.explode("SDG_list").dropna(subset=["SDG_list"])
        exploded = exploded[exploded["SDG_list"] != ""]
        if not exploded.empty:
            heat = exploded.pivot_table(index="School_clean", columns="SDG_list", values="Title",
                                         aggfunc="count", fill_value=0)
            heat = heat.reindex(sorted(heat.columns, key=lambda x: int(x)), axis=1)
            fig, ax = fig_ax(max(8, 0.55 * len(heat.columns)), max(3.5, 0.5 * len(heat)))
            sns.heatmap(heat, annot=True, fmt="g", cmap="Blues", ax=ax, cbar_kws={"label": "Publications"})
            ax.set_xlabel("SDG"); ax.set_ylabel("")
            st.pyplot(fig, use_container_width=True)

        with st.expander("SDG legend"):
            for s in sorted(sdg_counter.keys(), key=lambda x: int(x)):
                st.write(f"**SDG {s}** — {SDG_NAMES.get(s, 'Unlabeled')} ({sdg_counter[s]} publications)")
    else:
        st.info("No SDG tags found in the current filter selection.")

# ---------------- EXPLORER TAB ----------------
with tab_explorer:
    st.markdown('<div class="section-title">Publication Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-caption">Search, sort and open any publication or DOI link directly.</div>',
                unsafe_allow_html=True)

    exp_search = st.text_input("Search within filtered results (title, author, keyword, publisher)", "")
    view = fdf.copy()
    if exp_search.strip():
        q = exp_search.strip().lower()
        view = view[
            view["Title"].str.lower().str.contains(q, na=False) |
            view["Authors"].str.lower().str.contains(q, na=False) |
            view["Keywords"].str.lower().str.contains(q, na=False) |
            view["Publisher_clean"].str.lower().str.contains(q, na=False)
        ]

    sort_col = st.selectbox("Sort by", ["Year", "Title", "School_clean", "Quartile_clean", "DocType_clean"], index=0)
    sort_dir = st.radio("Order", ["Descending", "Ascending"], horizontal=True, index=0)
    view = view.sort_values(sort_col, ascending=(sort_dir == "Ascending"))

    display_cols = {
        "Year": "Year", "Title": "Title", "Authors": "Authors", "School_clean": "School",
        "Source title": "Source", "DocType_clean": "Type", "Indexing_clean": "Indexing",
        "Quartile_clean": "Quartile", "Best_link": "Link",
    }
    show_df = view[list(display_cols.keys())].rename(columns=display_cols)

    st.dataframe(
        show_df,
        use_container_width=True,
        hide_index=True,
        height=520,
        column_config={
            "Link": st.column_config.LinkColumn("Link", display_text="Open ↗"),
            "Title": st.column_config.TextColumn("Title", width="large"),
        },
    )

    csv_buffer = io.StringIO()
    view.drop(columns=["Faculty_list", "All_authors_list", "SDG_list"], errors="ignore").to_csv(csv_buffer, index=False)
    st.download_button(
        "⬇️ Export filtered results as CSV",
        data=csv_buffer.getvalue(),
        file_name=f"saiu_publications_export_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )

st.markdown("---")
st.caption("Sai University Research Intelligence Dashboard · Data fetched live from the Publications API · "
           "Built with Streamlit, Pandas, Matplotlib & Seaborn.")