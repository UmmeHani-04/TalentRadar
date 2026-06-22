import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.set_page_config(page_title="AI Hiring Dashboard", layout="wide")

# Load data
df = pd.read_csv("submission.csv")

# Extract values from reasoning text
def extract(text, key):
    match = re.search(rf"{key}:(\d+)%", text)
    return int(match.group(1)) if match else None

df["skill"] = df["reasoning"].apply(lambda x: extract(x, "skill"))
df["semantic"] = df["reasoning"].apply(lambda x: extract(x, "semantic"))
df["career"] = df["reasoning"].apply(lambda x: extract(x, "career"))

df["flagged"] = df["reasoning"].str.contains("flags", na=False)

# Title
st.title("🏆 AI Recruitment Ranking Dashboard")

# KPIs
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Candidates", len(df))
col2.metric("Avg Score", round(df["score"].mean(), 4))
col3.metric("Top Score", df["score"].max())
col4.metric("Flagged Candidates", df["flagged"].sum())

# Top 10 table
st.subheader("🥇 Top 10 Candidates")
st.dataframe(df.sort_values("rank").head(10), use_container_width=True)

# Search
st.subheader("🔍 Search Candidate")
search = st.text_input("Enter Candidate ID")

if search:
    st.dataframe(df[df["candidate_id"] == search])

# Score distribution
st.subheader("📊 Score Distribution")
fig = px.histogram(df, x="score", nbins=20)
st.plotly_chart(fig, use_container_width=True)

# Skill vs Semantic
st.subheader("🧠 Skill vs Semantic Analysis")
fig2 = px.scatter(
    df,
    x="skill",
    y="semantic",
    size="score",
    color="score",
    hover_data=["candidate_id"]
)
st.plotly_chart(fig2, use_container_width=True)

# Full table
st.subheader("📋 Full Ranking Table")
st.dataframe(df, use_container_width=True)