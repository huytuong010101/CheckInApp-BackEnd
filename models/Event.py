from peewee import *
from datetime import datetime
from models.BaseModel import BaseModel
from models.Location import Location
from models.Manager import Manager
from models.User import User
from models.Group import Group
from config import LIMIT_CHECKIN

class Event(BaseModel):
    # PK
    ID = PrimaryKeyField()
    # Info
    title = CharField()
    place = TextField()
    maximum_participant = IntegerField(null=True, constraints=[SQL("UNSIGNED")])
    # FK
    location = ForeignKeyField(Location, null=True, backref="has_events", on_delete="SET NULL")
    # Time
    created_at = DateTimeField(default=datetime.now())
    updated_at = DateTimeField(null=True)
    # Event time
    start_at = DateTimeField()
    stop_at = DateTimeField()
    start_register_at = DateTimeField(default=datetime.now())
    stop_register_at = DateTimeField(null=True)
    # Late and soon
    soon_checkin_time = IntegerField(null=True, constraints=[SQL("UNSIGNED")])
    late_checkin_time = IntegerField(null=True, constraints=[SQL("UNSIGNED")])
    soon_checkout_time = IntegerField(null=True, constraints=[SQL("UNSIGNED")])
    late_checkout_time = IntegerField(null=True, constraints=[SQL("UNSIGNED")])

    def add_group(self, group: Group):
        return LimitGroup.get_or_create(group=group, event=self)

    def remove_group(self, group: Group):
        LimitGroup.delete().where((LimitGroup.group == group) & (LimitGroup.event == self))

    def valid_to_register(self, user: User):
        # Check if registerd
        registered = RegisterEvent.get_or_none(event=self, user=user)
        if registered:
            if registered.block:
                return False, "Bạn đã bị chặn khỏi sự kiện này"
            return False, "Sự kiện đã được đăng ký từ trước"
        # check if enough member
        if self.maximum_participant is not None:
            num_participants = RegisterEvent.select()\
                .where((RegisterEvent.event == self) & (RegisterEvent.block == False))\
                .count()
            if num_participants >= self.maximum_participant:
                return False, "Đã vượt quá số người cho phép"
        # Check if not in group
        limit_groups = LimitGroup.select().where(LimitGroup.event == self)
        if limit_groups.exists():
            for group in limit_groups:
                if group.has_member(user):
                    return True, ""
            return False, "Bạn không thuộc nhóm được phép đăng ký"
        return True, ""

    def add_participant(self, user: User, add_by: Manager = None, note: str = None):
        return RegisterEvent.get_or_create(user=user, event=self, block=False, added_by=add_by, note=note)

    def check_in_with_image(self, user: User, image_path: str, accept: bool = None, score: float = None):
        return CheckinImage.create(path=image_path, user=user, event=self, accept=accept, score=score)

    def block_participant(self, user: User, note: str = None):
        result = RegisterEvent.get_or_create(user=user, event=self)
        result.block = True
        if note:
            result.note = note
        result.save(force_insert=True)
        return result

    def __str__(self):
        return str(self.title)


class EventDetail(BaseModel):
    event = ForeignKeyField(Event, primary_key=True, backref="event_detail", on_delete="SET NULL")
    description = TextField(null=True)
    created_by = ForeignKeyField(Manager, null=True, backref="create_events", on_delete="SET NULL")
    leader = ForeignKeyField(Manager, null=True, backref="lead_events", on_delete="SET NULL")


class CheckinImage(BaseModel):
    # PK
    ID = PrimaryKeyField()
    # Info
    path = CharField()
    uploaded_at = DateTimeField(default=datetime.now)
    accept = BooleanField(default=None, null=True)
    accepted_at = DateTimeField(null=True)
    score = DoubleField(null=True, constraints=[Check("score IS NULL OR (score >= 0 AND score <= 1)")])
    # FK
    user = ForeignKeyField(User, backref="checkin_images", on_delete="CASCADE")
    event = ForeignKeyField(Event, backref="checkin_image", on_delete="CASCADE")

    def approve_checkin(self, score: float = None):
        self.accept = True
        self.accepted_at = datetime.now()
        self.score = score
        return self

    def reject_checkin(self, score: float = None):
        self.accept = False
        self.accepted_at = datetime.now()
        self.score = score
        return self

    @staticmethod
    def valid_to_checkin(user_id: int, event_id: int):
        register = RegisterEvent.get_or_none(user=user_id, event=event_id)
        if register is None:
            return False, "Bạn không thể điểm danh khi chưa đăng ký sự kiện"
        if register.block:
            return False, "Bạn đã bị chặn khỏi sự kiện này"
        checkins = CheckinImage.select().where((CheckinImage.event == event_id) & (CheckinImage.user == user_id))
        if checkins.count() >= LIMIT_CHECKIN:
            return False, "Đã vượt quá số lần điểm danh cho phép"
        for checkin in checkins:
            print(checkin.accept)
            if checkin.accept is None:
                return False, "Bạn đang có một lượt điểm danh chưa được đánh giá"
            if checkin.accept is True:
                return False, "Bạn đã điểm danh thành công cho sự kiên này từ trước"
        return True, ""

    def __str__(self):
        return f"User: {str(self.user)}, Event: {str(self.event)}"


class LimitGroup(BaseModel):
    # FR
    group = ForeignKeyField(Group, backref="limit_groups", on_delete="CASCADE")
    event = ForeignKeyField(Event, backref="limit_groups", on_delete="CASCADE")

    # PK
    class Meta:
        primary_key = CompositeKey('group', 'event')

    def __str__(self):
        return f"Allow group {str(self.group)} join {str(self.event)}"


class RegisterEvent(BaseModel):
    # FK
    user = ForeignKeyField(User, backref="register_events", on_delete="CASCADE")
    event = ForeignKeyField(Event, backref="has_register", on_delete="CASCADE")
    added_by = ForeignKeyField(Manager, null=True, backref="add_to_events", on_delete="SET NULL")
    # Info
    block = BooleanField(default=False)
    note = TextField(null=True)
    feedback = TextField(null=True)
    # Time
    created_at = DateTimeField(default=datetime.now())
    checkin_at = DateTimeField(null=True)
    checkout_at = DateTimeField(null=True)

    # PK
    class Meta:
        primary_key = CompositeKey('user', 'event')

    def __str__(self):
        return f"{str(self.user)} register {str(self.group)}"
