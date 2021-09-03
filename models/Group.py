from models.BaseModel import BaseModel
from peewee import *
from datetime import datetime
from models.User import User
from models.Manager import Manager


class Group(BaseModel):
    # PK
    ID = PrimaryKeyField()
    # info
    name = CharField(max_length=255)
    description = TextField(null=True)
    code = CharField(max_length=255, null=True)
    require_approve = BooleanField(default=False)

    def add_member(self, user: User, add_by: Manager = None, approve: bool = None):
        result = JoinGroup(user=user, group=self, added_by=add_by)
        result.approve = approve if self.require_approve else True
        if result.approve:
            result.approved_at = datetime.now()
        result.save(force_insert=True)
        return result

    def approve_member(self, user: User):
        result = JoinGroup.get_or_none(JoinGroup.user == user & JoinGroup.group == self)
        if result:
            result.approve = True
            result.approved_at = datetime.now()
            result.save()
        return result

    def reject_member(self, user: User):
        result = JoinGroup.get_or_none(JoinGroup.user == user & JoinGroup.group == self)
        if result:
            result.approve = False
            result.approved_at = None
            result.save()
        return result

    def has_member(self, user: User):
        return JoinGroup.select().where(
            (JoinGroup.user == user)
            & (JoinGroup.group == self)
            & (JoinGroup.approve is True)
        ).exists()

    def valid_to_join(self, user_id: int):
        if JoinGroup.select().where((JoinGroup.group == self) & (JoinGroup.user == user_id)).exists():
            return False, "Bạn đã nằm trong nhóm này từ trước"
        if self.code is not None:
            join_with_code = \
                JoinGroup.select()\
                .join(Group).where((JoinGroup.user == user_id) & (JoinGroup.group.code == self.code))\
                .first()
            if join_with_code:
                return False, "Bạn không thể tham gia nhóm này khi đã tham gia nhóm " + join_with_code.group.name
        return True, ""

    def __str__(self):
        return str(self.name)


class JoinGroup(BaseModel):
    # FK
    group = ForeignKeyField(Group, backref="has_joins", on_delete="CASCADE")
    user = ForeignKeyField(User, backref="join_groups", on_delete="CASCADE")
    # info
    joined_at = DateTimeField(default=datetime.now())
    approved_at = DateTimeField(null=True)
    approve = BooleanField(default=False, null=True)
    # FK
    added_by = ForeignKeyField(Manager, null=True, backref="add_to", on_delete="SET NULL")

    # PK
    class Meta:
        primary_key = CompositeKey('group', 'user')

    def __str__(self):
        return f"{str(self.user)} join group {str(self.group)}"
