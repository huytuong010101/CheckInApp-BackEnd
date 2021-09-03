class BaseController:
    @staticmethod
    def get_by_id(object_id: int):
        pass

    @staticmethod
    def search(keyword: str = "", page: int = None) -> list:
        pass

    @staticmethod
    def update(object_id: int, detail: dict):
        pass

    @staticmethod
    def create(detail: dict):
        pass

    @staticmethod
    def delete(object_id: int):
        pass
