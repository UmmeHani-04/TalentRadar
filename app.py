import streamlit as st
import pandas as pd
import plotly.express as px

# Page Config
st.set_page_config(
    page_title="AI Recruitment Intelligence Dashboard",
    page_icon="🏆",
    layout="wide"
)

# Title
st.title("🏆 AI Recruitment Intelligence Dashboard")
st.markdown("### Hackathon Candidate Ranking & Explainability System")

# Load CSV
df = pd.read_csv("ranked_candidates.csv")

# Metrics
st.subheader("📊 Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Candidates", len(df))

with col2:
    st.metric(
        "Average Final Score",
        round(df["final_score"].mean(), 3)
    )

with col3:
    st.metric(
        "Top Score",
        round(df["final_score"].max(), 3)
    )

with col4:
    st.metric(
        "Candidates > 0.70",
        len(df[df["final_score"] > 0.70])
    )

st.divider()

# Top 10 Candidates
st.subheader("🏅 Top 10 Candidates")

top10 = df.sort_values(
    "final_score",
    ascending=False
).head(10)

fig = px.bar(
    top10,
    x="candidate_id",
    y="final_score",
    title="Top 10 Ranked Candidates"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# Score Distribution
st.subheader("📈 Score Distribution")

fig2 = px.histogram(
    df,
    x="final_score",
    nbins=20,
    title="Distribution of Final Scores"
)

st.plotly_chart(fig2, use_container_width=True)

st.divider()

# Candidate Explorer
st.subheader("🔍 Candidate Explorer")

selected_candidate = st.selectbox(
    "Select Candidate",
    df["candidate_id"]
)

candidate_data = df[
    df["candidate_id"] == selected_candidate
].iloc[0]

st.write(f"### Candidate: {selected_candidate}")

st.write(
    f"Semantic Score: {candidate_data['semantic_score']}"
)
st.progress(
    float(candidate_data["semantic_score"]) / 100
)

st.write(
    f"Skill Score: {candidate_data['skill_score']}"
)
st.progress(
    float(candidate_data["skill_score"]) / 100
)

st.write(
    f"Experience Score: {candidate_data['experience_score']}"
)
st.progress(
    float(candidate_data["experience_score"]) / 100
)

st.write(
    f"Career Score: {candidate_data['career_score']}"
)
st.progress(
    float(candidate_data["career_score"]) / 100
)

st.write(
    f"Behavior Score: {candidate_data['behavior_score']}"
)
st.progress(
    float(candidate_data["behavior_score"]) / 100
)

st.success(
    f"Final Score: {candidate_data['final_score']}"
)

st.divider()

# Rankings Table
st.subheader("📋 Candidate Rankings")

st.dataframe(
    df.sort_values(
        "final_score",
        ascending=False
    ),
    use_container_width=True
)