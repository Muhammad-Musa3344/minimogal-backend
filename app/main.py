# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import FRONTEND_ORIGIN
from app.api import (
    auth_routes,
    wallet_routes,
    decision_routes,
    profile_routes,
    screen_5_routes,
)

app = FastAPI(title="Mogul Mind Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(wallet_routes.router)
app.include_router(decision_routes.router)
app.include_router(profile_routes.router)
app.include_router(screen_5_routes.router)


@app.get("/health")
def health():
    return {"status": "ok"}