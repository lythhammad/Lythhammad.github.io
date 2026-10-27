import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from authenticator import authenticator
from routers import accounts, favorites, parks, reviews

# Local development origins, used only when CORS_HOST is not set.
DEFAULT_ORIGINS = ["http://localhost:3000", "http://localhost:8000"]

# Only the HTTP methods and headers the frontend actually needs.
ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
ALLOWED_HEADERS = ["Content-Type", "Authorization", "Accept"]


def get_allowed_origins() -> list[str]:
    """
    Build the list of allowed CORS origins.

    CORS_HOST may hold one origin or several separated by commas.
    Blank entries are ignored, and if nothing is set we fall back to
    the local development origins.
    """
    raw = os.environ.get("CORS_HOST", "")
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    return origins or DEFAULT_ORIGINS


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=ALLOWED_METHODS,
    allow_headers=ALLOWED_HEADERS,
)

app.include_router(authenticator.router, tags=["Auth"])
app.include_router(accounts.router, tags=["Auth"])
app.include_router(favorites.router, tags=["Favorites"])
app.include_router(parks.router, tags=["Parks"])
app.include_router(reviews.router, tags=["Reviews"])
