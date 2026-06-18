from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.common.response import make_response
from app.db.session import get_db
from app.modules.auth.dependencies import require_root
from app.modules.modules.model import Module
from app.modules.modules.schemas import ModuleRead
from app.modules.users.model import User


router = APIRouter(prefix="/modules", tags=["Modules"])


@router.get("")
def list_modules(db: Session = Depends(get_db), _: User = Depends(require_root)):
    modules = db.scalars(select(Module).order_by(Module.sort_order)).all()
    data = [ModuleRead.model_validate(module).model_dump(mode="json") for module in modules]
    return make_response(True, "Modules fetched successfully", data)
