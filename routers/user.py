from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from typing import List, Optional

from controllers.GroupController import GroupController
from pydantics.Group import GroupOfMember
from pydantics.User import UserIn, UserOut, UserUpdate
from pydantics.Password import Password
from controllers.UserController import UserController
from utils import error_messages
from utils.user_validator import validate_user_before_update
from utils.auth_util import allow_student, allow_manager, allow_admin
from pydantics.Token import TokenData
from pydantics.Image import ImageURLOut
from config import AVATAR_LIMIT_KB

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.get("/", response_model=List[UserOut], status_code=status.HTTP_200_OK)
async def get_users(
        fullname: Optional[str] = "",
        student_id: Optional[str] = "",
        phone: Optional[str] = "",
        username: Optional[str] = "",
        page: Optional[int] = "",
        current_user: TokenData = Depends(allow_manager)
):
    """
        Role:  Manager.
        Function: Get all students
    """
    try:
        users = UserController.search(
            fullname=fullname,
            student_id=student_id,
            phone=phone,
            username=username,
            page=page)
    except Exception as err:
        print(">> Error when get users:" + str(err))
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return users


@user_router.get("/profile", response_model=UserOut, status_code=status.HTTP_200_OK)
async def get_my_user(current_user: TokenData = Depends(allow_student)):
    """
        Role:  Student
        Function: Get profile of current user
    """
    try:
        user = UserController.get_by_id(current_user.ID)
    except Exception as err:
        print(">> Error when get profile")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    if user is None:
        raise HTTPException(status_code=404, detail=error_messages.USER_NOT_FOUND)
    return user


@user_router.get("/joined-groups", response_model=List[GroupOfMember], status_code=status.HTTP_200_OK)
async def get_group_of_user(current_user: TokenData = Depends(allow_student)):
    """
        Role:  Student.
        Function: Get all group which joined
    """
    try:
        group = GroupController.get_group_of_user(current_user.ID)
    except Exception as err:
        print(">> Error when get group")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    if group is None:
        raise HTTPException(status_code=404, detail=error_messages.USER_NOT_FOUND)
    return group


@user_router.get("/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
async def get_user(user_id: int, current_user: TokenData = Depends(allow_manager)):
    """
        Role:  Manager.
        Function: Get profile of special user
    """
    try:
        user = UserController.get_by_id(user_id)
    except Exception as err:
        print(">> Error when get user")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    if user is None:
        raise HTTPException(status_code=404, detail=error_messages.USER_NOT_FOUND)
    return user


@user_router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserIn):
    """
        Role:  Anyone.
        Function: Create a student account
    """
    try:
        created_user = UserController.create(user.dict())
    except Exception as err:
        print(">> Error when create user")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return created_user


@user_router.post("/join-group/{group_id}", status_code=status.HTTP_200_OK)
async def join_group(group_id: int, current_user: TokenData = Depends(allow_student)):
    """
        Role:  Student.
        Function: Join a group
    """
    try:
        UserController.join_group(current_user.ID, group_id)
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err))
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return {"success": True}


@user_router.put("/leave-group/{group_id}", status_code=status.HTTP_200_OK)
async def join_group(group_id: int, current_user: TokenData = Depends(allow_student)):
    """
        Role:  Student.
        Function: Leave a group for current user
    """
    try:
        GroupController.remove_member(group_id, current_user.ID)
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err))
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return {"success": True}


@user_router.put("/", response_model=UserOut, status_code=status.HTTP_200_OK)
async def update_my_user(detail: UserUpdate, current_user: TokenData = Depends(allow_student)):
    """
        Role:  Student.
        Function: Update profile of current user
    """
    user_id = current_user.ID
    # to dict
    origin_dict = detail.dict(exclude_unset=True)
    # validate in db
    errors = validate_user_before_update(user_id, origin_dict)
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
        user = UserController.update(user_id, origin_dict)
    except Exception as err:
        print("Error when update user")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    if user is None:
        raise HTTPException(status_code=404, detail=error_messages.USER_NOT_FOUND)
    return user


@user_router.put("/change-password", status_code=status.HTTP_200_OK)
async def change_my_password(password: Password, current_user: TokenData = Depends(allow_student)):
    """
        Role:  Student.
        Function: Change password of current account
    """
    try:
        UserController.change_password(current_user.ID, password.old_password, password.new_password)
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err))
    except Exception as err:
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return {"success": True}


@user_router.put("/update-avatar", response_model=ImageURLOut, status_code=status.HTTP_200_OK)
async def update_avatar(file: UploadFile = File(...), current_user: TokenData = Depends(allow_student)):
    """
        Role:  Student.
        Function: Update avatar of current user
    """
    data = await file.read()
    # limit size
    if len(data) / 1000 > AVATAR_LIMIT_KB:
        raise HTTPException(status_code=422, detail="Vui lòng chọn ảnh < " + str(AVATAR_LIMIT_KB) + "KB")
    # upload
    try:
        uploaded_url = UserController.update_avatar(user_id=current_user.ID, image_data=data)
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err))
    except Exception as err:
        print(">> Error when update avatar user")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    if not uploaded_url:
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return ImageURLOut(url=uploaded_url)


@user_router.put("/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
async def update_user(user_id: int, detail: UserUpdate, current_user: TokenData = Depends(allow_manager)):
    """
        Role:  Manager.
        Function: Update profile of special user
    """
    # to dict
    origin_dict = detail.dict(exclude_unset=True)
    # validate in db
    errors = validate_user_before_update(user_id, origin_dict)
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
        user = UserController.update(user_id, origin_dict)
    except Exception as err:
        print("Error when update user")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    if user is None:
        raise HTTPException(status_code=404, detail=error_messages.USER_NOT_FOUND)
    return user


@user_router.put("/{user_id}/change-password", status_code=status.HTTP_200_OK)
async def change_password(user_id: int, password: Password, current_user: TokenData = Depends(allow_manager)):
    """
        Role:  Manager.
        Function: Change password of special user
    """
    try:
        UserController.change_password(user_id, password.old_password, password.new_password)
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err))
    except Exception as err:
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return {"success": True}


@user_router.delete("/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(user_id: int, current_user: TokenData = Depends(allow_admin)):
    """
        Role:  Admin.
        Function: Delete a user
    """
    try:
        UserController.delete(user_id)
    except Exception as err:
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return {"success": True}





