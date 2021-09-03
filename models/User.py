from peewee import *
from models.BaseModel import BaseModel
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(BaseModel):
    # PK
    ID = PrimaryKeyField()
    # info
    fullname = CharField(max_length=255)
    date_of_birth = DateField()
    student_id = CharField(max_length=9, unique=True)
    email = CharField(max_length=255, null=True)
    phone = CharField(max_length=15, unique=True)
    phone_verify = BooleanField(default=False)
    email_verify = BooleanField(default=False)
    avatar_image = CharField(null=True)
    block = BooleanField(default=False)
    note = TextField(null=True)
    # time
    created_at = DateTimeField(default=datetime.now())
    updated_at = DateTimeField(null=True)
    # authentication
    username = CharField(max_length=255, unique=True)
    password = CharField(max_length=255)

    def add_identity_image(self, path: str):
        IdentityImages.create(path=path, user=self)

    def remove_identity_image(self, image_id: int = None, path: str = None):
        if image_id:
            IdentityImages.delete().where((IdentityImages.ID == image_id) & (IdentityImages.user == self))
        elif path:
            IdentityImages.delete().where((IdentityImages.path == path) & (IdentityImages.user == self))

    def compare_password(self, hash_password):
        pwd_context.verify(self.password, hash_password)

    def update_password(self, password: str):
        self.password = pwd_context.hash(password)
        self.save()

    def __str__(self):
        return str(self.fullname)


class IdentityImages(BaseModel):
    # PK
    ID = PrimaryKeyField()
    # Info
    path = CharField()
    uploaded_at = DateTimeField(default=datetime.now())
    approve = BooleanField(default=False)
    # FK
    user = ForeignKeyField(User, backref="identity_images", on_delete="CASCADE")

    def __str__(self):
        return f"Image {str(self.ID)} of  {str(self.user)}"
