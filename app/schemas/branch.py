from pydantic import BaseModel, ConfigDict
from datetime import datetime


class BranchBase(BaseModel):
    name: str
    location: str


class BranchCreate(BranchBase):
    pass


class Branch(BranchBase):
    id: int
    created_at: datetime


class BranchResponse(BranchBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class BranchUpdate(BranchBase):
    id: int
