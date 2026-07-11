from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import SessionLocal
from app.modules.access.router import router as groups_router
from app.modules.audit.router import router as activity_logs_router
from app.modules.auth.router import router as auth_router
from app.modules.health import router as health_router
from app.modules.modules.router import router as modules_router
from app.modules.modules.seed import seed_modules
from app.modules.trading_import.router import router as trading_import_router
from app.modules.users.router import router as users_router
from app.modules.users.seed import seed_root_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        seed_root_admin(
            db,
            full_name=settings.root_admin_full_name,
            email=settings.root_admin_email,
            password=settings.root_admin_password,
        )
        seed_modules(db)
    finally:
        db.close()

    yield


app = FastAPI(title=settings.app_name, version=settings.app_version, debug=settings.debug, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(activity_logs_router, prefix=settings.api_prefix)
app.include_router(users_router, prefix=settings.api_prefix)
app.include_router(modules_router, prefix=settings.api_prefix)
app.include_router(groups_router, prefix=settings.api_prefix)
app.include_router(trading_import_router, prefix=settings.api_prefix)


@app.get("/", tags=["Root"])
def root():
    return {"message": f"Welcome to {settings.app_name}"}
