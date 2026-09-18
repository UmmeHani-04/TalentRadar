"""TalentRadar FastAPI Backend Server."""

import sys
from pathlib import Path

# Ensure the project root (TalentRadar/) is in the Python path
# so that `rank.py` and `src/` can be imported correctly.
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.ranking import router as ranking_router, initialize_sample_store

app = FastAPI(title="TalentRadar API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ranking_router, prefix="/api", tags=["ranking"])


@app.on_event("startup")
async def startup_initialize_store() -> None:
    try:
        initialize_sample_store()
        print("[Startup] Sample ranking store initialized.")
    except Exception as error:
        print(f"[Startup] Sample store initialization failed: {error}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)