# generate_csv.py — creates candidates.csv (100 candidates)
import pandas as pd, numpy as np, random

base_rows = [
    ("CAND_007", 1, 0.868, "Staff ML Engineer 7yrs; skill:84%; semantic:76%; exp:100%; career:97%"),
    ("CAND_003", 2, 0.8655, "Senior AI Engineer 5.9yrs; skill:86%; semantic:79%; exp:100%; career:82%"),
    ("CAND_009", 3, 0.8624, "Senior AI Engineer 7.8yrs; skill:84%; semantic:73%; exp:100%; career:100%"),
    ("CAND_005", 4, 0.8498, "Applied ML Engineer 6yrs; skill:84%; semantic:71%; exp:100%; career:100%"),
    ("CAND_002", 5, 0.8483, "Search Engineer 4.2yrs; skill:84%; semantic:71%; exp:100%; career:100%"),
]
rows = list(base_rows)
titles = ["ML Engineer","Data Scientist","NLP Engineer","AI Researcher","Backend Engineer",
          "MLOps Engineer","Computer Vision Engineer","Software Engineer","Research Scientist",
          "Deep Learning Engineer","Applied Scientist","Data Engineer","LLM Engineer"]
random.seed(42); np.random.seed(42)
scores = np.linspace(0.84, 0.50, 95)
for i, sc in enumerate(scores):
    rank = i + 6
    cid = f"CAND_{rank+1:03d}"
    sc = round(float(sc) + random.uniform(-0.004, 0.004), 4)
    sc = max(0.50, min(0.845, sc))
    base = sc * 100
    skill = int(np.clip(base + random.uniform(-8, 8), 35, 95))
    semantic = int(np.clip(base - 8 + random.uniform(-10, 10), 30, 90))
    exp = int(np.clip(base + random.uniform(-5, 20), 40, 100))
    career = int(np.clip(base + random.uniform(-10, 15), 35, 100))
    yrs = round(random.uniform(1.5, 9.5), 1)
    title = random.choice(titles)
    reasoning = f"{title} {yrs}yrs; skill:{skill}%; semantic:{semantic}%; exp:{exp}%; career:{career}%"
    rows.append((cid, rank, sc, reasoning))

df = pd.DataFrame(rows, columns=["candidate_id","rank","score","reasoning"])
df.to_csv("candidates.csv", index=False)
print(f"✅ candidates.csv created with {len(df)} rows")