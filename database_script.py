from database_connection import db
from models.Group import *
from models.Event import *
from models.User import *
from models.Location import *
from models.Manager import *
from datetime import datetime


def init_table(database: SqliteDatabase):
    database.create_tables(
        [User, Manager, IdentityImages, Group, JoinGroup,
         Location, Event, CheckinImage, LimitGroup, RegisterEvent, EventDetail]
    )


def seed_data():
    # Delete all
    User.delete().where(True).execute()
    Group.delete().where(True).execute()
    Location.delete().where(True).execute()
    Event.delete().where(True).execute()
    # Seed user
    u1 = User.create(
        fullname="Nguyễn Văn A",
        date_of_birth=datetime.fromisocalendar(2001, 1, 1),
        student_id="102190001",
        phone="0123456789",
        username="102190001",
        password="123456789"
    )
    u1.update_password("102190001")

    u2 = User.create(
        fullname="Nguyễn Văn B",
        date_of_birth=datetime.fromisocalendar(2001, 5, 1),
        student_id="102190002",
        phone="1123456789",
        username="102190002",
        password="123456789"
    )
    u2.update_password("102190002")

    u3 = User.create(
        fullname="Nguyễn Văn C",
        date_of_birth=datetime.fromisocalendar(2001, 9, 1),
        student_id="102190003",
        phone="2123456789",
        username="102190003",
        password="123456789"
    )
    u3.update_password("102190003")
    # Group
    g1 = Group.create(name="CNTT", require_approve=True, code="KHOA")
    g2 = Group.create(name="DTVT", require_approve=True, code="KHOA")
    g3 = Group.create(name="19TCLC_DT1", require_approve=False)
    g4 = Group.create(name="19TCLC_DT2", require_approve=False)

    # Manager
    m1 = Manager.create(fullname="Thầy A", is_admin=True, username="admin", password="admin")
    m1.update_password("admin")
    m2 = Manager.create(fullname="Thầy B", is_admin=False, username="no_admin", password="no_admin")
    m2.update_password("no_admin")

    # Location
    l1 = Location.create(name="Toa nha khu H", longitude=1.5, latitude="2.5", radius="20")

    # Event
    e1 = Event.create(
        title="Khai giảng khóa 2021-2022",
        place="Tòa nhà H",
        location=l1,
        start_at=datetime.now(),
        stop_at=datetime.now()
    )

    ed1 = EventDetail.create(
        event=e1,
        description="Mo ta cho su kien khai gian"
    )

    e2 = Event.create(
        title="Văn nghệ chào mừng",
        place="Sân BK",
        start_at=datetime.now(),
        stop_at=datetime.now()
    )

    ed2 = EventDetail.create(
        event=e2,
        description="Mo ta cho su kien van nghe"
    )


if __name__ == "__main__":
    # create db
    init_table(db)
    # seed data
    seed_data()
    # end
    db.close()
