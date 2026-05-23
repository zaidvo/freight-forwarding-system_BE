from pydantic import BaseModel


class ModuleRead(BaseModel):
    id: int
    name: str
    slug: str
    icon: str
    color: str
    route: str | None
    is_active: bool
    sort_order: int

    model_config = {"from_attributes": True}
