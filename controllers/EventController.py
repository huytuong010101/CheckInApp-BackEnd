from datetime import datetime
from models.Event import Event, EventDetail, RegisterEvent, LimitGroup
from config import USER_IN_PAGE
from typing import List
from peewee import fn, JOIN


class EventController:
    @staticmethod
    def get_by_id(event_id: int) -> Event:
        result = Event\
            .select(Event, fn.COUNT(RegisterEvent.user).alias('num_participant'))\
            .where(Event.ID == event_id)\
            .join(RegisterEvent,
                  JOIN.LEFT_OUTER,
                  on=((Event.ID == RegisterEvent.event) & (RegisterEvent.block == False)))\
            .group_by(Event.ID)\
            .first()
        return result

    @staticmethod
    def search(keyword: str = "", page: int = None) -> list:
        search_results = Event\
            .select(Event, fn.COUNT(RegisterEvent.user).alias('num_participant'))\
            .where((Event.title.contains(keyword)) | (Event.place.contains(keyword)))\
            .join(
                RegisterEvent,
                JOIN.LEFT_OUTER,
                on=((Event.ID == RegisterEvent.event) & (RegisterEvent.block == False)))\
            .group_by(Event.ID)
        if page:
            return list(search_results.paginate(page, USER_IN_PAGE))
        else:
            return list(search_results)

    @staticmethod
    def update(event_id: int, event_dict: dict, detail_dict: dict) -> Event:
        event_dict["updated_at"] = datetime.now()
        # update event
        if event_dict:
            Event.update(**event_dict).where(Event.ID == event_id).execute()
        # update detail
        if detail_dict:
            if EventDetail.get_or_none(EventDetail.event == event_id) is None:
                EventDetail.create(event=event_id, **detail_dict)
            else:
                EventDetail.update(**detail_dict).where(EventDetail.event == event_id).execute()
        return Event.get_or_none(event_id)

    @staticmethod
    def create(detail: dict) -> Event:
        # create event
        event = Event.create(**detail)
        # create detail event
        EventDetail.create(
            event=event,
            description=detail["description"],
            created_by=detail["created_by"],
            leader=detail["leader"]
        )
        # create limit
        if detail.get("limit_group"):
            limit_group = [{"event": event.ID, "group": group_id} for group_id in detail["limit_group"]]
            LimitGroup.insert_many(limit_group).execute()
        return event

    @staticmethod
    def delete(event_id: int):
        Event.delete().where(Event.ID == event_id).execute()

    @staticmethod
    def register_event(event_id: int, user_id: int, add_by: int = None, note: str = None):
        event = Event.get_or_none(ID=event_id)
        if not event:
            raise ValueError("Sự kiện không tồn tại")
        valid, error = event.valid_to_register(user_id)
        if not valid:
            raise ValueError(error)
        event.add_participant(user=user_id, add_by=add_by, note=note)

    @staticmethod
    def unregister_event(event_id: int, user_id: int):
        register = RegisterEvent.get_or_none((RegisterEvent.event == event_id) & (RegisterEvent.user == user_id))
        if not register:
            raise ValueError("Chưa đăng ký sự kiện này")
        if register.block:
            raise ValueError("Đã đã bị block nên không thể rời nhóm này")
        register.delete_instance()

    @staticmethod
    def get_participants(event_id: int) -> List[RegisterEvent]:
        return list(RegisterEvent.select().where(RegisterEvent.event == event_id))

    @staticmethod
    def get_event_of_user(user_id: int, event_id: int = None) -> List[RegisterEvent]:
        return list(
            RegisterEvent.select()
            .where((RegisterEvent.user == user_id) & ((event_id is None) | (RegisterEvent.event == event_id)))
        )

    @staticmethod
    def feedback(user_id: int, event_id: int, content: str):
        register = RegisterEvent.get_or_none(user=user_id, event=event_id)
        if not register:
            raise ValueError("Tài khoản chưa đăng ký sự kiện")
        if register.block:
            raise ValueError("Bạn đã bị chẳn block với sự kiện này")
        register.feedback = content
        register.save()

    @staticmethod
    def block(user_id: int, event_id: int, note: str):
        registered = RegisterEvent.get_or_none(event=event_id, user=user_id)
        if registered is None:
            registered = RegisterEvent.create(event=event_id, user=user_id)
        registered.block = True
        registered.save()

    @staticmethod
    def add_limit_group(event_id: int, group_id: int):
        event = Event.get_or_none(ID=event_id)
        if not event:
            raise ValueError("Sự kiện không tồn tại")
        event.add_group(group=group_id)

    @staticmethod
    def remove_limit_group(event_id: int, group_id: int):
        LimitGroup.delete().where((LimitGroup.event == event_id) & (LimitGroup.group == group_id)).execute()


