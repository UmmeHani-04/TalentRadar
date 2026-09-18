---
title: TalentRadar API
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# TalentRadar AI

Discover Talent Beyond Keywords.

An Explainable Talent Discovery Engine that intelligently ranks candidates, discovers hidden talent, evaluates risk, and explains every hiring decision.

---

## The Problem
Current Applicant Tracking Systems (ATS) rely heavily on exact keyword matching. This leads to massive inefficiencies in modern hiring:
- Hidden talent is missed because candidates use different terminology for the same skills.
- Keyword stuffing fools the system.
- Black Box AI: There is no explanation behind candidate rankings.
- Recruiters lack context: They don't understand why a candidate was selected.

## Our Solution
TalentRadar AI completely revolutionizes the talent discovery pipeline. Instead of looking for words, our AI looks for meaning. 

By leveraging advanced semantic matching, automated risk evaluation, and Explainable AI (XAI), TalentRadar helps recruiters find the perfect candidate—even if their resume doesn't perfectly match the exact wording of the job description.

---

## High-Level Architecture

```text
Recruiter (Web Browser)
    |
    v
[ Frontend: Next.js (React) ]
    |
    | (REST API via Vercel)
    v
[ Backend: FastAPI (Python) ]  <-- Hosted on Hugging Face Spaces
    |
    +---> [1. JD Parser Module]
    |
    +---> [2. Semantic Matcher Module] (Sentence Transformers)
    |
    +---> [3. Risk Assessment Engine]
    |
    +---> [4. Explainable AI Generator]
```

## Key Features

- **Semantic Matching**: Understands candidate profiles beyond exact keywords using NLP sentence transformers.
- **Hidden Talent Discovery**: Finds candidates with highly transferable skills who might not fit traditional keyword filters.
- **Explainable AI**: Generates human-readable explanations detailing exactly why a candidate was recommended.
- **Risk Analysis**: Automatically detects risky hiring patterns (e.g., job hopping, low momentum).
- **Comprehensive Analytics**: A dynamic dashboard providing insights into the talent pool and score distributions.

---

## Tech Stack

**Frontend:**
- Next.js 14 (React)
- Tailwind CSS
- Recharts (Data Visualization)

**Backend:**
- FastAPI (Python)
- Sentence Transformers
- Pandas / Scikit-learn

---

## Quick Start (Local Development)

### 1. Start the Backend (FastAPI)
```bash
pip install -r backend/requirements.txt
python -m backend.main
```

### 2. Start the Frontend (Next.js)
```bash
cd talentradar-frontend
npm install
npm run dev
```

---
Built for the Hackathon.
