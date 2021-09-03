from fastapi import APIRouter, status, HTTPException, Depends, UploadFile, File
from pydantics.Manager import ManagerIn, ManageOut, ManagerUpdate
from typing import List, Optional
from controllers.ManagerController import ManagerController
from utils import error_messages
from utils.user_validator import validate_manager_before_update
from pydantics.Password import Password, SinglePassword
from pydantics.Image import ImageURLOut
from utils.auth_util import allow_manager, allow_admin
from pydantics.Token import TokenData
from config import AVATAR_LIMIT_KB


manager_router = APIRouter(prefix="/managers", tags=["managers"])


@manager_router.get("/", response_model=List[ManageOut], status_code=status.HTTP_200_OK)
async def read_managers(
    current_user: TokenData = Depends(allow_admin),
    fullname: Optional[str] = "",
    phone: Optional[str] = "",
    username: Optional[str] = "",
    page: Optional[int] = "",
):
    """
        Role:  Admin.
        Function: Get all managers
    """
    try:
        users = ManagerController.search(
            fullname=fullname,
            phone=phone,
            username=username,
            page=page)
    except Exception as err:
        print(">> Error when get managers:" + str(err))
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return users


@manager_router.get("/profile", response_model=ManageOut, status_code=status.HTTP_200_OK)
async def read_profile(current_user: TokenData = Depends(allow_manager)):
    """
        Role:  Manager.
        Function: Get profile of current user
    """
    try:
        user = ManagerController.get_by_id(current_user.ID)
    except Exception as err:
        print(">> Error when get profile")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    if user is None:
        raise HTTPException(status_code=404, detail=error_messages.USER_NOT_FOUND)
    return user


@manager_router.get("/{user_id}", response_model=ManageOut, status_code=status.HTTP_200_OK)
async def read_manager(user_id: int, current_user: TokenData = Depends(allow_admin)):
    """
        Role:  Admin.
        Function: Get detail of special manager
    """
    try:
        user = ManagerController.get_by_id(user_id)
    except Exception as err:
        print(">> Error when get manager")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    if user is None:
        raise HTTPException(status_code=404, detail=error_messages.USER_NOT_FOUND)
    return user


@manager_router.post("/", response_model=ManageOut, status_code=status.HTTP_201_CREATED)
async def create_manager(user: ManagerIn, current_user: TokenData = Depends(allow_admin)):
    """
        Role:  Admin.
        Function: Create a manager
    """
    try:
        created_user = ManagerController.create(user.dict())
    except Exception as err:
        print(">> Error when create manager")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return created_user


@manager_router.put("/", response_model=ManageOut, status_code=status.HTTP_200_OK)
async def update_profile(user_id: int, detail: ManagerUpdate, current_user: TokenData = Depends(allow_manager)):
    """
        Role:  Manager.
        Function: Update profile of current user
    """
    user_id = current_user.ID
    # to dict
    origin_dict = detail.dict(exclude_unset=True)
    # validate in db
    errors = validate_manager_before_update(user_id, origin_dict)
    if errors:
        detail = []
        for loc, error in errors.items():
            detail.append({
                "loc": [loc],
                "msg": error,
                "type": "value_error"
            })
        raise HTTPException(status_code=422, detail=detail)
    try:
        user = ManagerController.update(user_id, origin_dict)
    except Exception as err:
        print("Error when update user")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    if user is None:
        raise HTTPException(status_code=404, detail=error_messages.USER_NOT_FOUND)
    return user


@manager_router.put("/update-avatar", response_model=ImageURLOut, status_code=status.HTTP_200_OK)
async def update_avatar(file: UploadFile = File(...), current_user: TokenData = Depends(allow_manager)):
    """
        Role:  Manager.
        Function: Update avatar of current user
    """
    data = await file.read()
    # limit size
    if len(data) / 1000 > AVATAR_LIMIT_KB:
        raise HTTPException(status_code=422, detail="Vui lòng chọn ảnh < " + AVATAR_LIMIT_KB + "KB")
    # upload
    try:
        uploaded_url = ManagerController.update_avatar(user_id=current_user.ID, image_data=data)
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err))
    except Exception as err:
        print(">> Error when update avatar manager")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    if not uploaded_url:
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return ImageURLOut(url=uploaded_url)


@manager_router.put("/{user_id}", response_model=ManageOut, status_code=status.HTTP_200_OK)
async def update_manager(user_id: int, detail: ManagerUpdate, current_user: TokenData = Depends(allow_admin)):
    """
        Role:  Admin.
        Function: Update profile of special manager
    """
    # to dict
    origin_dict = detail.dict(exclude_unset=True)
    # validate in db
    errors = validate_manager_before_update(user_id, origin_dict)
    if errors:
        detail = []
        for loc, error in errors.items():
            detail.append({
                "loc": [loc],
                "msg": error,
                "type": "value_error"
            })
        raise HTTPException(status_code=422, detail=detail)
    try:
        user = ManagerController.update(user_id, origin_dict)
    except Exception as err:
        print("Error when update user")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    if user is None:
        raise HTTPException(status_code=404, detail=error_messages.USER_NOT_FOUND)
    return user


@manager_router.put("/{user_id}/change-password", status_code=status.HTTP_200_OK)
async def change_password(user_id: int, password: SinglePassword, current_user: TokenData = Depends(allow_admin)):
    """
        Role:  Admin.
        Function: Change password of special manager
    """
    try:
        ManagerController.force_change_password(user_id, password)
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err))
    except Exception as err:
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return {"success": True}


@manager_router.put("/change-password", status_code=status.HTTP_200_OK)
async def change_password(password: Password, current_user: TokenData = Depends(allow_manager)):
    """
        Role:  Manager.
        Function: Change password of current user
    """
    user_id = current_user.ID
    try:
        ManagerController.change_password(user_id, password.old_password, password.new_password)
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err))
    except Exception as err:
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return {"success": True}
