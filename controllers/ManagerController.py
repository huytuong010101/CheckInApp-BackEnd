from datetime import datetime
from models.Manager import Manager
from config import USER_IN_PAGE, AVATAR_DIR, AVATAR_BASE_URL
from utils import file_handle
import os
import uuid


class ManagerController:
    @staticmethod
    def get_by_id(user_id: int) -> Manager:
        return Manager.get_or_none(ID=user_id)

    @staticmethod
    def search(fullname: str = None, phone: str = "", username: str = "", page: int = None) -> list:
        search_results = Manager.select().where(
            (Manager.fullname.contains(fullname))
            & (((Manager.phone.is_null()) & (phone == "")) | (Manager.phone.contains(phone)))
            & (Manager.username.contains(username))
        )
        if page:
            return list(search_results.paginate(page, USER_IN_PAGE))
        else:
            return list(search_results)

    @staticmethod
    def update(user_id: int, detail: dict) -> Manager:
        detail["updated_at"] = datetime.now()
        Manager.update(**detail).where(Manager.ID == user_id).execute()
        return Manager.get_or_none(ID=user_id)

    @staticmethod
    def create(detail) -> Manager:
        user = Manager(**detail)
        user.update_password(detail["password"])  # include save method
        return user

    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str):
        user = Manager.get_or_none(ID=user_id)
        if user is None:
            raise ValueError("Tài khoản không tồn tại")
        if not user.compare_password(old_password):
            raise ValueError("Mật khẩu cũ không chính xác")
        user.update_password(new_password)

    @staticmethod
    def force_change_password(user_id: int, new_password: str):
        user = Manager.get_or_none(ID=user_id)
        if user:
            user.update_password(new_password)

    @staticmethod
    def update_avatar(user_id: int, image_data: str) -> str:
        # check user_id
        user = Manager.get_or_none(ID=user_id)
        if not user:
            raise ValueError("Tài khoản không tồn tại")
        # prepare
        now = datetime.now().strftime("%Y-%m-%d.%H-%M-%S")
        filename = f"manager_{user_id}.{uuid.uuid4()}.{now}.jpg"
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




