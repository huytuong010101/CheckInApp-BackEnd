from datetime import datetime
from config import AVATAR_LIMIT_KB
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from fastapi.responses import FileResponse
from utils import error_messages
from pydantics.IdentityImage import IdentityImage, IdentityImageNoUser
from typing import Optional, List
from controllers.IdentityImageController import IdentityImageController
from utils.auth_util import allow_manager, allow_student, allow_any_role
from pydantics.Token import TokenData


identity_image_router = APIRouter(prefix="/identity-images", tags=["identity-images"])


@identity_image_router.get("/", response_model=List[IdentityImage], status_code=status.HTTP_200_OK)
async def get_identity_images(
        user_id: Optional[int] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        page: Optional[int] = None,
        current_user: TokenData = Depends(allow_manager)
):
    """
        Role:  Manager.
        Function: Get all identity image
    """
    try:
        images = IdentityImageController.get_identity_images(
            user_id=user_id,
            from_date=from_date,
            to_date=to_date,
            page=page)
    except Exception as err:
        print(">> Error when get identity image:" + str(err))
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return images


@identity_image_router.get("/of-user", response_model=List[IdentityImageNoUser], status_code=status.HTTP_200_OK)
async def get_identity_images_of_user(
        current_user: TokenData = Depends(allow_student)
):
    """
        Role:  Student.
        Function: Get all identity image of current user
    """
    try:
        images = IdentityImageController.get_identity_images(user_id=current_user.ID)
    except Exception as err:
        print(">> Error when get identity image of user:" + str(err))
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return images


@identity_image_router.get("/{image_id}", response_class=FileResponse, status_code=status.HTTP_200_OK)
async def get_identity_image(
        image_id: int,
        current_user: TokenData = Depends(allow_any_role)
):
    """
        Role:  Student + Manager.
        Function: Render an image
    """
    user_id = current_user.ID if current_user.role == "student" else None
    try:
        path = IdentityImageController.get_image_path(image_id=image_id, user_id=user_id)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))
    except Exception as err:
        print(">> Error when get path identity image of user:" + str(err))
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    if path is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return FileResponse(path)


@identity_image_router.post("/", response_model=IdentityImageNoUser, status_code=status.HTTP_201_CREATED)
async def add_identity_images(
        file: UploadFile = File(...),
        current_user: TokenData = Depends(allow_student)
):
    """
        Role:  Student.
        Function: Add an identity image for current user
    """
    data = await file.read()
    # limit size
    if len(data) / 1000 > AVATAR_LIMIT_KB:
        raise HTTPException(status_code=422, detail="Vui lòng chọn ảnh < " + str(AVATAR_LIMIT_KB) + "KB")
    # upload
    try:
        result = IdentityImageController.add_identity_image(user_id=current_user.ID, image_data=data)
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err))
    except Exception as err:
        print(">> Error when add identity image")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    if not result:
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return result


@identity_image_router.delete("/{image_id}", status_code=status.HTTP_200_OK)
async def remove_identity_images(
        image_id: int,
        current_user: TokenData = Depends(allow_any_role)
):
    """
        Role:  Student+ Manager.
        Function: Remove an identity image
    """
    user_id = current_user.ID if current_user.role == "student" else None
    try:
        IdentityImageController.remove_identity_image(image_id=image_id, user_id=user_id)
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err))
    except Exception as err:
        print(">> Error when remove identity image")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return {"success": True}


@identity_image_router.put("/{image_id}/approve", status_code=status.HTTP_200_OK)
async def approve_identity_images(
        image_id: int,
        current_user: TokenData = Depends(allow_manager)
):
    """
        Role:  Manager.
        Function: Approve an identity image
    """
    try:
        IdentityImageController.approve_image(image_id=image_id)
    except Exception as err:
        print(">> Error when approve identity image")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return {"success": True}


@identity_image_router.put("/{image_id}/reject", status_code=status.HTTP_200_OK)
async def reject_identity_images(
        image_id: int,
        current_user: TokenData = Depends(allow_manager)
):
    """
        Role:  Manager.
        Function: Reject an identity image
    """
    try:
        IdentityImageController.reject_image(image_id=image_id)
    except Exception as err:
        print(">> Error when reject identity image")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return {"success": True}


