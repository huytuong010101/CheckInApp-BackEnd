
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from typing import Optional, List
from controllers.CheckinController import CheckinController
from utils.auth_util import allow_manager, allow_student, allow_any_role
from pydantics.Token import TokenData
from pydantics.Checkin import CheckIn, CheckInNoEvent, CheckInNoUser
from utils import error_messages

checkin_router = APIRouter(prefix="/checkin", tags=["checkin"])


@checkin_router.get("/", response_model=List[CheckIn], status_code=status.HTTP_200_OK)
async def get_checkins(
        user_id: Optional[int] = None,
        event_id: Optional[int] = None,
        page: Optional[int] = None,
        num_in_page: Optional[int] = 10,
        current_user: TokenData = Depends(allow_manager)
):
    """
    Role: Manager.
    Function: Get all check in
    """
    try:
        results = CheckinController.get_checkins(user_id=user_id, event_id=event_id, page=page, num_in_page=num_in_page)
    except Exception as err:
        print("> Error when get checkins")
        print(err)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_messages.DATABASE_ERROR)
    return results


@checkin_router.get("/of-user", response_model=List[CheckInNoUser], status_code=status.HTTP_200_OK)
async def get_checkins_of_user(
        event_id: Optional[int] = None,
        page: Optional[int] = None,
        num_in_page: Optional[int] = 10,
        current_user: TokenData = Depends(allow_student)
):
    """
    Role: Student.
    Function: Get all check in of current user
    """
    try:
        results = CheckinController.get_checkins(
            user_id=current_user.ID,
            event_id=event_id, page=page,
            num_in_page=num_in_page
        )
    except Exception as err:
        print("> Error when get checkins of user")
        print(err)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_messages.DATABASE_ERROR)
    return results


@checkin_router.post("/of-event/{event-id}", response_model=CheckInNoUser, status_code=status.HTTP_201_CREATED)
async def check_in(
        event_id: Optional[int] = None,
        file: UploadFile = File(...),
        current_user: TokenData = Depends(allow_student)
):
    """
        Role: Student.
        Function: Student check in an event with face image
    """
    data = await file.read()
    try:
        created = CheckinController.checkin(current_user.ID, event_id, data)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))
    except Exception as err:
        print("> Error when check in")
        print(err)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_messages.DATABASE_ERROR)
    return created

