# 🚀 TalentRadar AI

### Intelligent AI-Powered Candidate Ranking & Talent Discovery Platform

TalentRadar is a full-stack AI-powered recruitment platform that helps recruiters discover, rank, and analyze candidates beyond traditional keyword-based filtering.

Instead of relying only on keyword matching, TalentRadar evaluates candidates across multiple dimensions such as **semantic relevance, skills, experience, career momentum, behavioral signals, hidden talent, authenticity, and future potential** to provide a more comprehensive candidate assessment.

---

## 🌐 Live Demo

**🚀 Try TalentRadar:**
https://talentradar-frontend-app.onrender.com

**📂 GitHub Repository:**
https://github.com/UmmeHani-04/TalentRadar

---

## 📌 Project Overview

Traditional Applicant Tracking Systems (ATS) often depend heavily on keyword matching. This can cause potentially strong candidates to be overlooked when their resumes use different terminology or when their potential is not directly represented through keywords.

TalentRadar addresses this challenge using an AI-assisted ranking pipeline that combines semantic matching with multiple candidate evaluation factors.

### 🎯 Main Goal

> Build an intelligent candidate discovery system that goes beyond keyword matching and provides explainable, multi-dimensional candidate ranking.

---

## ✨ Key Features

### 🧠 AI Candidate Ranking

Ranks candidates according to their relevance to a given job description.

### 🔍 Semantic Matching

Uses semantic similarity and TF-IDF-based matching to identify relevant candidate profiles even when exact keywords differ.

### 📊 Multi-Dimensional Candidate Analysis

Candidates are evaluated across multiple dimensions:

* Semantic Relevance
* Skills Match
* Experience
* Career Momentum
* Behavioral Signals
* Hidden Talent
* Profile Authenticity
* Future Potential

### 📈 Analytics Dashboard

Provides recruitment analytics and visual insights into candidate data and ranking results.

### 👤 Candidate Profiles

Recruiters can open individual candidate profiles to view:

* Candidate information
* Skills
* Experience
* Match score
* Risk level
* AI reasoning
* Strengths
* Weaknesses

### ⚡ AI-Assisted Recommendations

The system generates an interpretable recommendation based on candidate scores and risk assessment.

### 📄 Candidate Report

Candidate analysis can be exported as a downloadable report.

### 🔎 Candidate Search

Recruiters can search and filter candidate profiles from the candidate database.

### 🌐 Full-Stack Deployment

The application is deployed with:

* Frontend → Render
* Backend API → Render
* GitHub → Source control

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────────┐
                    │      Recruiter/User     │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │     Next.js Frontend    │
                    │   React + Tailwind CSS   │
                    └────────────┬────────────┘
                                 │
                                 │ REST API
                                 ▼
                    ┌─────────────────────────┐
                    │      FastAPI Backend    │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   Ranking Pipeline      │
                    │                         │
                    │ • Semantic Matching     │
                    │ • Skills Analysis       │
                    │ • Experience Analysis   │
                    │ • Momentum              │
                    │ • Risk Assessment       │
                    │ • Explainability        │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    Ranked Candidates    │
                    │ + Scores + Reasoning     │
                    └─────────────────────────┘
```

---

## 🧠 How Candidate Ranking Works

The ranking pipeline combines multiple signals rather than relying on a single keyword score.

```text
Job Description
       │
       ▼
Candidate Data
       │
       ▼
Feature Extraction
       │
       ├── Semantic Relevance
       ├── Skills Match
       ├── Experience
       ├── Career Momentum
       ├── Behavioral Signals
       ├── Hidden Talent
       ├── Authenticity
       └── Future Potential
       │
       ▼
Multi-Dimensional Scoring
       │
       ▼
Risk Assessment
       │
       ▼
Explainable Ranking
       │
       ▼
Ranked Candidate Results
```

The system also provides reasoning alongside candidate scores so that recruiters can understand why a candidate received a particular ranking.

---

## 📊 Main Application Modules

| Module               | Description                                    |
| -------------------- | ---------------------------------------------- |
| 🏠 Dashboard         | Overview of the recruitment platform           |
| 👥 Candidates        | Browse and search candidate profiles           |
| 🧠 AI Ranking        | Rank candidates against a job description      |
| 👤 Candidate Details | Detailed candidate analysis                    |
| 📈 Analytics         | Recruitment and candidate insights             |
| 💎 Hidden Talent     | Identify potentially overlooked candidates     |
| 💼 New Job           | Submit a job description for candidate ranking |

---

## 🛠️ Tech Stack

### Frontend

* Next.js 16
* React
* TypeScript
* Tailwind CSS
* Lucide React
* Recharts / data visualization components

### Backend

* Python
* FastAPI
* Pydantic
* Pandas
* NumPy
* Scikit-learn
* Python DOCX

### AI / Ranking

* Semantic matching
* TF-IDF fallback
* Multi-dimensional candidate scoring
* Risk assessment
* Explainable ranking

### Deployment & Tools

* GitHub
* Render
* REST APIs
* VS Code

---

## 📁 Project Structure

```text
TalentRadar/
│
├── backend/
│   ├── main.py
│   ├── routes/
│   │   └── ranking.py
│   └── ...
│
├── talentradar-frontend/
│   ├── app/
│   │   ├── candidates/
│   │   ├── analytics/
│   │   ├── dashboard/
│   │   ├── hidden-talent/
│   │   ├── new-job/
│   │   └── lib/
│   │       ├── api.ts
│   │       └── types.ts
│   │
│   ├── components/
│   ├── public/
│   ├── package.json
│   └── next.config.mjs
│
├── src/
│   └── data/
│
├── rank.py
├── generate_csv.py
├── validate_submission.py
├── candidates.csv
├── ranked_candidates.csv
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 🔌 Backend API

The backend exposes REST endpoints for candidate ranking and analytics.

| Method | Endpoint                         | Description                               |
| ------ | -------------------------------- | ----------------------------------------- |
| `POST` | `/api/rank`                      | Rank candidates against a job description |
| `GET`  | `/api/candidates`                | Retrieve candidate list                   |
| `GET`  | `/api/candidates/{candidate_id}` | Retrieve candidate details                |
| `GET`  | `/api/analytics`                 | Retrieve analytics data                   |

### API Documentation

The FastAPI backend also provides interactive API documentation through Swagger UI:

```text
https://talentradar-1.onrender.com/docs
```

---

## ⚙️ Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/UmmeHani-04/TalentRadar.git
cd TalentRadar
```

---

### 2. Backend Setup

Create and activate a Python virtual environment:

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
uvicorn backend.main:app --reload
```

Backend will be available at:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

---

### 3. Frontend Setup

Open another terminal:

```bash
cd talentradar-frontend
```

Install dependencies:

```bash
pnpm install
```

Create an environment file:

```text
.env.local
```

Add:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

Start the development server:

```bash
pnpm dev
```

Frontend will be available at:

```text
http://localhost:3000
```

---

## 🌍 Deployment

TalentRadar is deployed using Render.

### Frontend

```text
Next.js
      ↓
Render Web Service
      ↓
https://talentradar-frontend-app.onrender.com
```

### Backend

```text
FastAPI
      ↓
Render
      ↓
https://talentradar-1.onrender.com
```

The frontend communicates with the backend through the environment variable:

```env
NEXT_PUBLIC_API_BASE_URL
```

---


## 🎯 Why TalentRadar?

TalentRadar focuses on a broader candidate evaluation approach:

```text
Traditional ATS
      │
      └── Keyword Matching
              │
              ▼
        Candidate Filtering


TalentRadar
      │
      ├── Semantic Matching
      ├── Skills
      ├── Experience
      ├── Career Momentum
      ├── Behavioral Signals
      ├── Hidden Talent
      ├── Authenticity
      └── Future Potential
              │
              ▼
       Explainable Ranking
```

This approach is designed to help surface candidates who may be missed by purely keyword-based screening.

---

## 🔮 Future Improvements

* [ ] Advanced LLM-based candidate reasoning
* [ ] Resume upload and automatic parsing
* [ ] Recruiter authentication
* [ ] Candidate comparison mode
* [ ] Advanced filtering and sorting
* [ ] Interview scheduling
* [ ] Recruiter feedback loop
* [ ] Model performance monitoring
* [ ] Bias and fairness monitoring
* [ ] Automated email notifications

---
## 👩‍💻 Contributors

This project was collaboratively developed by:

* **Umme Hani** — Developer
* **Ritu Ahirwar** — Developer

This project was developed as part of a **Hackathon / AI-based talent discovery challenge**.



## 📄 License

This project was created by Umme Hani and Ritu Ahirwar as part of a hackathon project.

The source code is provided for educational, portfolio, and demonstration purposes.

```

