from pydantic import BaseModel, validator
from utils.peewee_util import PeeweeGetterDict
from typing import Optional
from datetime import datetime


class GroupIn(BaseModel):
    name: str
    description: Optional[str] = ""
    code: Optional[str] = None
    require_approve: Optional[bool] = False


class GroupOut(GroupIn):
    ID: int

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class GroupUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    code: Optional[str]
    require_approve: Optional[bool]


class UserInGroup(BaseModel):
    ID: int
    fullname: str
    student_id: str
    phone: str

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class ManagerInGroup(BaseModel):
    ID: int
    fullname: str

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class MemberInGroup(BaseModel):
    user: UserInGroup
    joined_at: datetime
    approved_at: Optional[datetime] = None
    approve: Optional[bool] = None
    added_by: Optional[ManagerInGroup] = None

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class GroupOfMember(BaseModel):
    group: GroupOut
    joined_at: datetime
    approved_at: Optional[datetime] = None
    approve: Optional[bool] = None
    added_by: Optional[ManagerInGroup] = None

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict

