import streamlit as st
import pandas as pd
import numpy as np
import math
import plotly.graph_objects as go
import plotly.express as px
from itertools import product

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WC26 AI Command Center",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Dark background */
.stApp {
    background: radial-gradient(circle at top right, #14345d 0%, #07111f 45%);
    color: #eef4ff;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(8,17,31,0.97) !important;
    border-right: 1px solid rgba(255,255,255,0.08);
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stSelectbox label { color: #eef4ff !important; }

/* Metric cards */
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 16px 20px;
}
[data-testid="stMetricValue"] { color: #2dd4ff !important; font-weight: 800 !important; }
[data-testid="stMetricLabel"] { color: #8ea3c0 !important; }

/* Cards */
.wc-card {
    background: rgba(15,27,45,0.9);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 24px;
    padding: 24px;
    margin-bottom: 20px;
}

/* Score matrix cells */
.score-grid {
    display: grid;
    grid-template-columns: repeat(8, 1fr);
    gap: 5px;
    margin-top: 12px;
}
.score-cell {
    aspect-ratio: 1;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    font-weight: 600;
    text-align: center;
    padding: 4px;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(15,27,45,0.6);
    border-radius: 14px;
    gap: 4px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    color: #8ea3c0;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #1a3557, #0d2039) !important;
    color: #2dd4ff !important;
    border: 1px solid rgba(45,212,255,0.3) !important;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #22d3ee, #3b82f6);
    color: white;
    font-weight: 800;
    border: none;
    border-radius: 14px;
    padding: 12px 24px;
    width: 100%;
    font-size: 15px;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.85; }

/* Selectbox & slider */
.stSelectbox > div > div,
.stSlider > div { color: #eef4ff; }

/* Status dot */
.status-dot { display:inline-block; width:10px; height:10px;
    border-radius:50%; background:#38ff90; margin-right:6px; }

/* Team display */
.team-block { text-align:center; padding: 16px; }
.flag-big { font-size: 64px; line-height:1.1; }
.team-name { font-size: 20px; font-weight: 800; color: #eef4ff; margin-top: 6px; }
.lambda-val { font-size: 15px; color: #2dd4ff; font-weight: 700; margin-top: 2px; }

/* Section headers */
.section-title {
    font-size: 22px; font-weight: 800; color: #eef4ff;
    margin-bottom: 12px; border-bottom: 1px solid rgba(45,212,255,0.2);
    padding-bottom: 8px;
}

/* Probability bars custom */
.prob-bar-wrap { margin-bottom: 12px; }
.prob-label { display: flex; justify-content: space-between;
    font-size: 13px; color: #8ea3c0; margin-bottom: 4px; }
.prob-bar-bg { background: #1c2c43; border-radius: 50px; height: 10px; overflow:hidden; }
.prob-bar-fill { height:100%;
    background: linear-gradient(90deg, #22d3ee, #3b82f6); border-radius:50px; }

/* Winner badge */
.winner-badge {
    background: linear-gradient(90deg,#22d3ee22,#3b82f622);
    border: 1px solid #2dd4ff55;
    border-radius: 14px; padding: 12px 20px; text-align:center;
    font-size: 18px; font-weight: 800; color: #2dd4ff; margin-top: 14px;
}

/* Standings table */
.standings-row {
    display: flex; align-items: center; padding: 10px 14px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    font-size: 14px;
}
.standings-rank { width: 28px; color: #8ea3c0; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# ── Flags dictionary ────────────────────────────────────────────────────────────
FLAGS = {
    "Alemania": "🇩🇪", "Arabia Saudita": "🇸🇦", "Argelia": "🇩🇿",
    "Argentina": "🇦🇷", "Australia": "🇦🇺", "Austria": "🇦🇹",
    "Bosnia y Herzegovina": "🇧🇦", "Brasil": "🇧🇷", "Bélgica": "🇧🇪",
    "Cabo Verde": "🇨🇻", "Canadá": "🇨🇦", "Colombia": "🇨🇴",
    "Corea del Sur": "🇰🇷", "Costa de Marfil": "🇨🇮", "Croacia": "🇭🇷",
    "Curazao": "🇨🇼", "Ecuador": "🇪🇨", "Egipto": "🇪🇬",
    "Escocia": "🏴󠁧󠁢󠁳󠁣󠁴󠁿", "España": "🇪🇸", "Estados Unidos": "🇺🇸",
    "Francia": "🇫🇷", "Ghana": "🇬🇭", "Haití": "🇭🇹",
    "Inglaterra": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Irak": "🇮🇶", "Irán": "🇮🇷",
    "Japón": "🇯🇵", "Jordania": "🇯🇴", "Marruecos": "🇲🇦",
    "México": "🇲🇽", "Noruega": "🇳🇴", "Nueva Zelanda": "🇳🇿",
    "Panamá": "🇵🇦", "Paraguay": "🇵🇾", "Países Bajos": "🇳🇱",
    "Portugal": "🇵🇹", "Qatar": "🇶🇦", "RD Congo": "🇨🇩",
    "República Checa": "🇨🇿", "Senegal": "🇸🇳", "Sudáfrica": "🇿🇦",
    "Suecia": "🇸🇪", "Suiza": "🇨🇭", "Turquía": "🇹🇷",
    "Túnez": "🇹🇳", "Uruguay": "🇺🇾", "Uzbekistán": "🇺🇿",
}

# ── Model constants ─────────────────────────────────────────────────────────────
ALPHA, BETA, GAMMA, K = 0.6, 0.3, 0.1, 1.5
GOL_MAX = 7

# ── Data loading ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("predicciones_fase_grupos.csv")
    return df

@st.cache_data
def load_raw():
    df = pd.read_csv("Fase_grupos.txt")
    df["Equipo_A"] = df["Partido"].apply(lambda x: x.split("_vs_")[0])
    df["Equipo_B"] = df["Partido"].apply(lambda x: x.split("_vs_")[1])
    return df

# ── Poisson helpers ─────────────────────────────────────────────────────────────
def poisson_prob(lambd, n):
    return (math.exp(-lambd) * (lambd ** n)) / math.factorial(n)

def build_matrix(lam_a, lam_b, gol_max=GOL_MAX):
    goles = list(range(gol_max + 1))
    pa = np.array([poisson_prob(lam_a, g) for g in goles])
    pb = np.array([poisson_prob(lam_b, g) for g in goles])
    return np.outer(pa, pb)

def calc_lambdas(ov_a, dv_a, mv_a, fa_a, ov_b, dv_b, mv_b, fa_b, mv_ref):
    lam_a = ((ov_a/100)**ALPHA * (100/dv_b)**BETA * (mv_a/mv_ref)**GAMMA * fa_a) * K
    lam_b = ((ov_b/100)**ALPHA * (100/dv_a)**BETA * (mv_b/mv_ref)**GAMMA * fa_b) * K
    return lam_a, lam_b

def analyze_match(lam_a, lam_b, eq_a, eq_b):
    mat = build_matrix(lam_a, lam_b)
    P_A = float(np.sum(np.tril(mat, k=-1)))
    P_E = float(np.sum(np.diag(mat)))
    P_B = float(np.sum(np.triu(mat, k=1)))
    scores = []
    for i in range(GOL_MAX + 1):
        for j in range(GOL_MAX + 1):
            scores.append((f"{i}-{j}", float(mat[i, j])))
    scores.sort(key=lambda x: x[1], reverse=True)
    mx = max(P_A, P_E, P_B)
    winner = eq_a if mx == P_A else (eq_b if mx == P_B else "Empate")
    return P_A, P_E, P_B, winner, scores, mat

# ── Score matrix chart ──────────────────────────────────────────────────────────
def score_matrix_chart(mat, eq_a, eq_b):
    n = GOL_MAX + 1
    z = mat[:n, :n]
    text = [[f"{i}-{j}<br>{z[i,j]*100:.1f}%" for j in range(n)] for i in range(n)]
    fig = go.Figure(go.Heatmap(
        z=z,
        text=text,
        texttemplate="%{text}",
        colorscale=[[0,"#0f1b2d"],[0.4,"#1a3557"],[0.7,"#22d3ee"],[1,"#2dd4ff"]],
        showscale=False,
        hovertemplate="Marcador %{text}<extra></extra>",
    ))
    fig.update_layout(
        xaxis=dict(title=f"Goles {eq_b}", tickvals=list(range(n)),
                   color="#8ea3c0", gridcolor="rgba(255,255,255,0.05)"),
        yaxis=dict(title=f"Goles {eq_a}", tickvals=list(range(n)),
                   color="#8ea3c0", gridcolor="rgba(255,255,255,0.05)"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#eef4ff", size=11),
        margin=dict(l=50, r=10, t=10, b=50),
        height=370,
    )
    return fig

# ── Probability donut ───────────────────────────────────────────────────────────
def prob_donut(pa, pe, pb, eq_a, eq_b):
    labels = [eq_a, "Empate", eq_b]
    vals   = [pa*100, pe*100, pb*100]
    colors = ["#22d3ee", "#8ea3c0", "#3b82f6"]
    fig = go.Figure(go.Pie(
        labels=labels, values=vals,
        hole=0.6,
        marker_colors=colors,
        textinfo="label+percent",
        textfont_color="#eef4ff",
        hovertemplate="%{label}: %{value:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#eef4ff"),
        showlegend=False,
        margin=dict(l=10, r=10, t=10, b=10),
        height=280,
    )
    return fig

# ── Lambda radar ─────────────────────────────────────────────────────────────────
def radar_chart(row_a, row_b, eq_a, eq_b):
    cats = ["Ofensivo (OV)", "Defensivo (DV)", "Valor Mercado", "Aclimatación"]
    df_raw = load_raw()
    mv_ref = pd.concat([df_raw["MV_A"], df_raw["MV_B"]]).mean()

    vals_a = [row_a["OV_A"], row_a["DV_A"],
              min(row_a["MV_A"] / mv_ref * 50, 99),
              row_a["FA_A"] * 100]
    vals_b = [row_a["OV_B"], row_a["DV_B"],
              min(row_a["MV_B"] / mv_ref * 50, 99),
              row_a["FA_B"] * 100]

    fig = go.Figure()
    for vals, name, color in [(vals_a, eq_a, "#22d3ee"), (vals_b, eq_b, "#3b82f6")]:
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=cats + [cats[0]],
            fill="toself",
            name=name,
            line_color=color,
            fillcolor=color.replace("ee", "33").replace("f6", "33"),
        ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, 110],
                            color="#8ea3c0", gridcolor="rgba(255,255,255,0.1)"),
            angularaxis=dict(color="#8ea3c0", gridcolor="rgba(255,255,255,0.1)"),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#eef4ff"),
        legend=dict(font_color="#eef4ff", bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=40, r=40, t=20, b=20),
        height=300,
    )
    return fig

# ── Top teams by win probability ────────────────────────────────────────────────
@st.cache_data
def top_winners(df):
    wins = df["Ganador_Pred"].value_counts().reset_index()
    wins.columns = ["Equipo", "Victorias_Pred"]
    # avg win prob when they are team A
    pa = df.groupby("Equipo_A")["P_Victoria_A"].mean().reset_index()
    pa.columns = ["Equipo", "Avg_P_Win_A"]
    pb = df.groupby("Equipo_B")["P_Victoria_B"].mean().reset_index()
    pb.columns = ["Equipo", "Avg_P_Win_B"]
    merged = wins.merge(pa, on="Equipo", how="left").merge(pb, on="Equipo", how="left")
    merged["Avg_Win_Prob"] = merged[["Avg_P_Win_A","Avg_P_Win_B"]].mean(axis=1)
    merged = merged.sort_values("Victorias_Pred", ascending=False).head(10)
    return merged

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🏆 WC26 **AI**")
    st.markdown("<span style='color:#8ea3c0;font-size:13px'>World Cup Command Center</span>",
                unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio(
        "Navegación",
        ["🏆 Dashboard", "⚽ Predictor de Partido", "📊 Análisis de Equipos",
         "📋 Tabla de Predicciones"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("### ⚙️ Parámetros del Modelo")
    alpha_s = st.slider("α — Peso OV (Ofensivo)", 0.1, 1.0, 0.6, 0.05)
    beta_s  = st.slider("β — Peso DV (Defensivo)", 0.1, 1.0, 0.3, 0.05)
    gamma_s = st.slider("γ — Peso MV (Mercado)",   0.0, 0.5, 0.1, 0.05)
    k_s     = st.slider("k — Escala de goles",      0.5, 3.0, 1.5, 0.1)

    st.markdown("---")
    st.markdown("""
<div style='font-size:12px;color:#8ea3c0'>
<span class='status-dot'></span>Poisson Engine · ACTIVO<br>
<span class='status-dot'></span>Monte Carlo · ACTIVO<br>
<span class='status-dot'></span>Live Predictions · ACTIVO
</div>""", unsafe_allow_html=True)

# ── Load data ──────────────────────────────────────────────────────────────────
df     = load_data()
df_raw = load_raw()
MV_REF = pd.concat([df_raw["MV_A"], df_raw["MV_B"]]).mean()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🏆 Dashboard":

    st.markdown("# 🏆 World Cup 2026 · AI Command Center")
    st.markdown("<span style='color:#8ea3c0'>Poisson Simulations · xG Models · Monte Carlo Engine</span>",
                unsafe_allow_html=True)
    st.markdown("")

    # KPI row
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("⚽ PARTIDOS", "72")
    c2.metric("🌍 EQUIPOS", "48")
    c3.metric("🏟️ SEDES", str(df["Sede"].nunique()))
    c4.metric("📈 λ MEDIA LOCAL", f"{df['lambda_A'].mean():.2f}")
    c5.metric("📉 λ MEDIA VISITA", f"{df['lambda_B'].mean():.2f}")

    st.markdown("---")

    # Top teams + featured match
    col_left, col_right = st.columns([1.4, 1])

    with col_left:
        st.markdown('<div class="section-title">🥇 Favoritos del Torneo (victorias predichas)</div>',
                    unsafe_allow_html=True)
        top = top_winners(df)
        fig_top = go.Figure(go.Bar(
            x=top["Victorias_Pred"],
            y=[f"{FLAGS.get(t,'⚽')} {t}" for t in top["Equipo"]],
            orientation="h",
            marker=dict(
                color=top["Victorias_Pred"],
                colorscale=[[0,"#1a3557"],[1,"#22d3ee"]],
                showscale=False,
            ),
            text=top["Victorias_Pred"],
            textposition="outside",
            textfont_color="#eef4ff",
        ))
        fig_top.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#eef4ff"),
            xaxis=dict(color="#8ea3c0", gridcolor="rgba(255,255,255,0.07)"),
            yaxis=dict(color="#eef4ff", autorange="reversed"),
            margin=dict(l=10, r=40, t=10, b=10),
            height=340,
        )
        st.plotly_chart(fig_top, use_container_width=True)

    with col_right:
        st.markdown('<div class="section-title">📍 Partido Destacado</div>',
                    unsafe_allow_html=True)
        feat = df.iloc[0]
        ea, eb = feat["Equipo_A"], feat["Equipo_B"]
        fa, fb = FLAGS.get(ea, "⚽"), FLAGS.get(eb, "⚽")
        st.markdown(f"""
        <div style='display:flex;justify-content:space-around;align-items:center;padding:20px 0'>
          <div class='team-block'>
            <div class='flag-big'>{fa}</div>
            <div class='team-name'>{ea}</div>
            <div class='lambda-val'>λ = {feat['lambda_A']:.2f}</div>
          </div>
          <div style='font-size:30px;color:#8ea3c0;font-weight:800'>VS</div>
          <div class='team-block'>
            <div class='flag-big'>{fb}</div>
            <div class='team-name'>{eb}</div>
            <div class='lambda-val'>λ = {feat['lambda_B']:.2f}</div>
          </div>
        </div>
        <div class='winner-badge'>🏆 Ganador Predicho: {FLAGS.get(feat['Ganador_Pred'],'')} {feat['Ganador_Pred']}</div>
        <div style='margin-top:16px'>
          <div class='prob-bar-wrap'>
            <div class='prob-label'><span>{ea}</span><span>{feat['P_Victoria_A']*100:.1f}%</span></div>
            <div class='prob-bar-bg'><div class='prob-bar-fill' style='width:{feat["P_Victoria_A"]*100:.1f}%'></div></div>
          </div>
          <div class='prob-bar-wrap'>
            <div class='prob-label'><span>Empate</span><span>{feat['P_Empate']*100:.1f}%</span></div>
            <div class='prob-bar-bg'><div class='prob-bar-fill' style='width:{feat["P_Empate"]*100:.1f}%'></div></div>
          </div>
          <div class='prob-bar-wrap'>
            <div class='prob-label'><span>{eb}</span><span>{feat['P_Victoria_B']*100:.1f}%</span></div>
            <div class='prob-bar-bg'><div class='prob-bar-fill' style='width:{feat["P_Victoria_B"]*100:.1f}%'></div></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # Distribution of result types
    st.markdown("---")
    st.markdown('<div class="section-title">📊 Distribución de Resultados Predichos</div>',
                unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        res_counts = {
            "Victoria Local": (df["Ganador_Pred"] == df["Equipo_A"]).sum(),
            "Empate": (df["Ganador_Pred"] == "Empate").sum(),
            "Victoria Visitante": (df["Ganador_Pred"] == df["Equipo_B"]).sum(),
        }
        fig_pie = go.Figure(go.Pie(
            labels=list(res_counts.keys()),
            values=list(res_counts.values()),
            marker_colors=["#22d3ee", "#8ea3c0", "#3b82f6"],
            hole=0.55,
            textinfo="label+value",
            textfont_color="#eef4ff",
        ))
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#eef4ff"),
            showlegend=False,
            margin=dict(l=10, r=10, t=20, b=10),
            height=280,
            title=dict(text="Tipos de resultado", font_color="#eef4ff"),
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        top_scores = df["Marcador_1"].value_counts().head(6).reset_index()
        top_scores.columns = ["Marcador", "Frecuencia"]
        fig_sc = go.Figure(go.Bar(
            x=top_scores["Marcador"],
            y=top_scores["Frecuencia"],
            marker_color="#22d3ee",
            text=top_scores["Frecuencia"],
            textposition="outside",
            textfont_color="#eef4ff",
        ))
        fig_sc.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#eef4ff"),
            xaxis=dict(color="#8ea3c0"),
            yaxis=dict(color="#8ea3c0", gridcolor="rgba(255,255,255,0.07)"),
            margin=dict(l=10, r=10, t=30, b=10),
            height=280,
            title=dict(text="Marcadores más frecuentes", font_color="#eef4ff"),
        )
        st.plotly_chart(fig_sc, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — MATCH PREDICTOR
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "⚽ Predictor de Partido":

    st.markdown("# ⚽ Predictor de Partido")
    st.markdown("<span style='color:#8ea3c0'>Selecciona un partido del fixture o configura uno personalizado</span>",
                unsafe_allow_html=True)
    st.markdown("")

    mode = st.radio("Modo", ["📋 Fixture oficial", "🎛️ Partido personalizado"], horizontal=True)

    if mode == "📋 Fixture oficial":
        partido_sel = st.selectbox(
            "Selecciona el partido",
            df["Partido"].tolist(),
            format_func=lambda x: x.replace("_vs_", " vs "),
        )
        row = df[df["Partido"] == partido_sel].iloc[0]
        eq_a, eq_b = row["Equipo_A"], row["Equipo_B"]

        # Recalculate with sidebar params
        lam_a, lam_b = calc_lambdas(
            row["OV_A"], row["DV_A"], row["MV_A"], row["FA_A"],
            row["OV_B"], row["DV_B"], row["MV_B"], row["FA_B"],
            MV_REF,
        )
        # Override with sidebar params
        lam_a = ((row["OV_A"]/100)**alpha_s * (100/row["DV_B"])**beta_s *
                  (row["MV_A"]/MV_REF)**gamma_s * row["FA_A"]) * k_s
        lam_b = ((row["OV_B"]/100)**alpha_s * (100/row["DV_A"])**beta_s *
                  (row["MV_B"]/MV_REF)**gamma_s * row["FA_B"]) * k_s

        P_A, P_E, P_B, winner, scores, mat = analyze_match(lam_a, lam_b, eq_a, eq_b)
        row_dict = row.to_dict()

    else:  # Custom match
        all_teams = sorted(FLAGS.keys())
        col1, col2 = st.columns(2)
        with col1:
            eq_a = st.selectbox("🏠 Equipo Local (A)", all_teams, index=all_teams.index("México"))
            ov_a = st.slider("OV — Valor Ofensivo A", 30, 99, 80)
            dv_a = st.slider("DV — Valor Defensivo A", 30, 99, 75)
            mv_a = st.number_input("MV — Valor Mercado A (M€)", 5.0, 2000.0, 300.0, step=10.0)
            fa_a = st.slider("FA — Factor Aclimatación A", 0.7, 1.0, 1.0, 0.05)
        with col2:
            eq_b = st.selectbox("✈️ Equipo Visitante (B)", all_teams, index=all_teams.index("Argentina"))
            ov_b = st.slider("OV — Valor Ofensivo B", 30, 99, 90)
            dv_b = st.slider("DV — Valor Defensivo B", 30, 99, 85)
            mv_b = st.number_input("MV — Valor Mercado B (M€)", 5.0, 2000.0, 900.0, step=10.0)
            fa_b = st.slider("FA — Factor Aclimatación B", 0.7, 1.0, 0.95, 0.05)

        lam_a = ((ov_a/100)**alpha_s * (100/dv_b)**beta_s * (mv_a/MV_REF)**gamma_s * fa_a) * k_s
        lam_b = ((ov_b/100)**alpha_s * (100/dv_a)**beta_s * (mv_b/MV_REF)**gamma_s * fa_b) * k_s
        P_A, P_E, P_B, winner, scores, mat = analyze_match(lam_a, lam_b, eq_a, eq_b)
        row_dict = {
            "OV_A": ov_a, "DV_A": dv_a, "MV_A": mv_a, "FA_A": fa_a,
            "OV_B": ov_b, "DV_B": dv_b, "MV_B": mv_b, "FA_B": fa_b,
        }

    # ── Result display ─────────────────────────────────────────────────────────
    st.markdown("---")
    fl_a, fl_b = FLAGS.get(eq_a, "⚽"), FLAGS.get(eq_b, "⚽")

    top_c1, top_c2, top_c3 = st.columns([1.2, 0.6, 1.2])
    with top_c1:
        st.markdown(f"""
        <div class='team-block' style='border:1px solid rgba(45,212,255,0.2);border-radius:20px;padding:24px'>
          <div class='flag-big'>{fl_a}</div>
          <div class='team-name' style='font-size:24px'>{eq_a}</div>
          <div class='lambda-val' style='font-size:18px'>λ = {lam_a:.3f}</div>
          <div style='margin-top:8px;color:#8ea3c0;font-size:13px'>Goles esperados</div>
        </div>""", unsafe_allow_html=True)
    with top_c2:
        st.markdown(f"""
        <div style='display:flex;align-items:center;justify-content:center;height:100%'>
          <div style='text-align:center'>
            <div style='font-size:36px;color:#8ea3c0;font-weight:900'>VS</div>
            <div class='winner-badge' style='margin-top:12px;font-size:14px'>
              🏆 {winner}
            </div>
          </div>
        </div>""", unsafe_allow_html=True)
    with top_c3:
        st.markdown(f"""
        <div class='team-block' style='border:1px solid rgba(59,130,246,0.2);border-radius:20px;padding:24px'>
          <div class='flag-big'>{fl_b}</div>
          <div class='team-name' style='font-size:24px'>{eq_b}</div>
          <div class='lambda-val' style='font-size:18px'>λ = {lam_b:.3f}</div>
          <div style='margin-top:8px;color:#8ea3c0;font-size:13px'>Goles esperados</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")

    # Tabs: matrix | probs | radar
    tab1, tab2, tab3 = st.tabs(["🎯 Matriz de Marcadores", "📊 Probabilidades", "🕸️ Radar de Atributos"])

    with tab1:
        st.markdown(f"#### Matriz de probabilidades (Poisson, 0–{GOL_MAX} goles)")
        st.plotly_chart(score_matrix_chart(mat, eq_a, eq_b), use_container_width=True)

        # Top 5 scores table
        st.markdown("##### 🔝 Top 5 marcadores más probables")
        top5 = scores[:5]
        df_top5 = pd.DataFrame(top5, columns=["Marcador", "Probabilidad"])
        df_top5["Probabilidad"] = df_top5["Probabilidad"].apply(lambda x: f"{x*100:.2f}%")
        st.dataframe(df_top5, use_container_width=True, hide_index=True)

    with tab2:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.plotly_chart(prob_donut(P_A, P_E, P_B, eq_a, eq_b), use_container_width=True)
        with c2:
            st.markdown(f"""
            <br>
            <div class='prob-bar-wrap'>
              <div class='prob-label'><span>{fl_a} {eq_a}</span><span><b>{P_A*100:.1f}%</b></span></div>
              <div class='prob-bar-bg'><div class='prob-bar-fill' style='width:{P_A*100:.1f}%'></div></div>
            </div>
            <div class='prob-bar-wrap'>
              <div class='prob-label'><span>🤝 Empate</span><span><b>{P_E*100:.1f}%</b></span></div>
              <div class='prob-bar-bg'><div class='prob-bar-fill' style='width:{P_E*100:.1f}%'></div></div>
            </div>
            <div class='prob-bar-wrap'>
              <div class='prob-label'><span>{fl_b} {eq_b}</span><span><b>{P_B*100:.1f}%</b></span></div>
              <div class='prob-bar-bg'><div class='prob-bar-fill' style='width:{P_B*100:.1f}%'></div></div>
            </div>
            <br>
            <div style='background:rgba(255,255,255,0.04);border-radius:14px;padding:16px;font-size:13px;color:#8ea3c0'>
              <b style='color:#2dd4ff'>λ {eq_a}</b> = {lam_a:.4f} goles esperados<br>
              <b style='color:#3b82f6'>λ {eq_b}</b> = {lam_b:.4f} goles esperados<br><br>
              <i>λ = (OV/100)^α × (100/DV_rival)^β × (MV/MV_ref)^γ × FA × k</i>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.plotly_chart(radar_chart(row_dict, row_dict, eq_a, eq_b), use_container_width=True)
        st.caption("DV = capacidad defensiva. Aclimatación normalizada al 100. MV escalado respecto al promedio del torneo.")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — TEAM ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Análisis de Equipos":

    st.markdown("# 📊 Análisis de Equipos")
    st.markdown("")

    all_teams = sorted(set(list(df["Equipo_A"]) + list(df["Equipo_B"])))
    team = st.selectbox("Selecciona un equipo", all_teams,
                        format_func=lambda x: f"{FLAGS.get(x,'⚽')} {x}")

    matches_a = df[df["Equipo_A"] == team].copy()
    matches_b = df[df["Equipo_B"] == team].copy()

    wins_a    = (matches_a["Ganador_Pred"] == team).sum()
    wins_b    = (matches_b["Ganador_Pred"] == team).sum()
    draws_a   = (matches_a["Ganador_Pred"] == "Empate").sum()
    draws_b   = (matches_b["Ganador_Pred"] == "Empate").sum()
    losses_a  = len(matches_a) - wins_a - draws_a
    losses_b  = len(matches_b) - wins_b - draws_b

    total_w = wins_a + wins_b
    total_d = draws_a + draws_b
    total_l = losses_a + losses_b
    total   = total_w + total_d + total_l

    st.markdown(f"## {FLAGS.get(team,'⚽')} {team}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Partidos", total)
    c2.metric("✅ Victorias pred.", total_w)
    c3.metric("🤝 Empates pred.", total_d)
    c4.metric("❌ Derrotas pred.", total_l)

    # Lambda averages
    lam_home = matches_a["lambda_A"].mean() if len(matches_a) else 0
    lam_away = matches_b["lambda_B"].mean() if len(matches_b) else 0
    avg_lam = np.nanmean([lam_home, lam_away])

    c1b, c2b, c3b = st.columns(3)
    c1b.metric("λ como Local", f"{lam_home:.3f}" if len(matches_a) else "—")
    c2b.metric("λ como Visitante", f"{lam_away:.3f}" if len(matches_b) else "—")
    c3b.metric("λ Promedio", f"{avg_lam:.3f}")

    st.markdown("---")

    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("##### Resultados predichos")
        fig_res = go.Figure(go.Bar(
            x=["Victorias", "Empates", "Derrotas"],
            y=[total_w, total_d, total_l],
            marker_color=["#22d3ee", "#8ea3c0", "#3b82f6"],
            text=[total_w, total_d, total_l],
            textposition="outside",
            textfont_color="#eef4ff",
        ))
        fig_res.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#eef4ff"),
            xaxis=dict(color="#8ea3c0"), yaxis=dict(color="#8ea3c0", gridcolor="rgba(255,255,255,0.07)"),
            margin=dict(l=10, r=10, t=20, b=10), height=280,
        )
        st.plotly_chart(fig_res, use_container_width=True)

    with col_r:
        st.markdown("##### Probabilidades promedio de victoria")
        avg_p_win_a = matches_a["P_Victoria_A"].mean() if len(matches_a) else 0
        avg_p_win_b = matches_b["P_Victoria_B"].mean() if len(matches_b) else 0
        fig_win = go.Figure(go.Bar(
            x=["Como Local", "Como Visitante"],
            y=[avg_p_win_a*100, avg_p_win_b*100],
            marker_color=["#22d3ee", "#3b82f6"],
            text=[f"{avg_p_win_a*100:.1f}%", f"{avg_p_win_b*100:.1f}%"],
            textposition="outside",
            textfont_color="#eef4ff",
        ))
        fig_win.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#eef4ff"),
            xaxis=dict(color="#8ea3c0"),
            yaxis=dict(color="#8ea3c0", gridcolor="rgba(255,255,255,0.07)", range=[0,100]),
            margin=dict(l=10, r=10, t=20, b=10), height=280,
        )
        st.plotly_chart(fig_win, use_container_width=True)

    # Match list
    st.markdown("##### 📋 Todos sus partidos")
    all_matches = pd.concat([
        matches_a[["Partido","Sede","Equipo_B","lambda_A","lambda_B","P_Victoria_A","P_Empate","P_Victoria_B","Ganador_Pred","Marcador_1","Marcador_2"]].rename(
            columns={"Equipo_B":"Rival","lambda_A":"λ_propio","lambda_B":"λ_rival",
                     "P_Victoria_A":"P_Win","P_Victoria_B":"P_Win_Rival"}),
        matches_b[["Partido","Sede","Equipo_A","lambda_B","lambda_A","P_Victoria_B","P_Empate","P_Victoria_A","Ganador_Pred","Marcador_1","Marcador_2"]].rename(
            columns={"Equipo_A":"Rival","lambda_B":"λ_propio","lambda_A":"λ_rival",
                     "P_Victoria_B":"P_Win","P_Victoria_A":"P_Win_Rival"}),
    ])
    all_matches = all_matches[["Partido","Sede","Rival","λ_propio","λ_rival","P_Win","P_Empate","Ganador_Pred","Marcador_1","Marcador_2"]]
    all_matches["P_Win"] = all_matches["P_Win"].apply(lambda x: f"{x*100:.1f}%")
    all_matches["P_Empate"] = all_matches["P_Empate"].apply(lambda x: f"{x*100:.1f}%")
    all_matches["λ_propio"] = all_matches["λ_propio"].round(3)
    all_matches["λ_rival"]  = all_matches["λ_rival"].round(3)
    all_matches["Partido"] = all_matches["Partido"].str.replace("_vs_", " vs ")
    st.dataframe(all_matches, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — FULL PREDICTIONS TABLE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📋 Tabla de Predicciones":

    st.markdown("# 📋 Tabla Completa de Predicciones")
    st.markdown("<span style='color:#8ea3c0'>72 partidos · Fase de Grupos · World Cup 2026</span>",
                unsafe_allow_html=True)
    st.markdown("")

    # Filter
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        ganador_filter = st.multiselect(
            "Filtrar por ganador predicho",
            options=["Todos"] + sorted(df["Ganador_Pred"].unique().tolist()),
            default=["Todos"],
        )
    with f_col2:
        sede_filter = st.multiselect(
            "Filtrar por sede",
            options=["Todas"] + sorted(df["Sede"].unique().tolist()),
            default=["Todas"],
        )

    filtered = df.copy()
    if "Todos" not in ganador_filter and ganador_filter:
        filtered = filtered[filtered["Ganador_Pred"].isin(ganador_filter)]
    if "Todas" not in sede_filter and sede_filter:
        filtered = filtered[filtered["Sede"].isin(sede_filter)]

    # Display table
    display_cols = ["Partido", "Sede", "Equipo_A", "Equipo_B",
                    "lambda_A", "lambda_B",
                    "P_Victoria_A", "P_Empate", "P_Victoria_B",
                    "Ganador_Pred", "Marcador_1", "Prob_Marcador_1",
                    "Marcador_2", "Prob_Marcador_2"]

    show_df = filtered[display_cols].copy()
    show_df["Partido"] = show_df["Partido"].str.replace("_vs_", " vs ")
    show_df["lambda_A"] = show_df["lambda_A"].round(3)
    show_df["lambda_B"] = show_df["lambda_B"].round(3)
    show_df["P_Victoria_A"] = show_df["P_Victoria_A"].apply(lambda x: f"{x*100:.1f}%")
    show_df["P_Empate"]      = show_df["P_Empate"].apply(lambda x: f"{x*100:.1f}%")
    show_df["P_Victoria_B"]  = show_df["P_Victoria_B"].apply(lambda x: f"{x*100:.1f}%")
    show_df["Prob_Marcador_1"] = show_df["Prob_Marcador_1"].apply(lambda x: f"{x*100:.2f}%")
    show_df["Prob_Marcador_2"] = show_df["Prob_Marcador_2"].apply(lambda x: f"{x*100:.2f}%")

    show_df = show_df.rename(columns={
        "Equipo_A": "Local", "Equipo_B": "Visitante",
        "lambda_A": "λ Local", "lambda_B": "λ Visita",
        "P_Victoria_A": "P(Local)", "P_Empate": "P(Empate)", "P_Victoria_B": "P(Visita)",
        "Ganador_Pred": "Ganador",
        "Marcador_1": "Score #1", "Prob_Marcador_1": "P(Score #1)",
        "Marcador_2": "Score #2", "Prob_Marcador_2": "P(Score #2)",
    })

    st.markdown(f"**{len(show_df)} partidos mostrados**")
    st.dataframe(show_df, use_container_width=True, hide_index=True, height=550)

    # Download button
    csv_bytes = filtered[display_cols].to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        label="⬇️ Descargar CSV filtrado",
        data=csv_bytes,
        file_name="predicciones_wc26_filtered.csv",
        mime="text/csv",
    )
