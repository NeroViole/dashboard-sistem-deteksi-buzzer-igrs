# -*- coding: utf-8 -*-
"""Dashboard Deteksi Buzzer Terkoordinasi IGRS — Streamlit (tema editorial).
Semua angka di-import & dihitung dari folder data/ lewat data_loader.py.
"""
import html
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import data_loader as dl
import importlib
importlib.reload(dl)

st.set_page_config(page_title="Deteksi Buzzer IGRS", page_icon="🔍", layout="wide")

# ====================== PALET (editorial) ======================
BG = "#F3EFE6"; SURFACE = "#FBF9F3"; SURFACE2 = "#EFEADD"; RAISED = "#FFFFFF"
TEXT = "#211E17"; TEXT2 = "#433E33"; MUTED = "#4D473B"
ACCENT = "#9B4A2C"; SLATE = "#46546B"; BUZZER = "#A8472F"; ORGANIC = "#5E7152"; OCHRE = "#A6822B"
GRID = "rgba(38,33,25,0.10)"

# Mapping cluster_id ke Nama Tema deskriptif
CLUSTER_NAMES = {
    1: "Klaster 1 · Narasi Self-Declare (Buzzer)",
    2: "Klaster 2 · Rilis/Siaran Pers (Buzzer)",
    3: "Klaster 3 · Diskusi Regulasi (Campuran)",
    0: "Klaster 0 · Keluhan IGRS (Organik)",
    4: "Klaster 4 · Pengaruh Varka (Organik)",
    5: "Klaster 5 · Steam vs IGRS (Organik)",
    6: "Klaster 6 · Kritik & Sumpah Serapah (Organik)",
    7: "Klaster 7 · Khawatir Ban Akun (Organik)",
    8: "Klaster 8 · Komunitas Gamer (Organik)",
    9: "Klaster 9 · Masalah Parenting (Organik)"
}


CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,400&family=Inter:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* Force Streamlit CSS Variables to Light Theme values */
:root, [data-testid="stAppViewContainer"], .stApp, html, body {
    --background-color: #F3EFE6 !important;
    --secondary-background-color: #EFEADD !important;
    --text-color: #211E17 !important;
    --primary-color: #9B4A2C !important;
}

.stApp { background: #F3EFE6; }
.block-container { max-width: 1180px; padding-top: 2.2rem; padding-bottom: 4rem; }
html, body, [class*="css"] { font-family: 'Inter', system-ui, sans-serif; color: #211E17; }
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; }

.eyebrow { font-family:'DM Mono',monospace; font-size:11px; letter-spacing:.22em; text-transform:uppercase; color:#9B4A2C; margin-bottom:10px; }
h1.title { font-family:'Fraunces',Georgia,serif; font-weight:500; font-size:clamp(28px,4vw,46px); line-height:1.05; letter-spacing:-.01em; color:#211E17; margin:0; max-width:20ch; }
.subtitle { font-family:'Fraunces',serif; font-style:italic; font-weight:400; color:#433E33; font-size:clamp(15px,1.8vw,20px); margin-top:12px; max-width:58ch; }
.byline { display:flex; flex-wrap:wrap; gap:6px 20px; margin-top:18px; font-family:'DM Mono',monospace; font-size:11.5px; color:#4D473B; letter-spacing:.02em; }
.byline b { color:#9B4A2C; font-weight:500; }
.rule { height:1px; background:rgba(38,33,25,0.22); margin:22px 0 4px; }

.lead { font-family:'Fraunces',serif; font-size:19px; line-height:1.5; color:#433E33; max-width:64ch; margin:6px 0 4px; }
.lead .hl { color:#9B4A2C; font-style:italic; }
.kicker { font-family:'DM Mono',monospace; font-size:11px; letter-spacing:.18em; text-transform:uppercase; color:#9B4A2C; display:flex; align-items:center; gap:10px; margin:30px 0 14px; }
.kicker::after { content:""; flex:1; height:1px; background:rgba(38,33,25,0.13); }
.note { color:#4D473B; font-size:13.5px; max-width:74ch; margin:-4px 0 14px; line-height:1.55; }

.stat { background:#FBF9F3; border:1px solid rgba(38,33,25,0.13); border-radius:4px; padding:18px 18px 16px; position:relative; overflow:hidden; height:100%; }
.stat .lab { font-family:'DM Mono',monospace; font-size:10px; letter-spacing:.12em; text-transform:uppercase; color:#4D473B; }
.stat .val { font-family:'Fraunces',serif; font-weight:500; font-size:34px; line-height:1; margin-top:10px; letter-spacing:-.01em; color:#211E17; }
.stat .sub { font-size:12px; color:#4D473B; margin-top:6px; line-height:1.4; }
.stat .bar { position:absolute; left:0; top:0; bottom:0; width:3px; background:#9B4A2C; }
.stat.buzzer .val{color:#A8472F} .stat.buzzer .bar{background:#A8472F}
.stat.organic .val{color:#5E7152} .stat.organic .bar{background:#5E7152}
.stat.slate .val{color:#46546B} .stat.slate .bar{background:#46546B}

.callout { background:#EFEADD; border:1px solid rgba(38,33,25,0.13); border-left:3px solid #A6822B; border-radius:4px; padding:15px 18px; font-size:13.5px; color:#433E33; line-height:1.6; margin:6px 0; }
.callout b { color:#211E17; }
.callout.accent { border-left-color:#9B4A2C; }
.callout.buzzer { border-left-color:#A8472F; }

.pstep { background:#FBF9F3; border:1px solid rgba(38,33,25,0.13); border-radius:4px; padding:13px 14px; height:100%; }
.pstep .pn { font-family:'DM Mono',monospace; font-size:10px; color:#9B4A2C; letter-spacing:.1em; }
.pstep .pt { font-size:12.5px; font-weight:600; margin-top:5px; line-height:1.25; color:#211E17; }
.pstep .big { font-family:'Fraunces',serif; font-size:21px; font-weight:500; color:#211E17; margin-top:3px; }
.pstep .pd { font-family:'DM Mono',monospace; font-size:10.5px; color:#4D473B; margin-top:3px; }

.foldcard { background:#FBF9F3; border:1px solid rgba(38,33,25,0.13); border-radius:4px; padding:10px 12px 6px; text-align:center; height:100%; }
.foldcard .fn { font-family:'DM Mono',monospace; font-size:10px; letter-spacing:.12em; color:#9B4A2C; text-transform:uppercase; }
.foldcard .fm { font-family:'DM Mono',monospace; font-size:10.5px; color:#4D473B; margin-top:4px; line-height:1.5; }
.foldcard .fm b { color:#211E17; }

.lda-card { background:#FBF9F3; border:1px solid rgba(38,33,25,0.13); border-radius:4px; padding:18px; border-top:3px solid #46546B; height:100%; }
.lda-card.named { border-top-color:#9B4A2C; }
.lda-id { font-family:'DM Mono',monospace; font-size:10.5px; color:#4D473B; letter-spacing:.1em; }
.lda-name { font-family:'Fraunces',serif; font-size:17px; font-weight:500; margin:6px 0 10px; line-height:1.25; color:#211E17; }
.lda-desc { font-size:12.5px; color:#433E33; line-height:1.5; }
.tag { display:inline-block; font-family:'DM Mono',monospace; font-size:10.5px; color:#433E33; background:#EFEADD; border:1px solid rgba(38,33,25,0.13); border-radius:3px; padding:3px 9px; margin:4px 4px 0 0; }
.blockq { font-family:'Fraunces',serif; font-style:italic; font-size:13.5px; line-height:1.5; color:#433E33; border-left:3px solid #A8472F; padding:6px 0 6px 14px; margin:8px 0 2px; }
.tw-meta { font-family:'DM Mono',monospace; font-size:10.5px; color:#4D473B; margin:0 0 10px 14px; }
.tw-meta a { color:#9B4A2C; text-decoration:none; }

.stTabs [data-baseweb="tab-list"] { gap:2px; border-bottom:1px solid rgba(38,33,25,0.22); }
.stTabs [data-baseweb="tab"] { font-family:'Inter',sans-serif; font-size:13.5px; font-weight:500; color:#4D473B; padding:12px 18px; }
.stTabs [aria-selected="true"] { color:#211E17 !important; border-bottom:2px solid #9B4A2C; }
footer.cred { border-top:1px solid rgba(38,33,25,0.22); margin-top:40px; padding:24px 0 10px; color:#4D473B; font-size:12px; font-family:'DM Mono',monospace; line-height:1.6; }

/* Override Streamlit elements to prevent grey/white text on light background */
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p,
[data-testid="stCaptionContainer"] span,
.stCaption,
.stCaption p,
.stCaption span,
caption {
    color: #4D473B !important;
}
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] p,
[data-testid="stMetricLabel"] span,
.stMetric label {
    color: #4D473B !important;
}
[data-testid="stMetricValue"],
[data-testid="stMetricValue"] p,
[data-testid="stMetricValue"] span {
    color: #211E17 !important;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span,
.streamlit-expanderHeader,
.streamlit-expanderHeader p {
    color: #211E17 !important;
}
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span {
    color: #211E17 !important;
}
input, textarea, select {
    color: #211E17 !important;
}
input::placeholder, textarea::placeholder {
    color: #4D473B !important;
    opacity: 0.85 !important;
}

/* ── Force light-mode pada SEMUA elemen Streamlit (fix Streamlit Cloud dark-mode) ── */
/* Dataframe / Table */
[data-testid="stDataFrame"],
[data-testid="stDataFrame"] * ,
[data-testid="stTable"],
[data-testid="stTable"] * {
    color: #211E17 !important;
    background-color: transparent !important;
}
[data-testid="stDataFrame"] [data-testid="glideDataEditor"],
[data-testid="stDataFrame"] table {
    background-color: #FBF9F3 !important;
}
[data-testid="stDataFrame"] th,
[data-testid="stTable"] th {
    background-color: #EFEADD !important;
    color: #211E17 !important;
}
[data-testid="stDataFrame"] td,
[data-testid="stTable"] td {
    background-color: #FBF9F3 !important;
    color: #211E17 !important;
}
/* Glide Data Editor cells (used by st.dataframe internally) */
[data-testid="stDataFrame"] div[class*="cell"],
[data-testid="stDataFrame"] div[class*="header"] {
    color: #211E17 !important;
}

/* Selectbox, multiselect, radio, checkbox labels */
[data-testid="stSelectbox"] label,
[data-testid="stMultiSelect"] label,
[data-testid="stRadio"] label,
[data-testid="stCheckbox"] label,
[data-testid="stNumberInput"] label,
[data-testid="stTextInput"] label {
    color: #211E17 !important;
}

/* Selectbox and Text Input styling (Default / Light Mode) */
[data-baseweb="select"] span,
[data-baseweb="select"] div {
    color: #211E17 !important;
}
input, textarea {
    color: #211E17 !important;
}

/* Dark Mode overrides for inputs when browser prefers dark theme */
@media (prefers-color-scheme: dark) {
    [data-baseweb="select"] span,
    [data-baseweb="select"] div {
        color: #FFFFFF !important;
    }
    input, textarea {
        color: #FFFFFF !important;
    }
    input::placeholder, textarea::placeholder {
        color: rgba(255, 255, 255, 0.5) !important;
        opacity: 1 !important;
    }
}
[data-baseweb="popover"],
[data-baseweb="menu"],
ul[role="listbox"] {
    background-color: #FBF9F3 !important;
    color: #211E17 !important;
}
ul[role="listbox"] li {
    color: #211E17 !important;
}
ul[role="listbox"] li:hover {
    background-color: #EFEADD !important;
}

/* Markdown text */
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] li {
    color: #211E17 !important;
}

/* Sidebar */
[data-testid="stSidebar"],
[data-testid="stSidebar"] * {
    color: #211E17 !important;
}
[data-testid="stSidebar"] {
    background-color: #EFEADD !important;
}

/* Overall app background override */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #F3EFE6 !important;
    color: #211E17 !important;
}

/* Plotly chart backgrounds */
[data-testid="stPlotlyChart"] {
    background-color: transparent !important;
}

/* Force all buttons to have consistent ACCENT background and white text */
div[data-testid="stButton"] button {
    background-color: #9B4A2C !important;
    color: #FFFFFF !important;
    border: 1px solid #9B4A2C !important;
    border-radius: 4px !important;
    transition: background-color 0.2s ease, border-color 0.2s ease !important;
}
div[data-testid="stButton"] button:hover {
    background-color: #A8472F !important;
    border-color: #A8472F !important;
    color: #FFFFFF !important;
}

/* Force all Plotly legend text and chart labels/titles to be dark/black */
g.legend text,
text.legendtext,
g.xtick text,
g.ytick text,
g.gtitle text,
g.annotation text {
    fill: #211E17 !important;
}
"""

st.markdown("<style>" + CSS + "</style>", unsafe_allow_html=True)

D = dl.load_all()


@st.cache_data
def load_tweets_scored():
    import os
    import pandas as pd
    path = os.path.join(dl.DATA_DIR, "tweets_scored.csv")
    df = pd.read_csv(path)
    df["dt"] = pd.to_datetime(df["created_at"])
    df["hour_bin"] = df["dt"].dt.floor("h")
    return df



# ====================== HELPERS ======================
def stat(lab, val, sub="", kind=""):
    return ('<div class="stat ' + kind + '"><div class="bar"></div><div class="lab">' + str(lab)
            + '</div><div class="val">' + str(val) + '</div><div class="sub">' + str(sub) + '</div></div>')


def stat_row(items):
    cols = st.columns(len(items))
    for c, it in zip(cols, items):
        c.markdown(stat(*it[:3], kind=it[3] if len(it) > 3 else ""), unsafe_allow_html=True)


def kicker(t):
    st.markdown('<div class="kicker">' + t + '</div>', unsafe_allow_html=True)


def lead(t):
    st.markdown('<p class="lead">' + t + '</p>', unsafe_allow_html=True)


def note(t):
    st.markdown('<p class="note">' + t + '</p>', unsafe_allow_html=True)


def callout(t, kind=""):
    st.markdown('<div class="callout ' + kind + '">' + t + '</div>', unsafe_allow_html=True)


def style(fig, h=320, title=None):
    title_arg = dict(text=title, font=dict(family="Fraunces, serif", size=15, color=TEXT), x=0.01) if title else dict(text="")
    fig.update_layout(
        height=h, margin=dict(l=10, r=10, t=40 if title else 12, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=TEXT, size=12),
        title=title_arg,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
        colorway=[ACCENT, SLATE, ORGANIC, OCHRE, BUZZER],
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False, linecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, linecolor=GRID)
    return fig


def cm_fig(cm, scale, h=300, title=None, small=False):
    z = [[cm["TN"], cm["FP"]], [cm["FN"], cm["TP"]]]
    xlab = ["Pred Org", "Pred Buz"] if small else ["Pred Organik", "Pred Buzzer"]
    ylab = ["Akt Org", "Akt Buz"] if small else ["Aktual Organik", "Aktual Buzzer"]
    fig = px.imshow(z, text_auto=True, color_continuous_scale=scale, x=xlab, y=ylab)
    fig.update_coloraxes(showscale=False)
    fig.update_traces(textfont=dict(size=15 if small else 22, family="Fraunces, serif"))
    fig = style(fig, h, title)
    if small:
        fig.update_xaxes(tickfont=dict(size=9))
        fig.update_yaxes(tickfont=dict(size=9))
    return fig


# ====================== MASTHEAD ======================
pl = D["pipeline"]; smp = D["sampling"]; acc = D["accounts"]; th = D["threshold"]
st.markdown('<h1 class="title">Deteksi Akun Buzzer Terkoordinasi pada Diskursus Kebijakan IGRS</h1>', unsafe_allow_html=True)
st.markdown(
    '<div class="byline"><span><b>' + f'{pl["final"]:,}' + '</b> tweet bersih</span>'
    '<span><b>' + f'{acc["total_accounts"]:,}' + '</b> akun unik</span>'
    '<span><b>' + f'{smp["n"]}' + '</b> ground truth · Kappa <b>' + f'{smp["kappa"]:.4f}' + '</b></span>'
    '<span><b>' + f'{acc["n_buzzer"]}' + '</b> akun buzzer</span>'
    '<span>Threshold final <b>' + f'{th["final_threshold"]}' + '</b></span></div>',
    unsafe_allow_html=True)
st.markdown('<div class="rule"></div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "  01 · Validasi Model  ", "  02 · Hasil Investigasi  ",
    "  03 · Analisis Narasi  ", "  04 · Jaringan Serangan  "])

# ============================================================
# TAB 1 — VALIDASI MODEL
# ============================================================
with tab1:
    lead('Sebelum menuduh satu akun pun, model harus terbukti <span class="hl">dapat dipercaya</span>. Bagian ini memaparkan output teknis machine learning: pelabelan manusia, reliabilitas, performa lintas-fold beserta confusion matrix tiap fold, kalibrasi threshold, dan penjelasan fitur.')

    kicker("Pipeline Penyiapan Data")
    steps = [
        ("01", "Data Mentah", f'{pl["raw"]:,}', "tweet terkumpul"),
        ("02", "Filter Bahasa", f'{pl["after_noise"]:,}', f'{pl["n_language_noise"]} noise dibuang'),
        ("03", "Buang Spam", f'{pl["final"]:,}', f'{pl["n_spam"]} spam dibuang'),
        ("04", "Tweet Bersih", f'{pl["final"]:,}', f'{pl["n_accounts"]} akun unik'),
        ("05", "Ground Truth", f'{smp["n"]}', f'κ = {smp["kappa"]:.3f}'),
        ("06", "Terapkan Model", f'{acc["buzzer_tweets"]}', f'tweet buzzer · {acc["n_buzzer"]} akun'),
    ]
    cols = st.columns(len(steps))
    for c, (n, t, b, d) in zip(cols, steps):
        c.markdown('<div class="pstep"><div class="pn">' + n + '</div><div class="pt">' + t + '</div><div class="big">' + b + '</div><div class="pd">' + d + '</div></div>', unsafe_allow_html=True)

    kicker("Ground Truth & Reliabilitas Antar-Anotator")
    stat_row([
        ("Sampel Berlabel", f'{smp["n"]}', "dua anotator independen"),
        ("Cohen's Kappa", f'{smp["kappa"]:.3f}', f'{smp["agree"]}/{smp["n"]} sepakat ({smp["agree_pct"]*100:.1f}%) — hampir sempurna'),
        ("Label Buzzer", f'{smp["gt_buzzer"]}', f'{smp["gt_buzzer"]/smp["n"]*100:.1f}% ground truth', "buzzer"),
        ("Label Organik", f'{smp["gt_organic"]}', f'{smp["gt_organic"]/smp["n"]*100:.1f}% ground truth', "organic"),
    ])

    kicker("Mengapa Tidak Cukup Pakai Aturan (Heuristik)?")
    ha = D["heur_audit"]
    c1, c2 = st.columns([1, 1])
    with c1:
        st.plotly_chart(cm_fig(smp["heur_cm"], "oranges", 300,
                       f'Heuristik is_coordinated vs label manusia · akurasi {smp["heur_acc"]*100:.1f}%'),
                       use_container_width=True)
    with c2:
        callout('<b>Aturan saja tidak cukup.</b> Rule <code>is_coordinated</code> hanya mencapai akurasi '
                + f'{ha["heuristic_accuracy"]*100:.0f}' + '% dengan recall ' + f'{ha["heuristic_recall"]*100:.0f}'
                + '% — menghasilkan ' + f'{smp["heur_cm"]["FP"]}' + ' false positive dan melewatkan '
                + f'{smp["heur_cm"]["FN"]}' + ' buzzer. Model XGBoost yang dilatih dari label manusia menaikkan akurasi ke '
                + f'{ha["ai_accuracy"]*100:.1f}' + '% dan recall ke ' + f'{ha["ai_recall"]*100:.1f}' + '%. '
                + str(ha["improvement_note"]), "accent")

    kicker("5-Fold Stratified Cross-Validation — Metrik per Fold")
    fo = D["folds"]
    fdf = pd.DataFrame(fo["folds"])
    metrics = ["accuracy", "precision", "recall", "f1", "roc_auc"]
    figf = go.Figure()
    palette = [ACCENT, SLATE, ORGANIC, OCHRE, BUZZER]
    for i, m in enumerate(metrics):
        figf.add_bar(
            name=m, 
            x=[f'Fold {int(k)}' for k in fdf["fold"]], 
            y=(fdf[m] * 100), 
            marker_color=palette[i],
            text=[f'{val:.1f}%' for val in (fdf[m] * 100)],
            textposition="auto"
        )
    figf.update_layout(barmode="group")
    figf.update_yaxes(title="%", range=[60, 100])
    st.plotly_chart(style(figf, 360, "Metrik per fold (%)"), use_container_width=True)
    ci = fo.get("wilson_ci")
    cistr = ' Interval kepercayaan Wilson 95%: ' + f'{ci[0]*100:.1f}–{ci[1]*100:.1f}' + '%.' if ci else ""
    note('Rerata 5-fold: akurasi <b>' + f'{fo["mean_accuracy"]*100:.1f}' + '%</b> · presisi ' + f'{fo["mean_precision"]*100:.1f}'
         + '% · recall ' + f'{fo["mean_recall"]*100:.1f}' + '% · F1 ' + f'{fo["mean_f1"]*100:.1f}' + '% · ROC-AUC '
         + f'{fo["mean_auc"]*100:.1f}' + '%.' + cistr + ' Fold 4 sedikit menurun (recall turun) — lihat confusion matrix di bawah.')

    kicker("5 Confusion Matrix — Satu per Fold")
    note("Tiap fold menguji subset ground truth yang berbeda. Lima matriks ini memperlihatkan True/False Positive & Negative pada masing-masing fold — transparansi penuh performa lintas-fold.")
    kcm = D["kfold_cm"]["folds"]
    fcols = st.columns(5)
    scales = ["tealgrn", "blues", "purples", "oranges", "greens"]
    for i, (c, fd) in enumerate(zip(fcols, kcm)):
        with c:
            st.plotly_chart(cm_fig(fd["cm"], scales[i % len(scales)], 200, f"Fold {fd['fold']}", small=True), use_container_width=True)
            c.markdown('<div class="foldcard"><div class="fn">Fold ' + str(fd["fold"]) + ' · n=' + str(fd["n"])
                       + '</div><div class="fm">Akurasi <b>' + f'{fd["accuracy"]*100:.1f}' + '%</b><br>Presisi <b>'
                       + f'{fd["precision"]*100:.0f}' + '%</b> · Recall <b>' + f'{fd["recall"]*100:.0f}'
                       + '%</b><br>F1 <b>' + f'{fd["f1"]*100:.0f}' + '%</b></div></div>', unsafe_allow_html=True)

    kicker(f'Model Final & Matriks Kebingungan (Threshold {th["final_threshold"]})')
    c1, c2 = st.columns([1, 1])
    with c1:
        st.plotly_chart(cm_fig(th["holdout_cm"], "tealgrn", 320,
                       f'Confusion matrix holdout (n={th["n_test"]})'), use_container_width=True)
    with c2:
        cm = th["holdout_cm"]
        stat_row([
            ("Presisi (Buzzer)", f'{th["precision"]*100:.0f}%', f'{cm["FP"]} false positive', "slate"),
            ("Recall (Buzzer)", f'{th["recall"]*100:.0f}%', "konservatif by design"),
        ])
        st.write("")
        stat_row([
            ("F1-Score", f'{th["f1"]*100:.0f}%', f'pada τ={th["final_threshold"]}'),
            ("ROC-AUC (CV)", f'{fo["mean_auc"]:.2f}', "rata-rata 5-fold", "organic"),
        ])
    callout('<b>Threshold dinaikkan ke ' + f'{th["final_threshold"]}' + ' demi presisi maksimum.</b> Untuk tuduhan investigatif, menghindari <i>false accusation</i> lebih utama daripada menangkap semua kasus. Hasilnya: <b>'
            + f'{cm["FP"]}' + ' false positive</b> pada data uji.', "buzzer")

    kicker("Kalibrasi Threshold")
    tdf = pd.DataFrame(th["rows"])
    figt = go.Figure()
    for m, col in [("precision", ACCENT), ("recall", SLATE), ("f1", ORGANIC)]:
        figt.add_scatter(
            x=tdf["threshold"], 
            y=tdf[m], 
            name=m, 
            mode="lines+markers+text", 
            text=tdf[m].round(2),
            textposition="top center",
            line=dict(color=col, width=2)
        )
    figt.add_vline(x=th["final_threshold"], line=dict(color=BUZZER, dash="dash"))
    st.plotly_chart(style(figt, 320, "Presisi vs Recall vs F1 terhadap threshold"), use_container_width=True)

    kicker("SHAP — Kontribusi Fitur (Mean |SHAP|)")
    sh = pd.DataFrame(D["shap"]["rows"]).sort_values("value")
    figs = go.Figure(go.Bar(
        x=sh["value"], 
        y=sh["feature"], 
        orientation="h", 
        marker_color=ACCENT,
        text=sh["value"].round(2),
        textposition="outside",
        name="SHAP"
    ))
    figs.update_layout(showlegend=False)
    st.plotly_chart(style(figs, 340, "SHAP"), use_container_width=True)
    top_feat = D["shap"]["rows"][0]["feature"]
    note('Fitur semantik (SBERT) mendominasi: <b>' + str(top_feat) + '</b> adalah penanda koordinasi terkuat — kemiripan <i>makna</i> antar-tweet lebih menentukan daripada duplikasi kata-per-kata maupun struktur jaringan.')

    kicker("DBSCAN — Sensitivitas Epsilon")
    db = D["dbscan"]
    ddf = pd.DataFrame(db["rows"])
    figd = go.Figure()
    figd.add_bar(
        x=ddf["eps"], 
        y=ddf["n_noise"], 
        name="Noise", 
        marker_color=SLATE, 
        yaxis="y",
        text=ddf["n_noise"],
        textposition="outside"
    )
    figd.add_scatter(
        x=ddf["eps"], 
        y=ddf["n_clusters"], 
        name="Jml klaster", 
        mode="lines+markers+text", 
        text=ddf["n_clusters"],
        textposition="bottom center",
        textfont=dict(color="white", size=10, family="Inter, sans-serif"),
        line=dict(color=ACCENT, width=2), 
        yaxis="y2"
    )
    figd.add_vline(x=db["chosen_eps"], line=dict(color=BUZZER, dash="dash"))
    figd.update_layout(yaxis=dict(title="Noise"), yaxis2=dict(title="Klaster", overlaying="y", side="right"))
    st.plotly_chart(style(figd, 320, "Sensitivitas DBSCAN: noise & jumlah klaster vs epsilon"), use_container_width=True)
    note('Epsilon <b>' + f'{db["chosen_eps"]}' + '</b> (cosine) dipilih sebagai keseimbangan: cukup ketat untuk memisahkan klaster naratif yang koheren, namun tidak terlalu longgar. Garis merah menandai nilai yang dipakai.')

# ============================================================
# TAB 2 — HASIL INVESTIGASI
# ============================================================
with tab2:
    lead('Setelah divalidasi, model diterapkan ke <span class="hl">seluruh ' + f'{pl["final"]:,}' + ' tweet</span>. Inilah peta hasil investigasi pada tingkat tweet dan akun.')

    kicker("Ringkasan Hasil")
    org_tweets = acc["total_tweets"] - acc["buzzer_tweets"]
    stat_row([
        ("Total Tweet", f'{acc["total_tweets"]:,}', "dianalisis penuh"),
        ("Tweet Buzzer", f'{acc["buzzer_tweets"]}', f'{acc["buzzer_tweet_pct"]*100:.1f}% dari total', "buzzer"),
        ("Tweet Organik", f'{org_tweets:,}', f'{(1-acc["buzzer_tweet_pct"])*100:.1f}% dari total', "organic"),
        ("Akun Buzzer", f'{acc["n_buzzer"]}', f'dari {acc["total_accounts"]} akun unik', "buzzer"),
    ])

    kicker("Distribusi Probabilitas Buzzer (per Tweet)")
    pr = D["prob"]
    high = pr["counts"][-1]
    figp = go.Figure(go.Bar(x=pr["labels"], y=pr["counts"],
                            marker_color=[ORGANIC, OCHRE, MUTED, SLATE, BUZZER],
                            text=pr["counts"], textposition="outside"))
    figp.update_yaxes(type="log", title="jumlah tweet (log)")
    figp.update_layout(showlegend=False)
    st.plotly_chart(style(figp, 320, "Distribusi skor probabilitas buzzer"), use_container_width=True)
    note('Distribusi sangat <b>bimodal</b>: ' + f'{pr["counts"][0]:,}' + ' tweet menumpuk di ujung rendah (jelas organik), sementara <b>'
         + str(high) + '</b> tweet terkonsentrasi di ujung tinggi (≥0,8). Pola terbelah ini adalah tanda khas populasi terkoordinasi yang terpisah dari percakapan alami.')

    kicker("Akun Terindikasi Buzzer — Klik untuk Semua Twit & Reply-out")
    note('Seluruh <b>' + f'{acc["n_buzzer"]}' + ' akun buzzer</b> diurutkan menurun berdasarkan probabilitas. Klik tiap akun untuk melihat <b>semua isi twit buzzernya</b> dan <b>semua akun yang dibalas (reply-out)</b>.')
    q = st.text_input("Cari username", "", placeholder="mis. rahayu49384")
    
    if "show_all_buzzers" not in st.session_state:
        st.session_state.show_all_buzzers = False
        
    limit = 5 if not st.session_state.show_all_buzzers and not q else None
    
    shown = 0
    total_matching = 0
    for i, a in enumerate(acc["top"], 1):
        if q and q.lower() not in a["username"].lower():
            continue
        total_matching += 1
        if limit is not None and shown >= limit:
            continue
        shown += 1
        head = ('#' + str(i) + ' · @' + a["username"] + ' — prob ' + f'{a["prob"]:.3f}'
                + ' · ' + str(a["n_buzzer_tweets"]) + '/' + str(a["n_tweets"]) + ' twit buzzer · '
                + str(len(a["reply_out"])) + ' reply-out')
        with st.expander(head):
            st.markdown(
                f'<div style="margin-bottom:12px; font-size:13px;">'
                f'🔗 <b>Profil X (Twitter):</b> '
                f'<a href="https://x.com/{a["username"]}" target="_blank" style="color:{ACCENT}; text-decoration:none; font-weight:bold;">'
                f'@{a["username"]} di X (Twitter) ↗'
                f'</a>'
                f'</div>',
                unsafe_allow_html=True
            )
            m = st.columns(5)
            m[0].metric("Duplikasi konten", f'{a["dup"]:.3f}')
            m[1].metric("Kemiripan leksikal", f'{a["lex"]:.4f}')
            m[2].metric("Burst temporal", f'{a["burst"]:.2f}')
            m[3].metric("Out-degree (SNA)", f'{int(a["out_deg"])}')
            m[4].metric("In-degree (SNA)", f'{int(a["in_deg"])}')

            st.markdown('<div class="kicker">Semua Twit Buzzer (' + str(len(a["tweets"])) + ')</div>', unsafe_allow_html=True)
            if a["tweets"]:
                for tw in a["tweets"]:
                    txt = html.escape(tw["text"]).replace("\n", "<br>")
                    st.markdown('<div class="blockq">“' + txt + '”</div>', unsafe_allow_html=True)
                    meta = 'prob ' + f'{tw["prob"]:.3f}'
                    if tw["in_reply_to"]:
                        meta += ' · membalas @' + html.escape(tw["in_reply_to"])
                    if tw["url"]:
                        meta += ' · <a href="' + tw["url"] + '" target="_blank">buka di X ↗</a>'
                    st.markdown('<div class="tw-meta">' + meta + '</div>', unsafe_allow_html=True)
            else:
                st.caption("Tidak ada teks twit buzzer tersimpan untuk akun ini.")

            st.markdown('<div class="kicker">Reply-out / Target Balasan (' + str(len(a["reply_out"])) + ')</div>', unsafe_allow_html=True)
            if a["reply_out"]:
                chips = ""
                for ro in a["reply_out"]:
                    lbl = '@' + html.escape(ro["target"])
                    if ro["weight"] > 1:
                        lbl += ' ×' + str(ro["weight"])
                    chips += '<a class="tag" href="https://x.com/' + ro["target"] + '" target="_blank">' + lbl + '</a>'
                st.markdown(chips, unsafe_allow_html=True)
            else:
                st.caption("Tidak ada reply-out tercatat untuk akun ini.")
                
    if total_matching == 0:
        st.info("Tidak ada akun cocok dengan pencarian.")
        
    if limit is not None and total_matching > limit:
        if st.button("Lebih lanjut", key="more_btn"):
            st.session_state.show_all_buzzers = True
            st.rerun()
    elif st.session_state.show_all_buzzers and not q:
        if st.button("Tampilkan lebih sedikit", key="less_btn"):
            st.session_state.show_all_buzzers = False
            st.rerun()

    kicker("Volume & Probabilitas Seluruh Akun")
    sc = pd.DataFrame(acc["scatter"])
    sc_sorted = sc.sort_values("n_tweets", ascending=False).copy()
    sc_sorted["Username"] = sc_sorted["username"].apply(lambda u: f"@{u}")
    sc_sorted["Jumlah Tweet"] = sc_sorted["n_tweets"]
    sc_sorted["Probabilitas Buzzer"] = sc_sorted["max_buzzer_prob"]
    sc_sorted["Klasifikasi"] = sc_sorted["buzzer_label"].apply(
        lambda l: "🚨 Buzzer" if l == "Buzzer" else "🟢 Non-Buzzer"
    )
    sc_table = sc_sorted[["Username", "Jumlah Tweet", "Probabilitas Buzzer", "Klasifikasi"]]
    
    total_rows = len(sc_table)
    
    # Pagination UI
    pg_col1, pg_col2, pg_col3, pg_col4 = st.columns([2, 1, 2, 1])
    
    with pg_col1:
        rows_per_page = st.selectbox(
            "Baris per halaman", 
            [10, 25, 50, 100], 
            index=1, 
            key="scatter_rows_per_page"
        )
    
    total_pages = max(1, (total_rows + rows_per_page - 1) // rows_per_page)
    
    # Initialize or sanitize page number in session state
    if "scatter_page_num" not in st.session_state:
        st.session_state["scatter_page_num"] = 1
    if st.session_state["scatter_page_num"] > total_pages:
        st.session_state["scatter_page_num"] = total_pages
    if st.session_state["scatter_page_num"] < 1:
        st.session_state["scatter_page_num"] = 1
        
    current_page = st.session_state["scatter_page_num"]
            
    with pg_col2:
        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
        prev_clicked = st.button("Prev", disabled=(current_page == 1), use_container_width=True)
        if prev_clicked:
            st.session_state["scatter_page_num"] = current_page - 1
            st.rerun()
            
    with pg_col3:
        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
        st.markdown(
            f'<div style="text-align: center; line-height: 2.2em; font-weight: 500; color: #433E33;">'
            f'Hal {current_page} dari {total_pages}'
            f'</div>', 
            unsafe_allow_html=True
        )
        
    with pg_col4:
        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
        next_clicked = st.button("Next", disabled=(current_page == total_pages), use_container_width=True)
        if next_clicked:
            st.session_state["scatter_page_num"] = current_page + 1
            st.rerun()
        
    start_idx = (st.session_state["scatter_page_num"] - 1) * rows_per_page
    end_idx = min(start_idx + rows_per_page, total_rows)
    
    page_data = sc_table.iloc[start_idx:end_idx]
    
    st.caption(f"Menampilkan {start_idx + 1} sampai {end_idx} dari {total_rows} akun")
    
    st.dataframe(
        page_data,
        column_config={
            "Username": st.column_config.TextColumn("Username", help="Username akun X (Twitter)"),
            "Jumlah Tweet": st.column_config.NumberColumn("Jumlah Tweet", help="Jumlah tweet terkait akun ini dalam dataset"),
            "Probabilitas Buzzer": st.column_config.ProgressColumn(
                "Probabilitas Buzzer Maksimal",
                help="Probabilitas maksimal akun ini diklasifikasikan sebagai buzzer",
                format="%.3f",
                min_value=0.0,
                max_value=1.0,
            ),
            "Klasifikasi": st.column_config.TextColumn("Klasifikasi", help="Status klasifikasi akun"),
        },
        use_container_width=True,
        hide_index=True
    )
    callout('<b>Catatan target.</b> Akun yang paling banyak <i>diserang</i> (mis. @RRDelusi, @kukuhya) justru berlabel Non-Buzzer — mereka sasaran, bukan pelaku. Struktur serangannya dibedah di tab <b>Jaringan Serangan</b>.')

# ============================================================
# TAB 3 — ANALISIS NARASI
# ============================================================
with tab3:
    lead('Apa <span class="hl">isi narasinya</span>? LDA mengurai tema dominan; analisis klaster & frasa memetakan seberapa terkoordinasi tiap kelompok pesan.')

    kicker("Topik LDA — Tema Dominan")
    lda = D["lda"]
    note('Topik laten diekstrak dari ' + str(lda["total"]) + ' tweet buzzer. Tiap kartu menampilkan interpretasi tema beserta trigram pembentuknya.')
    cols = st.columns(len(lda["topics"]))
    for c, t in zip(cols, lda["topics"]):
        tags = "".join('<span class="tag">' + html.escape(str(g)) + '</span>' for g in t["trigrams"][:5])
        tweets_html = ""
        if "tweets" in t and t["tweets"]:
            tweets_html += '<div style="margin-top:15px; border-top:1px solid rgba(38,33,25,0.13); padding-top:10px;">'
            tweets_html += '<div style="font-size:11px; font-weight:bold; color:#4D473B; margin-bottom:5px;">Top 3 Tweet:</div>'
            for tw in t["tweets"]:
                tweets_html += (
                    '<div style="font-size:11px; line-height:1.4; color:#211E17; margin-bottom:8px; padding:6px; background:#FBF9F3; border-radius:4px; border-left:2px solid ' + ACCENT + ';">'
                    '<b>@' + html.escape(tw["username"]) + '</b>: ' + html.escape(tw["text"]) + 
                    '</div>'
                )
            tweets_html += '</div>'
        c.markdown(
            '<div class="lda-card named"><div class="lda-id">TOPIK ' + str(t["topic_id"]) + ' · ' + str(t["count"]) + ' tweet</div>'
            '<div class="lda-name">' + html.escape(str(t["name"])) + '</div>'
            '<div class="lda-desc">' + html.escape(str(t["description"])) + '</div>'
            '<div style="margin-top:10px">' + tags + '</div>'
            + tweets_html + '</div>',
            unsafe_allow_html=True)
        
        if "more_tweets" in t and t["more_tweets"]:
            with c.expander("Sisa Tweet Lainnya"):
                for tw in t["more_tweets"]:
                    st.markdown(
                        f'<div style="font-size:11px; line-height:1.4; color:#211E17; margin-bottom:8px; padding:6px; background:#FBF9F3; border-radius:4px; border-left:2px solid {ACCENT};">'
                        f'<b>@{html.escape(tw["username"])}</b>: {html.escape(tw["text"])}'
                        f'</div>',
                        unsafe_allow_html=True
                    )

    kicker("Distribusi Tweet per Topik")
    ldf = pd.DataFrame([{"topik": f'T{t["topic_id"]} · {t["name"]}', "jumlah": t["count"]} for t in lda["topics"]])
    figl = go.Figure(go.Bar(
        x=ldf["jumlah"], 
        y=ldf["topik"], 
        orientation="h", 
        marker_color=SLATE, 
        text=ldf["jumlah"],
        textposition="outside",
        name="Jumlah Tweet"
    ))
    figl.update_layout(showlegend=False)
    figl = style(figl, 280)
    figl.update_layout(margin=dict(l=280, r=40, t=10, b=10))
    st.plotly_chart(figl, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        kicker("Trigram Paling Sering")
        tg = pd.DataFrame(D["trigrams"]["rows"]).sort_values("frequency")
        figg = go.Figure(go.Bar(
            x=tg["frequency"], 
            y=tg["trigram"], 
            orientation="h", 
            marker_color=ACCENT,
            text=tg["frequency"],
            textposition="outside",
            name="Frekuensi Trigram"
        ))
        figg.update_layout(showlegend=False)
        figg = style(figg, 380)
        figg.update_layout(margin=dict(l=140, r=40, t=10, b=10))
        st.plotly_chart(figg, use_container_width=True)
    with c2:
        kicker("Kata Kunci (TF-IDF)")
        tf = pd.DataFrame(D["tfidf"]["rows"]).sort_values("score")
        figtf = go.Figure(go.Bar(
            x=tf["score"], 
            y=tf["term"], 
            orientation="h", 
            marker_color=OCHRE,
            text=tf["score"].round(2),
            textposition="outside",
            name="TF-IDF Score"
        ))
        figtf.update_layout(showlegend=False)
        figtf = style(figtf, 380)
        figtf.update_layout(margin=dict(l=100, r=40, t=10, b=10))
        st.plotly_chart(figtf, use_container_width=True)
    note('Frasa <b>“self declare belum final”</b> mendominasi — narasi inti buzzer membingkai polemik rating IGRS sebagai sekadar “data awal yang belum final” untuk meredam kritik publik.')

    kicker("Panel Analisis Klaster (DBSCAN)")
    cl = pd.DataFrame(D["clusters"]["rows"])
    cl["Nama Tema"] = cl["cluster_id"].map(CLUSTER_NAMES).fillna("Klaster Lain")
    cl_show = cl.rename(columns={"cluster_id": "Klaster", "n_tweets": "Total Tweet",
                 "n_akun_unik": "Akun Unik", "n_buzzer_tweets": "Tweet Buzzer",
                 "pct_buzzer": "% Buzzer", "diversity_ratio": "Rasio Keragaman"})
    cols_order = ["Klaster", "Nama Tema", "Total Tweet", "Akun Unik", "Tweet Buzzer", "% Buzzer", "Rasio Keragaman"]
    note('Tiap klaster naratif diukur ukuran, proporsi tweet buzzer, dan keragaman akun. Klaster dengan <b>%buzzer tinggi</b> menandai koordinasi paling pekat.')
    st.dataframe(cl_show[cols_order], use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div style="font-family:\'Fraunces\',serif; font-size:18px; font-weight:500; margin-bottom:12px; color:#211E17;">Detail Tweet per Klaster Naratif</div>', unsafe_allow_html=True)
    for cl_data in D["clusters"]["rows"]:
        cid = cl_data["cluster_id"]
        cname = CLUSTER_NAMES.get(cid, f"Klaster {cid}")
        pct_buzz_val = cl_data['pct_buzzer'] * 100
        header = f"🔍 {cname} — {cl_data['n_tweets']} tweet ({pct_buzz_val:.1f}% Buzzer)"
        
        with st.expander(header):
            st.markdown(
                f'<div style="font-family:\'DM Mono\',monospace; font-size:11.5px; color:#4D473B; margin-bottom:10px;">'
                f'Total Tweet: <b>{cl_data["n_tweets"]}</b> | '
                f'Akun Unik: <b>{cl_data["n_akun_unik"]}</b> | '
                f'Tweet Buzzer: <b>{cl_data["n_buzzer_tweets"]}</b> ({pct_buzz_val:.1f}%) | '
                f'Rasio Keragaman: <b>{cl_data["diversity_ratio"]:.2f}</b>'
                f'</div>',
                unsafe_allow_html=True
            )
            
            # Show top 3 tweets
            if cl_data["tweets"]:
                st.markdown('<div style="font-size:12px; font-weight:600; color:#9B4A2C; margin-top:8px; margin-bottom:6px;">Top 3 Tweet:</div>', unsafe_allow_html=True)
                for tw in cl_data["tweets"]:
                    badge = "🚨 Buzzer" if tw.get("is_coordinated") == 1 else "🟢 Non-Buzzer"
                    badge_color = BUZZER if tw.get("is_coordinated") == 1 else ORGANIC
                    st.markdown(
                        f'<div style="font-size:12px; line-height:1.45; color:#211E17; margin-bottom:8px; padding:8px; background:#FBF9F3; border-radius:4px; border-left:3px solid {badge_color};">'
                        f'<span style="font-size:10px; font-weight:bold; color:{badge_color}; margin-right:8px; font-family:\'DM Mono\',monospace;">{badge}</span>'
                        f'<b>@{html.escape(tw["username"])}</b>: {html.escape(tw["text"])}'
                        f'</div>',
                        unsafe_allow_html=True
                    )
            
            # Show remaining tweets
            if cl_data["more_tweets"]:
                with st.expander("Tampilkan Sisa Tweet Lainnya"):
                    for tw in cl_data["more_tweets"]:
                        badge = "🚨 Buzzer" if tw.get("is_coordinated") == 1 else "🟢 Non-Buzzer"
                        badge_color = BUZZER if tw.get("is_coordinated") == 1 else ORGANIC
                        st.markdown(
                            f'<div style="font-size:11px; line-height:1.4; color:#211E17; margin-bottom:6px; padding:6px; background:#F5F1E6; border-radius:4px; border-left:2px solid {badge_color};">'
                            f'<span style="font-size:9px; font-weight:bold; color:{badge_color}; margin-right:8px; font-family:\'DM Mono\',monospace;">{badge}</span>'
                            f'<b>@{html.escape(tw["username"])}</b>: {html.escape(tw["text"])}'
                            f'</div>',
                            unsafe_allow_html=True
                        )

    kicker("Peta Klaster (PCA dari embedding SBERT)")
    cs = pd.DataFrame(D["cluster_scatter"]["rows"])
    cs = cs[cs["cluster_id"] >= 0].copy()
    cs["Klaster"] = cs["cluster_id"].map(CLUSTER_NAMES).fillna("Klaster Lain")
    cs = cs.sort_values("cluster_id")
    figcs = px.scatter(cs, x="pca_x", y="pca_y", color="Klaster",
                       hover_name="username", hover_data={"Klaster": False, "pca_x": False, "pca_y": False, "clean_text": True},
                       color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(style(figcs, 380, f'{D["cluster_scatter"]["n_clustered"]} tweet dalam {D["cluster_scatter"]["n_clusters"]} klaster naratif'), use_container_width=True)
    note('Tweet yang berdekatan punya makna serupa. Gumpalan padat = pesan nyaris identik yang disebar banyak akun — jejak visual koordinasi.')

# ============================================================
# TAB 4 — JARINGAN SERANGAN
# ============================================================
with tab4:
    net = D["network"]
    lead('Koordinasi paling jelas terlihat pada <span class="hl">struktur jaringan</span>: ' + str(net["unique_sources"]) + ' akun buzzer mengarahkan balasan ke segelintir akun-target yang sama.')

    kicker("Ringkasan Jaringan (Reply/Mention · Threshold 0.85)")
    stat_row([
        ("Total Node", f'{net["n_nodes"]:,}', "akun dalam jaringan"),
        ("Edge (balasan)", f'{net["n_edges"]}', "buzzer → target", "slate"),
        ("Sumber Buzzer", f'{net["unique_sources"]}', "akun penyerang aktif", "buzzer"),
        ("Target Unik", f'{net["unique_targets"]}', "akun sasaran"),
    ])

    kicker("Graf Koordinasi: Sumber Buzzer → Target")
    note("Grafik koordinasi interaktif menggunakan layout <b>ForceAtlas2</b> (seperti Gephi). Hanya menampilkan node yang terhubung dalam jaringan. Node merah = buzzer (🚨); node biru = non-buzzer (🟢).")
    edges = net["edges"]
    all_nodes_data = net.get("all_nodes", [])
    
    # Hanya node yang terhubung (muncul di edges)
    edge_sources = {e["source"] for e in edges}
    edge_targets = {e["target"] for e in edges}
    edge_connected = edge_sources | edge_targets
    connected_nodes = [nd for nd in all_nodes_data if nd["Label"] in edge_connected]
    
    # ── ForceAtlas2 Layout (scaling=150) ─────────────────────────────────
    import numpy as np
    import math
    
    node_labels = [nd["Label"] for nd in connected_nodes]
    n = len(node_labels)
    node_to_idx = {label: i for i, label in enumerate(node_labels)}
    
    rng = np.random.RandomState(42)
    positions = rng.randn(n, 2) * 10.0
    
    degree = np.ones(n, dtype=np.float64)
    edge_indices = []
    for e in edges:
        si = node_to_idx.get(e["source"])
        ti = node_to_idx.get(e["target"])
        if si is not None and ti is not None:
            degree[si] += 1
            degree[ti] += 1
            edge_indices.append((si, ti))
    
    fa2_iterations = 80
    fa2_gravity = 1.0
    fa2_scaling = 150.0
    fa2_edge_weight = 1.0
    
    for iteration in range(fa2_iterations):
        forces = np.zeros((n, 2), dtype=np.float64)
        
        # 1) REPULSION
        diff = positions[:, np.newaxis, :] - positions[np.newaxis, :, :]
        dist = np.sqrt((diff ** 2).sum(axis=2)) + 0.01
        deg_prod = degree[:, np.newaxis] * degree[np.newaxis, :]
        rep_mag = fa2_scaling * deg_prod / dist
        np.fill_diagonal(rep_mag, 0.0)
        forces += (rep_mag[:, :, np.newaxis] * diff / dist[:, :, np.newaxis]).sum(axis=1)
        
        # 2) ATTRACTION
        for si, ti in edge_indices:
            d = positions[si] - positions[ti]
            forces[si] -= fa2_edge_weight * d
            forces[ti] += fa2_edge_weight * d
        
        # 3) GRAVITY
        dist_center = np.sqrt((positions ** 2).sum(axis=1)) + 0.01
        grav_force = fa2_gravity * degree
        forces -= (grav_force[:, np.newaxis] * positions) / dist_center[:, np.newaxis]
        
        # 4) Apply
        force_mag = np.sqrt((forces ** 2).sum(axis=1)) + 0.01
        speed = 1.0 / (1.0 + np.sqrt(float(n)))
        displacement = np.minimum(speed * force_mag, 10.0)
        positions += (displacement / force_mag)[:, np.newaxis] * forces
    
    pos = {node_labels[i]: (float(positions[i, 0]), float(positions[i, 1])) for i in range(n)}
    
    # ── Edge lurus ───────────────────────────────────────────────────────
    ex, ey = [], []
    for e in edges:
        if e["source"] in pos and e["target"] in pos:
            x0, y0 = pos[e["source"]]
            x1, y1 = pos[e["target"]]
            ex += [x0, x1, None]
            ey += [y0, y1, None]

    fign = go.Figure()
    fign.add_scatter(
        x=ex, y=ey, mode="lines",
        line=dict(color="rgba(142, 68, 173, 0.3)", width=0.7),
        hoverinfo="none", showlegend=False
    )
    
    # ── Node: Buzzer (merah) & Target (biru) ─────────────────────────────
    buzzer_x, buzzer_y, buzzer_t = [], [], []
    target_x, target_y, target_t = [], [], []
    
    for nd in connected_nodes:
        label = nd["Label"]
        if label not in pos:
            continue
        x, y = pos[label]
        if nd["binary_label_gephi"] == "Buzzer":
            buzzer_x.append(x); buzzer_y.append(y)
            buzzer_t.append("🚨 @" + label)
        else:
            target_x.append(x); target_y.append(y)
            target_t.append("🟢 @" + label)
    
    if buzzer_x:
        fign.add_scatter(
            x=buzzer_x, y=buzzer_y, mode="markers",
            marker=dict(color="#D32F2F", size=12, line=dict(width=1, color="rgba(255,255,255,0.6)")),
            text=buzzer_t, hoverinfo="text", name="🚨 Buzzer"
        )
    if target_x:
        fign.add_scatter(
            x=target_x, y=target_y, mode="markers",
            marker=dict(color="#1F77B4", size=14, line=dict(width=1.5, color="rgba(255,255,255,0.8)")),
            text=target_t, hoverinfo="text", name="🟢 Non-Buzzer"
        )
    
    fign.update_xaxes(visible=False, showgrid=False, zeroline=False)
    fign.update_yaxes(visible=False, showgrid=False, zeroline=False)
    fign.update_layout(showlegend=True)
    
    # Initialize session state for chart key versioning to allow resetting selection
    if "sna_chart_version" not in st.session_state:
        st.session_state["sna_chart_version"] = 0

    # Capture click events on the SNA Plotly chart
    event_sna = st.plotly_chart(
        style(fign, 460, "SNA Graf Koordinasi"), 
        use_container_width=True, 
        on_select="rerun",
        key=f"sna_chart_v_{st.session_state['sna_chart_version']}"
    )
    
    # Initialize session state for selected SNA account
    if "selected_sna_account" not in st.session_state:
        st.session_state["selected_sna_account"] = None
        
    # Sync chart clicks to session state
    if event_sna and "selection" in event_sna and "points" in event_sna["selection"] and event_sna["selection"]["points"]:
        pt = event_sna["selection"]["points"][0]
        txt = pt.get("text") or pt.get("hovertext")
        if txt and "@" in txt:
            clicked_user = txt[txt.find("@")+1:]
            if st.session_state["selected_sna_account"] != clicked_user:
                st.session_state["selected_sna_account"] = clicked_user
                st.rerun()
                
    # Search/Dropdown selector for accounts in the SNA graph
    all_nodes_sorted = sorted(list(edge_sources | edge_targets))
    
    default_idx = 0
    if st.session_state["selected_sna_account"] in all_nodes_sorted:
        default_idx = all_nodes_sorted.index(st.session_state["selected_sna_account"]) + 1
        
    options = ["-- Pilih Akun (atau klik node pada graf di atas) --"] + [f"@{node}" for node in all_nodes_sorted]
    
    selected_option = st.selectbox(
        "Cari/Pilih Akun dari Graf SNA:",
        options=options,
        index=default_idx,
        key="sna_account_selectbox"
    )
    
    if selected_option != "-- Pilih Akun (atau klik node pada graf di atas) --":
        selected_user = selected_option[1:]
        if st.session_state["selected_sna_account"] != selected_user:
            st.session_state["selected_sna_account"] = selected_user
            st.rerun()
    else:
        # If selectbox is placeholder but we have a selection, clear it
        if st.session_state["selected_sna_account"] is not None:
            # Check if this rerun is because the user selected the placeholder
            if st.session_state.get("sna_account_selectbox") == "-- Pilih Akun (atau klik node pada graf di atas) --":
                st.session_state["selected_sna_account"] = None
                st.session_state["sna_chart_version"] += 1
                st.rerun()
                
    # Display the details panel if an account is selected
    if st.session_state["selected_sna_account"]:
        sel_user = st.session_state["selected_sna_account"]
        
        # Query account metadata from D["accounts"]["scatter"] or nodes_centrality.csv
        acc_meta = next((x for x in D["accounts"]["scatter"] if x["username"].lower() == sel_user.lower()), None)
        
        if acc_meta:
            is_buzzer = (acc_meta["buzzer_label"] == "Buzzer")
            prob = acc_meta["max_buzzer_prob"]
        else:
            try:
                import pandas as pd
                import os
                nodes_df = pd.read_csv(os.path.join(dl.DATA_DIR, "nodes_centrality.csv"))
                user_node = nodes_df[nodes_df["Label"].str.lower() == sel_user.lower()]
                if not user_node.empty:
                    is_buzzer = (user_node.iloc[0]["binary_label_gephi"] == "Buzzer")
                    prob = float(user_node.iloc[0]["max_buzzer_prob"])
                else:
                    is_buzzer = False
                    prob = 0.0
            except Exception:
                is_buzzer = False
                prob = 0.0
                
        label_text = "🚨 Buzzer" if is_buzzer else "🟢 Non-Buzzer"
        badge_bg = BUZZER if is_buzzer else ORGANIC
        
        # Load tweets for the selected user
        tweets_df = load_tweets_scored()
        user_tweets = tweets_df[tweets_df["username"].str.lower() == sel_user.lower()].copy()
        
        st.markdown(
            f'<div style="background-color: {SURFACE}; border: 1px solid rgba(38,33,25,0.13); border-left: 4px solid {badge_bg}; border-radius: 6px; padding: 20px; margin-top: 15px; margin-bottom: 25px;">'
            f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">'
            f'<h3 style="font-family: \'Fraunces\', serif; font-size: 20px; font-weight: 500; color: {TEXT}; margin: 0;">'
            f'🔍 Detail Akun: @{sel_user}'
            f'</h3>'
            f'</div>',
            unsafe_allow_html=True
        )
        
        col_m1, col_m2, col_m3, col_m4 = st.columns([3, 2.5, 3, 2])
        
        # Nama Akun with Profil X link
        col_m1.markdown(
            f'<div style="margin-top: 5px;">'
            f'<span style="font-size: 11px; color: {MUTED}; font-family: \'DM Mono\', monospace;">NAMA AKUN</span><br>'
            f'<a href="https://x.com/{sel_user}" target="_blank" style="font-family: \'Fraunces\', serif; font-size: 18px; font-weight: 500; color: {ACCENT}; text-decoration: none;">'
            f'@{sel_user} ↗'
            f'</a>'
            f'</div>',
            unsafe_allow_html=True
        )
        
        col_m2.metric("Probabilitas Buzzer (Maks)", f"{prob:.4f}")
        
        col_m3.markdown(
            f'<div style="margin-top: 25px;"><span class="tag" style="background-color: {badge_bg}; color: white; border: none; font-weight: 600; padding: 6px 12px; font-size: 13px;">'
            f'{label_text}'
            f'</span></div>',
            unsafe_allow_html=True
        )
        
        with col_m4:
            st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
            if st.button("Tutup Panel ✕", key="close_sna_panel", use_container_width=True):
                st.session_state["selected_sna_account"] = None
                st.session_state["sna_chart_version"] += 1
                st.rerun()
                
        st.markdown('<div class="kicker" style="margin-top: 20px;">Daftar Tweet dalam Dataset</div>', unsafe_allow_html=True)
        if not user_tweets.empty:
            user_tweets = user_tweets.sort_values("created_at", ascending=False)
            display_df = user_tweets.copy()
            display_df["Waktu"] = pd.to_datetime(display_df["created_at"]).dt.strftime("%d %b %Y %H:%M:%S")
            display_df["Isi Tweet"] = display_df["full_text"].fillna(display_df["clean_text"])
            display_df["Probabilitas Tweet"] = display_df["buzzer_prob"].round(4)
            display_df["Link X"] = display_df["tweet_url"].apply(lambda u: str(u) if isinstance(u, str) and u.startswith("http") else f"https://x.com/{sel_user}")
            
            display_df = display_df[["Waktu", "Isi Tweet", "Probabilitas Tweet", "Link X"]]
            
            st.dataframe(
                display_df,
                column_config={
                    "Waktu": st.column_config.TextColumn("Waktu", width="medium"),
                    "Isi Tweet": st.column_config.TextColumn("Isi Tweet", width="large"),
                    "Probabilitas Tweet": st.column_config.NumberColumn("Probabilitas Tweet", format="%.4f"),
                    "Link X": st.column_config.LinkColumn("Link X", display_text="Buka Tweet ↗")
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("Tidak ada tweet terekam untuk akun ini dalam dataset.")
            
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

    kicker("Akun Target Serangan Narasi")
    note("Akun non-buzzer yang paling banyak menerima balasan dari kluster buzzer — kemungkinan kritikus, media, atau lawan narasi.")
    tg = pd.DataFrame(net["targets"])
    show = tg.rename(columns={"Target": "Akun Target", "incoming_from_buzzer": "Diserang (dari buzzer)",
                              "total_weight": "Bobot", "binary_label_gephi": "Tipe"})
    cols_show = [c for c in ["Akun Target", "Diserang (dari buzzer)", "Bobot", "Tipe"] if c in show.columns]
    st.dataframe(show[cols_show], use_container_width=True, hide_index=True)

    kicker("Akun Buzzer Paling Sentral (PageRank)")
    cen = pd.DataFrame(net["central"]).rename(columns={"Label": "Akun", "pagerank": "PageRank",
                      "betweenness_centrality": "Betweenness", "out_degree": "Out-degree",
                      "max_buzzer_prob": "Prob Buzzer"})
    st.dataframe(cen, use_container_width=True, hide_index=True)

    kicker("Pola Temporal Aktivitas")
    tp = D["temporal"]
    tser = pd.DataFrame(tp["series"])
    tser["hour"] = pd.to_datetime(tser["hour"])
    if tser["hour"].dt.tz is not None:
        tser["hour"] = tser["hour"].dt.tz_convert("Asia/Jakarta").dt.tz_localize(None)
    
    figtm = go.Figure()
    # Blue bars for Jumlah tweet/jam
    figtm.add_trace(go.Bar(
        x=tser["hour"],
        y=tser["tweets"],
        name="Jumlah tweet/jam",
        marker_color=SLATE
    ))
    # Red line + dots for Akun unik/jam
    figtm.add_trace(go.Scatter(
        x=tser["hour"],
        y=tser["users"],
        name="Akun unik/jam",
        mode="lines+markers",
        line=dict(color="red", width=1.5),
        marker=dict(size=4, color="red")
    ))
    
    peak_h = pd.to_datetime(tp["peak_hour"])
    if peak_h.tz is not None:
        peak_h = peak_h.tz_convert("Asia/Jakarta").tz_localize(None)
    
    # We will position the peak annotation neatly above the unique users line
    figtm.add_annotation(x=peak_h, y=tp["peak_users"], text='Puncak: ' + str(tp["peak_users"]) + ' akun', showarrow=False, yshift=12, font=dict(color=BUZZER))
    
    figtm = style(figtm, 340, "Timeline Aktivitas per Jam")
    figtm.update_layout(
        showlegend=True,
        xaxis_title="Waktu (WIB)",
        yaxis_title="Jumlah",
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            bordercolor="rgba(38,33,25,0.2)",
            borderwidth=1,
            bgcolor="rgba(251,249,243,0.8)", # Match SURFACE color
        ),
        xaxis=dict(
            tickformat="%d/%m %H:%M",
            tickangle=-30
        )
    )
    
    # Capture click events on the Plotly chart
    event = st.plotly_chart(figtm, use_container_width=True, on_select="rerun")
    
    peak_formatted = pd.to_datetime(tp["peak_hour"]).strftime("%d/%m/%Y %H:%M")
    note('Aktivitas melonjak hingga <b>' + str(tp["peak_users"]) + ' akun aktif dalam satu jam</b> (puncak ' + peak_formatted + ' WIB). Lonjakan serempak dalam jendela sempit adalah indikator klasik aktivasi terkoordinasi.')

    selected_time_str = None
    if event and "selection" in event and "points" in event["selection"] and event["selection"]["points"]:
        selected_time_str = event["selection"]["points"][0].get("x")
        
    st.markdown('<div style="height: 1px; background-color: rgba(38,33,25,0.13); margin: 25px 0 20px 0;"></div>', unsafe_allow_html=True)
    
    if selected_time_str:
        selected_time = pd.to_datetime(selected_time_str)
        if selected_time.tz is None:
            selected_time = selected_time.tz_localize("Asia/Jakarta").tz_convert("UTC")
        else:
            selected_time = selected_time.tz_convert("UTC")
            
        tw_df = load_tweets_scored()
        subset = tw_df[tw_df["hour_bin"] == selected_time]
        
        st.markdown(
            f'<div style="font-family:\'Fraunces\',serif; font-size:17px; font-weight:500; margin-bottom:12px; color:#211E17;">'
            f'Detail Tweet pada Jam: {selected_time.tz_convert("Asia/Jakarta").strftime("%d %b %Y, %H:%M")} WIB'
            f'</div>',
            unsafe_allow_html=True
        )
        
        tot = len(subset)
        buzz = int((subset["is_coordinated"] == 1).sum())
        org = tot - buzz
        
        m = st.columns(3)
        m[0].metric("Total Tweet", f"{tot:,}")
        m[1].metric("Tweet Buzzer", f"{buzz:,}", f"{buzz/tot*100:.1f}%" if tot else "0%")
        m[2].metric("Tweet Non-Buzzer", f"{org:,}", f"{org/tot*100:.1f}%" if tot else "0%")
        
        if tot > 0:
            sub_display = subset.copy()
            sub_display["Waktu"] = pd.to_datetime(sub_display["created_at"]).dt.strftime("%H:%M:%S")
            sub_display["Akun"] = sub_display["username"].apply(lambda u: f"@{u}")
            sub_display["Profil X"] = sub_display["username"].apply(lambda u: f"https://x.com/{u}")
            sub_display["Kategori"] = sub_display["is_coordinated"].apply(lambda x: "🚨 Buzzer" if x == 1 else "🟢 Non-Buzzer")
            
            sub_display = sub_display.rename(columns={
                "clean_text": "Isi Tweet",
                "buzzer_prob": "Probabilitas"
            })
            sub_display = sub_display[["Waktu", "Akun", "Isi Tweet", "Kategori", "Probabilitas", "Profil X"]]
            sub_display = sub_display.sort_values("Waktu")
            
            st.dataframe(
                sub_display,
                column_config={
                    "Waktu": st.column_config.TextColumn("Waktu", width="small"),
                    "Akun": st.column_config.TextColumn("Akun", width="medium"),
                    "Isi Tweet": st.column_config.TextColumn("Isi Tweet", width="large"),
                    "Kategori": st.column_config.TextColumn("Kategori", width="small"),
                    "Probabilitas": st.column_config.NumberColumn("Probabilitas", format="%.3f", width="small"),
                    "Profil X": st.column_config.LinkColumn("Profil X", display_text="Buka Profil ↗", width="small")
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("Tidak ada tweet terekam untuk jam ini.")
    else:
        st.markdown(
            f'<div style="padding:15px; background-color:#F5F1E6; border-radius:6px; border-left:4px solid {ACCENT}; font-size:13.5px; color:#4D473B;">'
            f'💡 <b>Tips Interaksi:</b> Klik salah satu titik marker bulat pada grafik <b>Pola Aktivitas Temporal</b> di atas untuk memfilter dan melihat isi tweet terperinci yang diposting pada jam tersebut.'
            f'</div>',
            unsafe_allow_html=True
        )

st.markdown(
    '<footer class="cred">Metodologi: SBERT (paraphrase-multilingual-MiniLM-L12-v2) → DBSCAN → fitur koordinasi → XGBoost (8 fitur, threshold 0.85) → SNA. '
    'Seluruh angka dihitung langsung dari folder <code>data/</code>. Klasifikasi bersifat probabilistik untuk analisis investigatif, bukan vonis hukum.</footer>',
    unsafe_allow_html=True)
