from models.User import User
from models.Manager import Manager


def validate_user_before_update(user_id: int, detail: dict) -> dict:
    errors = {}
    # check student_id í unique
    if detail.get("student_id") \
            and User.select().where((User.ID != user_id) & (User.student_id == detail["student_id"])).exists():
        errors["student_id"] = "Mã sinh viên đã được đăng ký"
    # check phone is unique
    if detail.get("phone") and User.select().where((User.ID != user_id) & (User.phone == detail["phone"])).exists():
        errors["phone"] = "Số điện thoại đã được đăng ký"
    # check ì username is unique
    if detail.get("username") \
            and User.select().where((User.ID != user_id) & (User.username == detail["username"])).exists():
        errors["username"] = "Tên đã khoản đã được sử dụng"
    return errors


def validate_manager_before_update(user_id: int, detail: dict) -> dict:
    errors = {}
    # check phone is unique
    if detail.get("phone")\
            and Manager.select().where((Manager.ID != user_id) & (Manager.phone == detail["phone"])).exists():
        errors["phone"] = "Số điện thoại đã được đăng ký"
    # check if username is unique
    if detail.get("username") \
            and Manager.select().where((Manager.ID != user_id) & (Manager.username == detail["username"])).exists():
        errors["username"] = "Tên đã khoản đã được sử dụng"
    return errors
