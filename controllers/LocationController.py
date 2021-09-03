from config import USER_IN_PAGE
from models.Location import Location


class LocationController:
    @staticmethod
    def get_by_id(location_id: int) -> Location:
        return Location.get_or_none(ID=location_id)

    @staticmethod
    def search(keyword: str = "", page: int = None) -> list:
        search_results = Location.select().where(
            (Location.name.contains(keyword))
        )
        if page:
            return list(search_results.paginate(page, USER_IN_PAGE))
        else:
            return list(search_results)

    @staticmethod
    def update(location_id: int, detail: dict) -> Location:
        Location.update(**detail).where(Location.ID == location_id).execute()
        return Location.get_or_none(location_id)

    @staticmethod
    def create(detail: dict) -> Location:
        # create location
        location = Location.create(**detail)
        return location

    @staticmethod
    def delete(location_id: int):
        Location.delete().where(Location.ID == location_id).execute()





