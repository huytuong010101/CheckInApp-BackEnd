from models.Event import CheckinImage, Event
from datetime import datetime
from config import CHECKIN_IMAGE_DIR
import uuid
import os
from utils import file_handle


class CheckinController:
    @staticmethod
    def get_checkins(user_id: int = None, event_id: int = None, page: int = None, num_in_page: int = 10):
        search_results = CheckinImage.select().where(
            ((user_id is None) | (CheckinImage.user == user_id))
            & ((event_id is None) | (CheckinImage.event == event_id))
        )
        if page:
            return list(search_results.paginate(page, num_in_page))
        else:
            return list(search_results)

    @staticmethod
    def checkin(user_id: int, event_id: int, image_data: str) -> CheckinImage:
        # check event_id
        if Event.get_or_none(event_id) is None:
            raise ValueError("Sự kiện không còn tồn tại")
        # validate
        valid, error = CheckinImage.valid_to_checkin(user_id, event_id)
        print(valid, error)
        if not valid:
            raise ValueError(error)
        # prepare
        now = datetime.now().strftime("%Y-%m-%d.%H-%M-%S")
        filename = f"student_{user_id}.event_{event_id}.{uuid.uuid4()}.{now}.jpg"
        save_dir = os.path.join(CHECKIN_IMAGE_DIR, str(user_id))
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
            created = CheckinImage(path=filepath, user=user_id, event=event_id)
            created.save(force_insert=True)
        except Exception as err:
            file_handle.delete_file(filepath)
            return None
        return created

