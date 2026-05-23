from datetime import datetime

from pydantic import BaseModel, Field


class GroupBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    module_ids: list[int] = Field(default_factory=list)


class GroupCreate(GroupBase):
    pass


class GroupUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    module_ids: list[int] | None = None


class GroupRead(BaseModel):
    id: int
    name: str
    description: str | None
    module_ids: list[int]
    user_ids: list[int]
    created_at: datetime
    updated_at: datetime


class UserGroupsUpdate(BaseModel):
    group_ids: list[int] = Field(default_factory=list)
