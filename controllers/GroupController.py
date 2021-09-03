from config import USER_IN_PAGE
from models.Group import Group, JoinGroup
from typing import List


class GroupController:
    @staticmethod
    def get_by_id(group_id: int) -> Group:
        return Group.get_or_none(ID=group_id)

    @staticmethod
    def search(keyword: str = "", page: int = None) -> list:
        search_results = Group.select().where(
            (Group.name.contains(keyword))
        )
        if page:
            return list(search_results.paginate(page, USER_IN_PAGE))
        else:
            return list(search_results)

    @staticmethod
    def update(group_id: int, detail: dict) -> Group:
        Group.update(**detail).where(Group.ID == group_id).execute()
        return Group.get_or_none(group_id)

    @staticmethod
    def create(detail: dict) -> Group:
        group = Group.create(**detail)
        return group

    @staticmethod
    def delete(group_id: int):
        Group.delete().where(Group.ID == group_id).execute()

    @staticmethod
    def get_member_in_group(group_id: int) -> List[JoinGroup]:
        return list(JoinGroup.select().where(JoinGroup.group == group_id))

    @staticmethod
    def get_group_of_user(user_id: int) -> List[JoinGroup]:
        return list(JoinGroup.select().where(JoinGroup.user == user_id))

    @staticmethod
    def add_member(user_id: int, group_id: int, added_by: int, approve: bool = True):
        group = Group.get_or_none(ID=group_id)
        if group is None:
            raise ValueError("Nhóm này không tồn tại")
        success, error = group.valid_to_join(user_id)
        if not success:
            raise ValueError(error)
        group.add_member(user=user_id, add_by=added_by, approve=approve)

    @staticmethod
    def remove_member(group_id: int, user_id: int):
        JoinGroup.delete().where((JoinGroup.group == group_id) & (JoinGroup.user == user_id)).execute()

    @staticmethod
    def approve_member(group_id: int, user_id: int):
        group = Group.get_or_none(ID=group_id)
        if group:
            group.approve_member(user_id)

    @staticmethod
    def reject_member(group_id: int, user_id: int):
        group = Group.get_or_none(ID=group_id)
        if group:
            group.reject_member(user_id)




