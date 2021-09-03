from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional, List
from utils.peewee_util import PeeweeGetterDict
from pydantics.Manager import ManageOut
from pydantics.Location import LocationOut
from pydantics.Group import GroupOut
from models.Event import Event, EventDetail


class EventBase(BaseModel):
    title: str
    place: str
    maximum_participant: Optional[int] = None
    # time
    start_at: datetime
    stop_at: datetime
    start_register_at: datetime
    stop_register_at: Optional[datetime] = None
    # Late and soon
    soon_checkin_time: Optional[int] = None
    late_checkin_time: Optional[int] = None
    soon_checkout_time: Optional[int] = None
    late_checkout_time: Optional[int] = None


class EventOut(EventBase):
    ID: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    location: Optional[LocationOut] = None
    num_participant: Optional[int] = None

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class EventDetail(BaseModel):
    description: Optional[str] = None
    created_by: Optional[ManageOut] = None
    leader: Optional[ManageOut] = None

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class EventOutDetail(EventOut):
    event_detail: Optional[EventDetail] = None
    limit_group: Optional[List[GroupOut]] = []

    @staticmethod
    def from_orm_load(event):
        result = EventOutDetail.from_orm(event)
        result.event_detail = EventDetail.from_orm(event.event_detail.first())
        result.limit_group = []
        for limit in event.limit_groups.select():
            result.limit_group.append(GroupOut.from_orm(limit.group))
        return result

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class EventIn(EventBase):
    location: Optional[int] = None
    description: Optional[str] = None
    leader: Optional[int] = None
    created_by: Optional[int] = None
    limit_group: Optional[List[int]] = []

    @validator("maximum_participant")
    def validate_maximum_participant(cls, value: int):
        if value is not None and value < 0:
            raise ValueError("Số lượng người tham gia không hợp lệ")
        return value

    @validator("stop_at")
    def validate_stop_at(cls, value: datetime, values: dict):
        if value < values["start_at"]:
            raise ValueError("Thời gian kết thúc không hợp lệ")
        return value

    @validator("stop_register_at")
    def validate_stop_register_at(cls, value: datetime, values: dict):
        if value < values["start_register_at"]:
            raise ValueError("Thời gian kết thúc đăng ký không hợp lệ")
        return value


class EventUpdate(BaseModel):
    title: Optional[str]
    place: Optional[str]
    maximum_participant: Optional[int]
    location: Optional[int]
    # time
    start_at: Optional[datetime]
    stop_at: Optional[datetime]
    start_register_at: Optional[datetime]
    stop_register_at: Optional[datetime]
    # Late and soon
    soon_checkin_time: Optional[int]
    late_checkin_time: Optional[int]
    soon_checkout_time: Optional[int]
    late_checkout_time: Optional[int]

    @validator("maximum_participant")
    def validate_maximum_participant(cls, value: int):
        if value < 0:
            raise ValueError("Số lượng người tham gia không hợp lệ")
        return value

    @validator("stop_at")
    def validate_stop_at(cls, value: datetime, values: dict):
        if value < values["start_at"]:
            raise ValueError("Thời gian kết thúc không hợp lệ")
        return value

    @validator("stop_register_at")
    def validate_stop_register_at(cls, value: datetime, values: dict):
        if value < values["start_register_at"]:
            raise ValueError("Thời gian kết thúc đăng ký không hợp lệ")
        return value


class EventDetailUpdate(BaseModel):
    # detail
    description: Optional[str]
    created_by: Optional[int]
    leader: Optional[int]


class UserInEvent(BaseModel):
    ID: int
    fullname: str
    student_id: str
    phone: str

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class ManagerInEvent(BaseModel):
    ID: int
    fullname: str

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class EventRegister(BaseModel):
    added_by: Optional[ManagerInEvent] = None
    block: bool
    note: Optional[str] = None
    feedback: Optional[str] = None
    created_at: datetime
    checkin_at: Optional[datetime] = None
    checkout_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class EventParticipant(EventRegister):
    user: UserInEvent

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class BriefEvent(BaseModel):
    ID: int
    title: str
    place: str

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class EventOfUser(EventRegister):
    event: BriefEvent

    class Config:
        orm_mode = True
        getter_dict = PeeweeGetterDict


class Feedback(BaseModel):
    content: str


