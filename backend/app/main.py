from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import allocation, lifeguards, locations, settings
from .core.deps import get_cors_origins
from .db import init_db, session_scope
from .services.import_export import seed_if_empty


app = FastAPI(title="Lifeguard Shift Manager", version="1.0.0")

origins = get_cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


@app.on_event("startup")
async def startup_event() -> None:
    with session_scope() as session:
        seed_if_empty(session)


app.include_router(lifeguards.router, prefix="/api/v1")
app.include_router(locations.router, prefix="/api/v1")
app.include_router(settings.router, prefix="/api/v1")
app.include_router(allocation.router, prefix="/api/v1")


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}
