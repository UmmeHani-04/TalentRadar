# dashboard.py — Talent Radar Dashboard (FINAL)
# Run: streamlit run dashboard.py
# Requires: pip install streamlit pandas numpy plotly
import streamlit as st
import pandas as pd
import numpy as np
import re
import plotly.graph_objects as go
import plotly.express as px
import os, random

st.set_page_config(page_title="Talent Radar Dashboard", page_icon="🛰️",
                   layout="wide", initial_sidebar_state="expanded")

# ============================================================
# DESIGN SYSTEM — "Aurora Glass"
# ============================================================
C = {
    "bg": "#070A18", "bg2": "#0B1226",
    "glass": "rgba(20,28,54,0.55)",
    "border": "rgba(99,179,237,0.18)",
    "cyan": "#22D3EE", "violet": "#A78BFA", "blue": "#60A5FA",
    "green": "#34D399", "amber": "#FBBF24", "red": "#FB7185", "pink": "#F472B6",
    "text": "#EAF2FF", "muted": "#7C89A8",
}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap');

html, body, [class*="css"] {{ font-family:'Sora',sans-serif; color:{C['text']}; }}
.stApp {{
    background:
      radial-gradient(900px 600px at 12% 0%, rgba(34,211,238,0.10), transparent 60%),
      radial-gradient(900px 600px at 90% 10%, rgba(167,139,250,0.12), transparent 60%),
      radial-gradient(800px 600px at 50% 100%, rgba(96,165,250,0.08), transparent 60%),
      {C['bg']};
    background-attachment: fixed;
}}
.mono {{ font-family:'JetBrains Mono',monospace; }}
#MainMenu, footer, header {{ visibility:hidden; }}

.stApp::before {{
    content:""; position:fixed; inset:0; z-index:-1; opacity:0.5;
    background: conic-gradient(from 0deg at 50% 50%,
        rgba(34,211,238,0.06), rgba(167,139,250,0.06), rgba(96,165,250,0.06), rgba(34,211,238,0.06));
    animation: spin 40s linear infinite;
}}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}

section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #0A0F22, #0B1430);
    border-right:1px solid {C['border']};
}}

.glass {{
    background:{C['glass']}; backdrop-filter: blur(14px);
    border:1px solid {C['border']}; border-radius:20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.04);
}}

.hero {{
    position:relative; overflow:hidden; border-radius:26px; padding:42px 46px; margin-bottom:24px;
    background: linear-gradient(120deg, rgba(11,18,38,0.9), rgba(20,28,54,0.7));
    border:1px solid {C['border']};
    box-shadow: 0 20px 60px rgba(0,0,0,0.45);
    animation: rise .8s cubic-bezier(.2,.8,.2,1) both;
}}
.hero::before {{
    content:""; position:absolute; top:-50%; left:-30%; width:60%; height:200%;
    background: linear-gradient(120deg, transparent, rgba(34,211,238,0.18), rgba(167,139,250,0.14), transparent);
    transform: rotate(8deg); animation: sweep 5s infinite;
}}
@keyframes sweep {{ 0%{{left:-40%}} 100%{{left:120%}} }}
.hero h1 {{
    font-size:2.7rem; font-weight:800; margin:0; letter-spacing:-1px;
    background: linear-gradient(90deg,#EAF2FF,{C['cyan']},{C['violet']});
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    background-size:200% auto; animation: shine 6s linear infinite;
}}
@keyframes shine {{ to {{ background-position:200% center; }} }}
.hero p {{ color:#9FB0D0; font-size:1.05rem; margin-top:8px; }}
.live-dot {{ display:inline-block; width:9px; height:9px; border-radius:50%; background:{C['green']};
    box-shadow:0 0 0 0 rgba(52,211,153,.7); animation: pulse 1.8s infinite; margin-right:7px; }}
@keyframes pulse {{ 70%{{box-shadow:0 0 0 10px rgba(52,211,153,0)}} 100%{{box-shadow:0 0 0 0 rgba(52,211,153,0)}} }}

.badge {{
    border-radius:18px; padding:16px 18px; text-align:center;
    background: linear-gradient(160deg, rgba(34,211,238,0.10), rgba(167,139,250,0.08));
    border:1px solid {C['border']}; position:relative; overflow:hidden;
    animation: float 5s ease-in-out infinite;
}}
@keyframes float {{ 0%,100%{{transform:translateY(0)}} 50%{{transform:translateY(-7px)}} }}
.badge .lab {{ color:{C['muted']}; font-size:.66rem; letter-spacing:1.5px; text-transform:uppercase; }}
.badge .val {{ font-family:'JetBrains Mono'; font-size:1.4rem; font-weight:700; color:{C['cyan']}; }}

.kpi {{
    border-radius:20px; padding:22px 20px; position:relative; overflow:hidden;
    background:{C['glass']}; backdrop-filter:blur(12px); border:1px solid {C['border']};
    transition:.3s cubic-bezier(.2,.8,.2,1); animation: rise .7s ease both;
}}
.kpi:hover {{ transform: translateY(-8px) scale(1.02);
    box-shadow:0 18px 40px rgba(34,211,238,0.18); border-color:rgba(34,211,238,0.4); }}
.kpi::after {{ content:""; position:absolute; bottom:0; left:0; height:3px; width:100%;
    background:linear-gradient(90deg,{C['cyan']},{C['violet']});
    transform:scaleX(0); transform-origin:left; transition:.4s; }}
.kpi:hover::after {{ transform:scaleX(1); }}
.kpi .ic {{ font-size:1.3rem; }}
.kpi .lab {{ color:{C['muted']}; font-size:.72rem; text-transform:uppercase; letter-spacing:.6px; margin-top:8px; }}
.kpi .val {{ font-family:'JetBrains Mono'; font-size:2rem; font-weight:700; margin-top:4px;
    background:linear-gradient(90deg,#EAF2FF,{C['cyan']}); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}

.podium {{ border-radius:22px; padding:26px 20px; text-align:center; position:relative;
    background:{C['glass']}; backdrop-filter:blur(12px); animation: rise .8s ease both; transition:.35s; }}
.podium:hover {{ transform:translateY(-10px); }}
.podium .medal {{ font-size:3rem; filter:drop-shadow(0 4px 12px rgba(0,0,0,.5)); animation: float 4s ease-in-out infinite; }}
.podium .cid {{ font-family:'JetBrains Mono'; font-size:1.4rem; font-weight:700; margin-top:6px; }}
.podium .scr {{ font-family:'JetBrains Mono'; font-size:1.7rem; margin:6px 0;
    background:linear-gradient(90deg,{C['cyan']},{C['green']}); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
.podium .m {{ color:#9FB0D0; font-size:.85rem; font-family:'JetBrains Mono'; margin:2px 0; }}
.gold {{ border:2px solid {C['amber']}; box-shadow:0 0 32px rgba(251,191,36,.28); }}
.silver {{ border:2px solid #CBD5E1; box-shadow:0 0 32px rgba(203,213,225,.2); }}
.bronze {{ border:2px solid #FB923C; box-shadow:0 0 32px rgba(251,146,60,.22); }}

.section-h {{ font-size:1.35rem; font-weight:700; margin:26px 0 14px; display:flex; align-items:center; gap:10px; }}
.section-h::before {{ content:""; width:4px; height:24px; border-radius:4px;
    background:linear-gradient(180deg,{C['cyan']},{C['violet']}); }}

.statcard {{ border-radius:16px; padding:16px 18px; margin-bottom:12px;
    background:{C['glass']}; backdrop-filter:blur(10px); border:1px solid {C['border']}; transition:.3s; }}
.statcard:hover {{ border-color:rgba(167,139,250,.4); transform:translateX(4px); }}

@keyframes rise {{ from{{opacity:0; transform:translateY(22px)}} to{{opacity:1; transform:translateY(0)}} }}
.rlow {{color:{C['green']};font-weight:700}} .rmed {{color:{C['amber']};font-weight:700}} .rhigh {{color:{C['red']};font-weight:700}}

div[data-testid="stDataFrame"] {{ border-radius:16px; overflow:hidden; border:1px solid {C['border']}; }}
.stDownloadButton button, .stButton button {{
    border-radius:12px; border:1px solid {C['border']};
    background:linear-gradient(160deg,rgba(34,211,238,0.12),rgba(167,139,250,0.10));
    color:{C['text']}; font-weight:600; transition:.3s; }}
.stDownloadButton button:hover, .stButton button:hover {{
    border-color:{C['cyan']}; box-shadow:0 0 18px rgba(34,211,238,.3); transform:translateY(-2px); }}
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA — loads candidates.csv if present, else generates
# ============================================================
@st.cache_data
def load_data():
    if os.path.exists("candidates.csv"):
        df = pd.read_csv("candidates.csv")
    else:
        base = [
            ("CAND_007",1,0.868,"Staff ML Engineer 7yrs; skill:84%; semantic:76%; exp:100%; career:97%"),
            ("CAND_003",2,0.8655,"Senior AI Engineer 5.9yrs; skill:86%; semantic:79%; exp:100%; career:82%"),
            ("CAND_009",3,0.8624,"Senior AI Engineer 7.8yrs; skill:84%; semantic:73%; exp:100%; career:100%"),
            ("CAND_005",4,0.8498,"Applied ML Engineer 6yrs; skill:84%; semantic:71%; exp:100%; career:100%"),
            ("CAND_002",5,0.8483,"Search Engineer 4.2yrs; skill:84%; semantic:71%; exp:100%; career:100%"),
        ]
        rows=list(base); random.seed(42); np.random.seed(42)
        titles=["ML Engineer","Data Scientist","NLP Engineer","AI Researcher","MLOps Engineer",
                "Software Engineer","Research Scientist","LLM Engineer","Data Engineer"]
        for i,sc in enumerate(np.linspace(0.84,0.50,95)):
            rank=i+6; cid=f"CAND_{rank+1:03d}"
            sc=round(float(sc)+random.uniform(-.004,.004),4); sc=max(.50,min(.845,sc)); b=sc*100
            sk=int(np.clip(b+random.uniform(-8,8),35,95)); se=int(np.clip(b-8+random.uniform(-10,10),30,90))
            ex=int(np.clip(b+random.uniform(-5,20),40,100)); ca=int(np.clip(b+random.uniform(-10,15),35,100))
            rows.append((cid,rank,sc,f"{random.choice(titles)} {round(random.uniform(1.5,9.5),1)}yrs; skill:{sk}%; semantic:{se}%; exp:{ex}%; career:{ca}%"))
        df=pd.DataFrame(rows,columns=["candidate_id","rank","score","reasoning"])

    def pm(t,k):
        m=re.search(rf"{k}:(\d+)%",str(t)); return int(m.group(1)) if m else np.nan
    for k in ["skill","semantic","exp","career"]:
        df[k]=df["reasoning"].apply(lambda t: pm(t,k))
    df=df.sort_values("rank").reset_index(drop=True)
    qh,ql=df["score"].quantile(0.67),df["score"].quantile(0.33)
    df["risk"]=df["score"].apply(lambda s:"🟢 Low" if s>=qh else ("🟡 Medium" if s>=ql else "🔴 High"))
    return df

df=load_data()

# ---------- CLEAN EXPORT HELPER (fixes Excel emoji garbage) ----------
def make_export(frame):
    """Return a clean copy for CSV: emoji-free risk so Excel shows Low/Medium/High."""
    out = frame.copy()
    risk_map = {"🟢 Low": "Low", "🟡 Medium": "Medium", "🔴 High": "High"}
    if "risk" in out.columns:
        out["risk"] = out["risk"].map(risk_map).fillna(out["risk"])
    return out

def to_csv_bytes(frame):
    # utf-8-sig adds a BOM so Excel detects UTF-8 correctly (no more ðŸŸ¢ garbage)
    return make_export(frame).to_csv(index=False).encode("utf-8-sig")

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown(f"<h2 style='margin-bottom:0'>🛰️ Talent Radar</h2>"
                f"<p class='mono' style='color:{C['muted']};font-size:.72rem;letter-spacing:1px'>INTELLIGENCE SUITE </p>",
                unsafe_allow_html=True)
    st.divider()
    st.markdown("#### 🎛️ Filters")
    top_n=st.slider("Top N candidates",10,100,100,5)
    smin,smax=st.slider("Score range",0.50,0.90,(float(df.score.min()),float(df.score.max())),0.01)
    kmin,kmax=st.slider("Skill range (%)",0,100,(0,100),5)
    risk_opt=["🟢 Low","🟡 Medium","🔴 High"]
    risk_sel=st.multiselect("Risk level",risk_opt,default=risk_opt)
    st.divider()
    st.markdown("#### ⚖️ Compare Candidates")
    cmp=st.multiselect("Pick up to 3",df.candidate_id.tolist(),default=df.candidate_id.tolist()[:3],max_selections=3)
    mode=st.radio("Display",["Top N","Show all"],horizontal=True)
    st.divider()
    st.caption("🛰️ Talent Radar · Talent Intelligence Suite")

fdf=df[(df.score>=smin)&(df.score<=smax)&(df.skill>=kmin)&(df.skill<=kmax)&(df.risk.isin(risk_sel))].copy()
if mode=="Top N": fdf=fdf[fdf["rank"]<=top_n]

# ============================================================
# HERO
# ============================================================
top=df.iloc[0]
h1,h2=st.columns([3,1.5])
with h1:
    st.markdown(f"""<div class="hero">
        <h1>🛰️ Talent Radar Dashboard</h1>
        <p><span class="live-dot"></span>AI / NLP-powered candidate ranking · <b>{len(df)}</b> profiles scanned in real time</p>
    </div>""",unsafe_allow_html=True)
with h2:
    b1,b2=st.columns(2)
    b1.markdown(f"""<div class="badge"><div class="lab">Top Candidate</div>
        <div class="val">{top.candidate_id}</div>
        <div class="mono" style="color:#9FB0D0;font-size:.85rem">{top.score:.3f}</div></div>""",unsafe_allow_html=True)
    b2.markdown(f"""<div class="badge"><div class="lab">Total Ranked</div>
        <div class="val">{len(df)}</div>
        <div class="mono" style="color:#9FB0D0;font-size:.85rem">candidates</div></div>""",unsafe_allow_html=True)

# ============================================================
# KPI
# ============================================================
st.markdown('<div class="section-h">📊 Key Metrics</div>',unsafe_allow_html=True)
kth=df.skill.quantile(0.75)
kpis=[("👥","Total Candidates",f"{len(df)}"),("⚡","Average Score",f"{df.score.mean():.3f}"),
      ("🚀","Top 10 Avg",f"{df.nsmallest(10,'rank').score.mean():.3f}"),
      ("🎯","High Skill",f"{int((df.skill>=kth).sum())}"),
      ("🛡️","Low Risk Hires",f"{int((df.risk=='🟢 Low').sum())}")]
for col,(ic,lab,val) in zip(st.columns(5),kpis):
    col.markdown(f"""<div class="kpi"><div class="ic">{ic}</div>
        <div class="lab">{lab}</div><div class="val">{val}</div></div>""",unsafe_allow_html=True)

# ============================================================
# PODIUM
# ============================================================
st.markdown('<div class="section-h">🏆 Champions Podium</div>',unsafe_allow_html=True)
podium_data=[("🥇","gold",0),("🥈","silver",1),("🥉","bronze",2)]
for col,(medal,cls,idx) in zip(st.columns(3),podium_data):
    r=df.iloc[idx]
    col.markdown(f"""<div class="podium {cls}"><div class="medal">{medal}</div>
        <div class="cid">{r.candidate_id}</div><div class="scr">{r.score:.3f}</div>
        <div class="m">⚙️ Skill {r.skill}%</div><div class="m">🧠 Semantic {r.semantic}%</div>
        <div class="m">📈 Experience {r.exp}%</div></div>""",unsafe_allow_html=True)

# ============================================================
# CHART HELPER
# ============================================================
def sf(fig,h=400):
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
        font_color=C["text"],font_family="Sora",height=h,margin=dict(l=20,r=20,t=50,b=20),
        legend=dict(bgcolor="rgba(0,0,0,0)"),title_font_size=15)
    fig.update_xaxes(gridcolor="rgba(99,179,237,0.10)",zerolinecolor="rgba(99,179,237,0.15)")
    fig.update_yaxes(gridcolor="rgba(99,179,237,0.10)",zerolinecolor="rgba(99,179,237,0.15)")
    return fig

# CHARTS ROW 1
st.markdown('<div class="section-h">🔭 Distribution & Talent Map</div>',unsafe_allow_html=True)
a,b=st.columns(2)
with a:
    cnt,bins=np.histogram(df.score,bins=15); ctr=(bins[:-1]+bins[1:])/2
    t10=df.nsmallest(10,"rank").score.min()
    cols_=[C["green"] if c>=t10 else C["blue"] for c in ctr]
    f=go.Figure(go.Bar(x=ctr,y=cnt,marker_color=cols_,marker_line_width=0))
    f.update_layout(title="Score Distribution (green = top-10 zone)",bargap=.05,
                    xaxis_title="Composite Score",yaxis_title="Count")
    st.plotly_chart(sf(f),use_container_width=True)
with b:
    f=px.scatter(df,x="skill",y="semantic",size="score",color="score",
        color_continuous_scale=[C["violet"],C["blue"],C["cyan"],C["green"]],size_max=28,hover_name="candidate_id")
    for i in range(3):
        r=df.iloc[i]
        f.add_annotation(x=r.skill,y=r.semantic,text=f"#{r['rank']} {r.candidate_id}",
            showarrow=True,arrowcolor=C["amber"],font=dict(color=C["amber"],size=11))
    f.update_layout(title="Talent Map · Skill × Semantic",xaxis_title="Skill %",yaxis_title="Semantic %")
    st.plotly_chart(sf(f),use_container_width=True)

# CHARTS ROW 2
st.markdown('<div class="section-h">⚡ Top 10 Deep Dive</div>',unsafe_allow_html=True)
c,d=st.columns(2)
with c:
    t=df.nsmallest(10,"rank").sort_values("score"); n=len(t)
    grad=[f"rgb({int(167-(167-34)*i/(n-1))},{int(139+(211-139)*i/(n-1))},{int(250-(250-238)*i/(n-1))})" for i in range(n)]
    f=go.Figure(go.Bar(x=t.score,y=t.candidate_id,orientation="h",marker_color=grad,
        text=[f"{s:.3f}" for s in t.score],textposition="outside"))
    f.update_layout(title="Top 10 by Composite Score",xaxis_title="Score")
    st.plotly_chart(sf(f),use_container_width=True)
with d:
    t=df.nsmallest(10,"rank")
    f=go.Figure()
    f.add_bar(name="Skill",x=t.candidate_id,y=t.skill,marker_color=C["cyan"])
    f.add_bar(name="Semantic",x=t.candidate_id,y=t.semantic,marker_color=C["green"])
    f.add_bar(name="Experience",x=t.candidate_id,y=t.exp,marker_color=C["amber"])
    f.add_bar(name="Career",x=t.candidate_id,y=t.career,marker_color=C["pink"])
    f.update_layout(title="4-Factor Breakdown (Top 10)",barmode="group",yaxis_title="%")
    st.plotly_chart(sf(f),use_container_width=True)

# COMPARISON
st.markdown('<div class="section-h">⚖️ Candidate Face-Off</div>',unsafe_allow_html=True)
cc,sc_=st.columns([2,1.3])
cats=["Score","Skill","Semantic","Experience","Career"]; rc=[C["cyan"],C["violet"],C["amber"]]
with cc:
    f=go.Figure()
    for i,cid in enumerate(cmp):
        r=df[df.candidate_id==cid].iloc[0]
        v=[r.score*100,r.skill,r.semantic,r.exp,r.career]
        f.add_trace(go.Scatterpolar(r=v+[v[0]],theta=cats+[cats[0]],fill="toself",name=cid,
            line_color=rc[i%len(rc)]))
    f.update_layout(title="Multi-Factor Radar",polar=dict(bgcolor="rgba(0,0,0,0)",
        radialaxis=dict(range=[0,100],gridcolor="rgba(99,179,237,0.12)"),
        angularaxis=dict(gridcolor="rgba(99,179,237,0.12)")))
    st.plotly_chart(sf(f,430),use_container_width=True)
with sc_:
    for cid in cmp:
        r=df[df.candidate_id==cid].iloc[0]
        cls="rlow" if "Low" in r.risk else("rmed" if "Medium" in r.risk else "rhigh")
        st.markdown(f"""<div class="statcard"><div class="mono" style="font-size:1.1rem;font-weight:700">
            {r.candidate_id}<span style="float:right" class="{cls}">{r.risk}</span></div>
            <div class="mono" style="color:#9FB0D0;font-size:.85rem;margin-top:6px">
            Score {r.score:.3f} · Rank #{r['rank']}<br>⚙️ {r.skill}% · 🧠 {r.semantic}%<br>
            📈 {r.exp}% · 🚀 {r.career}%</div></div>""",unsafe_allow_html=True)

# ============================================================
# 🤖 AI HIRE RECOMMENDATION
# ============================================================
st.markdown('<div class="section-h">🤖 AI Hire Recommendation</div>', unsafe_allow_html=True)

rec_col, out_col = st.columns([1, 2.2])
with rec_col:
    pick = st.selectbox("Select a candidate to analyze", df.candidate_id.tolist(), index=0)

def hire_recommendation(r):
    score, sk, se, ex, ca = r.score, r.skill, r.semantic, r.exp, r.career
    if score >= 0.82:
        verdict, vcolor, emoji = "STRONG HIRE", C["green"], "✅"
    elif score >= 0.72:
        verdict, vcolor, emoji = "HIRE", C["cyan"], "👍"
    elif score >= 0.62:
        verdict, vcolor, emoji = "INTERVIEW", C["amber"], "🟡"
    else:
        verdict, vcolor, emoji = "HOLD / PASS", C["red"], "⚠️"
    metrics = {"technical skill": sk, "semantic fit": se, "experience": ex, "career trajectory": ca}
    strengths = [k for k, v in metrics.items() if v >= 80]
    concerns  = [k for k, v in metrics.items() if v < 65]
    s_txt = ", ".join(strengths) if strengths else "balanced profile with no standout peaks"
    c_txt = ", ".join(concerns) if concerns else "no major red flags detected"
    conf = int(min(99, max(40, (score - df.score.min()) / (df.score.max() - df.score.min()) * 100)))
    if verdict == "STRONG HIRE":
        action = "Fast-track to final round and prepare a competitive offer."
    elif verdict == "HIRE":
        action = "Advance to technical + culture interview; strong potential."
    elif verdict == "INTERVIEW":
        action = "Schedule a screening call to validate borderline metrics."
    else:
        action = "Keep in talent pool; revisit if stronger needs arise."
    return verdict, vcolor, emoji, conf, s_txt, c_txt, action

with out_col:
    r = df[df.candidate_id == pick].iloc[0]
    verdict, vcolor, emoji, conf, s_txt, c_txt, action = hire_recommendation(r)
    st.markdown(f"""
    <div class="glass" style="padding:24px 28px; border-radius:20px; border-left:4px solid {vcolor};">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div class="mono" style="font-size:1.3rem; font-weight:700">{r.candidate_id}</div>
            <div style="background:{vcolor}22; color:{vcolor}; padding:6px 16px; border-radius:30px;
                 font-weight:700; font-size:.9rem; border:1px solid {vcolor}55">{emoji} {verdict}</div>
        </div>
        <div class="mono" style="color:{C['muted']}; margin-top:6px; font-size:.85rem">
            Composite {r.score:.3f} · Rank #{r['rank']} · Confidence {conf}%</div>
        <div style="margin-top:16px; line-height:1.7; color:{C['text']}; font-size:.95rem">
            <b style="color:{C['green']}">💪 Strengths:</b> {s_txt}.<br>
            <b style="color:{C['amber']}">🔍 Watch-outs:</b> {c_txt}.<br>
            <b style="color:{C['cyan']}">📌 Recommended action:</b> {action}
        </div>
        <div style="margin-top:14px; background:rgba(255,255,255,0.04); border-radius:10px; overflow:hidden; height:8px">
            <div style="width:{conf}%; height:100%; background:linear-gradient(90deg,{C['cyan']},{vcolor})"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# TABLE
# ============================================================
st.markdown('<div class="section-h">📋 Full Ranking Console</div>',unsafe_allow_html=True)
s1,s2,s3=st.columns([2,1,1])
search=s1.text_input("🔍 Search by Candidate ID","")
s2.download_button("⬇️ Full CSV", to_csv_bytes(df),
                   "talent_radar_full.csv", "text/csv", use_container_width=True)
s3.download_button("⬇️ Top 10 CSV", to_csv_bytes(df.nsmallest(10, "rank")),
                   "talent_radar_top10.csv", "text/csv", use_container_width=True)
tbl=fdf.copy()
if search: tbl=tbl[tbl.candidate_id.str.contains(search,case=False,na=False)]
disp=tbl[["rank","candidate_id","score","skill","semantic","exp","career","risk"]].copy()
disp.columns=["Rank","Candidate ID","Score","Skill","Semantic","Experience","Career","Risk Flag"]
st.dataframe(disp,use_container_width=True,hide_index=True,height=480,column_config={
    "Score":st.column_config.ProgressColumn("Score",min_value=0.0,max_value=1.0,format="%.3f"),
    "Skill":st.column_config.ProgressColumn("Skill",min_value=0,max_value=100,format="%d%%"),
    "Semantic":st.column_config.ProgressColumn("Semantic",min_value=0,max_value=100,format="%d%%"),
    "Experience":st.column_config.ProgressColumn("Experience",min_value=0,max_value=100,format="%d%%"),
    "Career":st.column_config.ProgressColumn("Career",min_value=0,max_value=100,format="%d%%")})
st.caption(f"Showing {len(disp)} of {len(df)} candidates · 🛰️ Talent Radar Dashboard ")