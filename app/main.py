from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.db.session import SessionLocal
from app.modules.auth.router import router as auth_router
from app.modules.health import router as health_router
from app.modules.users.router import router as users_router
from app.modules.users.seed import seed_super_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        seed_super_admin(
            db,
            full_name=settings.root_admin_full_name,
            email=settings.root_admin_email,
            password=settings.root_admin_password,
        )
    finally:
        db.close()

    yield


app = FastAPI(title=settings.app_name, version=settings.app_version, debug=settings.debug, lifespan=lifespan)

app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(users_router, prefix=settings.api_prefix)


@app.get("/", tags=["Root"])
def root():
    return {"message": f"Welcome to {settings.app_name}"}
