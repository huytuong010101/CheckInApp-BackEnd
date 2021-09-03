from datetime import datetime
from models.User import User, IdentityImages
from config import USER_IN_PAGE, AVATAR_BASE_URL, AVATAR_DIR, IDENTITY_IMAGE_DIR
from models.Group import Group
import uuid
from utils import file_handle
import os

class UserController:
    @staticmethod
    def get_by_id(user_id: int) -> User:
        return User.get_or_none(ID=user_id)

    @staticmethod
    def search(fullname: str = None, student_id: str = "", phone: str = "", username: str = "", page: int = None) -> list:
        search_results = User.select().where(
            (User.fullname.contains(fullname))
            & (User.student_id.contains(student_id))
            & (User.phone.contains(phone))
            & (User.username.contains(username))
        )
        if page:
            return list(search_results.paginate(page, USER_IN_PAGE))
        else:
            return list(search_results)

    @staticmethod
    def update(user_id: int, detail: dict) -> User:
        detail["updated_at"] = datetime.now()
        User.update(**detail).where(User.ID == user_id).execute()
        return User.get_or_none(ID=user_id)

    @staticmethod
    def create(detail) -> User:
        user = User(**detail)
        user.update_password(detail["password"]) #include save method
        return user

    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str):
        user = User.get_or_none(ID=user_id)
        if user is None:
            raise ValueError("Tài khoản không tồn tại")
        if not user.compare_password(old_password):
            raise ValueError("Mật khẩu cũ không chính xác")
        user.update_password(new_password)

    @staticmethod
    def delete(user_id: int):
        if user := User.get_or_none(ID=user_id):
            old_filename = user.avatar_image.split("/")[-1]
            old_filepath = os.path.join(AVATAR_DIR, old_filename)
            file_handle.delete_file(old_filepath)
            user.delete_instance()

    @staticmethod
    def join_group(user_id: int, group_id: int):
        group = Group.get_or_none(ID=group_id)
        if group is None:
            raise ValueError("Nhóm này không tồn tại")
        success, error = group.valid_to_join(user_id)
        if not success:
            raise ValueError(error)
        group.add_member(user=user_id)

    @staticmethod
    def update_avatar(user_id: int, image_data: str) -> str:
        # check user_id
        user = User.get_or_none(ID=user_id)
        if not user:
            raise ValueError("Tài khoản không tồn tại")
        # prepare
        now = datetime.now().strftime("%Y-%m-%d.%H-%M-%S")
        filename = f"student_{user_id}.{uuid.uuid4()}.{now}.jpg"
        filepath = os.path.join(AVATAR_DIR, filename)
        avatar_url = AVATAR_BASE_URL + "/" + filename
        old_avatar = user.avatar_image
        # upload image
        try:
            file_handle.save_file(image_data, filepath)
        except Exception as err:
            print("Error when save file " + filepath)
            print(err)
            return ""
        # update in db
        try:
            user.avatar_image = avatar_url
            user.save()
        except Exception as err:
            file_handle.delete_file(filepath)
            return ""
        # delete old file
        if old_avatar:
            old_filename = old_avatar.split("/")[-1]
            old_filepath = os.path.join(AVATAR_DIR, old_filename)
            try:
                file_handle.delete_file(old_filepath)
            except Exception as err:
                print(">> Error when delete old avatar " + old_filepath)
                print(err)
        return avatar_url










