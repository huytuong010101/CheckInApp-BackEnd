from peewee import *
from models.BaseModel import BaseModel
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Manager(BaseModel):
    # PK
    ID = PrimaryKeyField()
    # info
    fullname = CharField(max_length=255)
    email = CharField(max_length=255, null=True)
    phone = CharField(max_length=15, null=True)
    is_admin = BooleanField(default=False)
    avatar_image = CharField(null=True)
    # time
    created_at = DateTimeField(default=datetime.now())
    updated_at = DateTimeField(null=True)
    # authentication
    username = CharField(max_length=255, unique=True)
    password = CharField(max_length=255)

    def compare_password(self, hash_password):
        pwd_context.verify(self.password, hash_password)

    def update_password(self, password: str):
        self.password = pwd_context.hash(password)
        self.save()

    def __str__(self):
        return str(self.fullname)
