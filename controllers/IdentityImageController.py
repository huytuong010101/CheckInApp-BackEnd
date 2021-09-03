from models.User import User, IdentityImages
from datetime import datetime
import os
from utils import file_handle
from config import IDENTITY_IMAGE_DIR, USER_IN_PAGE
import uuid


class IdentityImageController:
    @staticmethod
    def get_identity_images(user_id: int = None, from_date: datetime = None, to_date: datetime = None, page: int = None):
        search_results = IdentityImages.select().where(
            ((user_id is None) | (IdentityImages.user == user_id))
            & ((from_date is None) | (IdentityImages.uploaded_at >= from_date))
            & ((to_date is None) | (IdentityImages.uploaded_at <= to_date))
        )
        if page:
            return list(search_results.paginate(page, USER_IN_PAGE))
        else:
            return list(search_results)

    @staticmethod
    def get_image_path(image_id: int, user_id: int = None) -> str:
        image = IdentityImages.get_or_none(image_id)
        if image is None:
            return None
        if user_id is not None and image.user.ID != user_id:
            raise ValueError("Bạn không có quyền truy cập ảnh này")
        return image.path

    @staticmethod
    def add_identity_image(user_id: int, image_data: str) -> IdentityImages:
        # check user_id
        user = User.get_or_none(ID=user_id)
        if not user:
            raise ValueError("Tài khoản không tồn tại")
        # prepare
        now = datetime.now().strftime("%Y-%m-%d.%H-%M-%S")
        filename = f"student_{user_id}.{uuid.uuid4()}.{now}.jpg"
        save_dir = os.path.join(IDENTITY_IMAGE_DIR, str(user_id))
        os.makedirs(save_dir, exist_ok=True)
        filepath = os.path.join(save_dir, filename)
        # upload image
        try:
            file_handle.save_file(image_data, filepath)
        except Exception as err:
            print("Error when save file " + filepath)
            print(err)
            return None
        # update in db
        try:
            created = IdentityImages(path=filepath, user=user_id)
            created.save(force_insert=True)
        except Exception as err:
            file_handle.delete_file(filepath)
            return None
        return created

    @staticmethod
    def remove_identity_image(image_id: int, user_id: int = None):
        image = IdentityImages.get_or_none(image_id)
        if image is None:
            raise ValueError("Ảnh không tồn tại")
        if user_id is not None and image.user.ID != user_id:
            raise ValueError("Bạn không có quyền xóa ảnh này")
        path = image.path
        image.delete_instance()
        # todo: Delete identity image

    @staticmethod
    def approve_image(image_id: int):
        IdentityImages.update({"approve": True}).where(IdentityImages.ID == image_id).execute()

    @staticmethod
    def reject_image(image_id: int):
        IdentityImages.update({"approve": False}).where(IdentityImages.ID == image_id).execute()
