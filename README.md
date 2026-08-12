# 🚀 TalentRadar — AI-Powered Candidate Ranking Dashboard

> An AI-assisted recruitment intelligence platform designed to help recruiters evaluate, rank, and compare candidates using multi-factor scoring, semantic matching, experience analysis, and risk insights.

<p align="center">
  <a href="https://ummehani-04.github.io/TalentRadar/TalentRadar_Dashbaord.html">
    <strong>🌐 View Live Dashboard →</strong>
  </a>
</p>

---

## 📌 Overview

**TalentRadar** is an AI-powered candidate ranking and recruitment analytics system built to simulate how an intelligent Applicant Tracking System (ATS) can evaluate candidates.

The system processes candidate profiles against a job description and generates a ranked candidate pool using multiple factors such as:

* Technical skill matching
* Semantic similarity
* Experience
* Career signals
* Risk indicators
* Overall candidate fit

The results are presented through an interactive recruiter-focused dashboard for easier analysis and decision-making.

---

## ✨ Key Features

### 🎯 Candidate Ranking

Ranks candidates using a composite score generated from multiple evaluation factors.

### 🧠 Semantic Matching

Uses semantic similarity to evaluate how well a candidate's profile aligns with the requirements of a job description.

### 📊 Recruitment Analytics

Provides visual insights into:

* Score distribution
* Risk breakdown
* Global score trends
* Experience distribution
* Hiring funnel metrics
* Skill vs. semantic correlation

### ⚠️ Risk Analysis

Provides risk-tier insights to help recruiters identify potential concerns within candidate profiles.

### 🔍 Candidate Search & Filtering

Recruiters can search candidates using identifiers, titles, or skills and explore individual candidate profiles.

### 🤖 TalentGPT Recruiter Copilot

An AI-assisted evaluation layer designed to generate recruiter-oriented insights from candidate scoring patterns.

### ⚖️ Candidate Comparison

The dashboard includes a matrix comparison interface for evaluating multiple candidates across different scoring dimensions.

### ➕ Candidate Management

Recruiters can add candidate profiles with:

* Candidate ID
* Role
* Composite score
* Technical skill percentage
* Semantic alignment percentage

---

## 🖥️ Dashboard

The TalentRadar dashboard provides a centralized view of the candidate pool, including **100 candidate profiles**, ranking information, score distributions, risk tiers, analytics, and candidate comparison tools.

### 🌐 Live Demo

**[🚀 Open TalentRadar Dashboard](https://ummehani-04.github.io/TalentRadar/TalentRadar_Dashbaord.html)**

---

## 🛠️ Tech Stack

### Frontend

* HTML5
* CSS3
* JavaScript
* Chart.js

### AI / Data Processing

* Python
* Pandas
* Sentence Transformers
* `all-MiniLM-L6-v2`
* Semantic similarity
* Multi-factor candidate scoring

### Development Tools

* Git
* GitHub
* VS Code

---

## 🔄 How It Works

```text
Job Description
       ↓
JD Parsing
       ↓
Candidate Profile Processing
       ↓
Rule-Based Scoring
       ↓
Semantic Matching
       ↓
Multi-Factor Candidate Scoring
       ↓
Risk & Career Analysis
       ↓
Candidate Ranking
       ↓
TalentRadar Dashboard
```

---

## 📈 Candidate Evaluation

TalentRadar combines multiple dimensions to produce a more comprehensive candidate evaluation:

| Factor          | Purpose                                               |
| --------------- | ----------------------------------------------------- |
| Technical Score | Measures technical skill alignment                    |
| Semantic Score  | Measures semantic similarity with the job description |
| Experience      | Evaluates relevant professional experience            |
| Career Score    | Considers career-related signals                      |
| Risk Tier       | Highlights potential candidate risks                  |
| Composite Score | Combines multiple factors into an overall ranking     |

---

## 📂 Project Structure

```text
TalentRadar/
│
├── src/
│   ├── config.py
│   ├── jd_parser.py
│   ├── semantic_matcher.py
│   └── ranker.py
│
├── TalentRadar_Dashbaord.html
├── candidates.csv
├── generate_csv.py
├── rank.py
├── ranked_candidates.csv
├── parsed_jd.json
├── requirements.txt
├── submission.csv
├── submission_metadata.yaml
├── test_submission.csv
└── validate_submission.py
```

---

## 🎯 Project Goals

TalentRadar was designed to explore how AI and semantic search can improve traditional candidate screening by:

* Reducing manual candidate screening effort
* Ranking candidates according to job relevance
* Combining rule-based and semantic evaluation
* Providing explainable candidate insights
* Helping recruiters compare candidates more efficiently

---

## 🚀 Future Improvements

* Resume upload and automatic parsing
* Real-time AI-generated candidate explanations
* Advanced recruiter filtering
* Authentication and recruiter accounts
* Backend API integration
* Persistent candidate database
* Improved LLM-powered candidate reasoning
* Production-ready deployment

---

## 👥 Team Project

TalentRadar was developed as part of a **Data & AI Challenge**, involving collaborative work across candidate analysis, job-description understanding, ranking logic, risk analysis, explainability, and dashboard development.

---

## 🔗 Links

* 🌐 **[Live Dashboard](https://ummehani-04.github.io/TalentRadar/TalentRadar_Dashbaord.html)**
* 💻 **[GitHub Repository](https://github.com/UmmeHani-04/TalentRadar)**

---

## 📄 License

This project was created for educational, hackathon, and portfolio purposes.
