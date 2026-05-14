from fastapi import APIRouter

from app.common.response import make_response


router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", summary="Health check")
def health_check():
    return make_response(success=True, message="API is healthy", data={"status": "ok"})
