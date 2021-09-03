from fastapi import APIRouter, HTTPException, status, Depends
from utils import error_messages
from pydantics.Group import GroupIn, GroupOut, GroupUpdate, MemberInGroup, GroupOfMember
from typing import Optional, List
from controllers.GroupController import GroupController
from utils.auth_util import allow_manager, allow_any_role
from pydantics.Token import TokenData

group_router = APIRouter(prefix="/groups", tags=["group"])


@group_router.get("/", response_model=List[GroupOut], status_code=status.HTTP_200_OK)
async def get_group(
        keyword: Optional[str] = "",
        page: Optional[int] = None,
        current_user: TokenData = Depends(allow_any_role)
):
    """
        Role:  Student + Manager.
        Function: Get all group
    """
    try:
        groups = GroupController.search(
            keyword=keyword,
            page=page)
    except Exception as err:
        print(">> Error when get groups:" + str(err))
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return groups


@group_router.get("/of-user/{user_id}", response_model=List[GroupOfMember], status_code=status.HTTP_200_OK)
async def get_group_of_user(user_id: int, current_user: TokenData = Depends(allow_manager)):
    """
        Role:  Manager.
        Function: Get all group which user joined
    """
    try:
        group = GroupController.get_group_of_user(user_id)
    except Exception as err:
        print(">> Error when get group")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    if group is None:
        raise HTTPException(status_code=404, detail=error_messages.USER_NOT_FOUND)
    return group


@group_router.get("/{group_id}/members", response_model=List[MemberInGroup],  status_code=status.HTTP_200_OK)
async def get_members(group_id: int, current_user: TokenData = Depends(allow_any_role)):
    """
        Role:  Student + Manager.
        Function: Get all member of group
    """
    try:
        members = GroupController.get_member_in_group(group_id)
    except Exception as err:
        print("Error when get member group")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return members


@group_router.get("/{group_id}", response_model=GroupOut, status_code=status.HTTP_200_OK)
async def get_group(group_id: int, current_user: TokenData = Depends(allow_any_role)):
    """
        Role:  Student + Manager.
        Function: Get Group detail
    """
    try:
        group = GroupController.get_by_id(group_id)
    except Exception as err:
        print(">> Error when get group")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    if group is None:
        raise HTTPException(status_code=404, detail=error_messages.USER_NOT_FOUND)
    return group


@group_router.post("/", response_model=GroupOut, status_code=status.HTTP_201_CREATED)
async def create_group(detail: GroupIn, current_user: TokenData = Depends(allow_manager)):
    """
        Role:  Manager.
        Function: Create an group
    """
    try:
        created_group = GroupController.create(detail.dict())
    except Exception as err:
        print(">> Error when create group")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return created_group


@group_router.post("/{group_id}/add-member/{user_id}", status_code=status.HTTP_200_OK)
async def add_member(group_id: int, user_id: int, current_user: TokenData = Depends(allow_manager)):
    """
        Role:  Manager.
        Function: Add special user to group
    """
    try:
        GroupController.add_member(user_id=user_id, group_id=group_id, added_by=current_user.ID, approve=True)
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err))
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return {"success": True}


@group_router.put("/{group_id}/approve/{user_id}", status_code=status.HTTP_200_OK)
async def approve_member(group_id: int, user_id: int, current_user: TokenData = Depends(allow_manager)):
    """
        Role:  Manager.
        Function: Approve join group request
    """
    try:
        GroupController.approve_member(group_id, user_id)
    except Exception as err:
        print("Error when approve group")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return {"success": True}


@group_router.put("/{group_id}/reject/{user_id}", status_code=status.HTTP_200_OK)
async def reject_member(group_id: int, user_id: int, current_user: TokenData = Depends(allow_manager)):
    """
        Role:  Manager.
        Function: Reject an join request
    """
    try:
        GroupController.reject_member(group_id, user_id)
    except Exception as err:
        print("Error when reject group")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return {"success": True}


@group_router.put("/{group_id}/remove-member/{user_id}", status_code=status.HTTP_200_OK)
async def remove_member(group_id: int, user_id: int, current_user: TokenData = Depends(allow_manager)):
    """
        Role:  Manager.
        Function: Remove member from group
    """
    try:
        GroupController.remove_member(group_id, user_id)
    except Exception as err:
        print("Error when remove member")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return {"success": True}


@group_router.put("/{group_id}", response_model=GroupOut, status_code=status.HTTP_200_OK)
async def update_group(group_id: int, detail: GroupUpdate, current_user: TokenData = Depends(allow_manager)):
    """
        Role:  Manager.
        Function: Update a group information
    """
    # to dict
    detail = detail.dict(exclude_unset=True)
    try:
        updated_group = GroupController.update(group_id, detail)
    except Exception as err:
        print("Error when update group")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    if updated_group is None:
        raise HTTPException(status_code=404, detail=error_messages.USER_NOT_FOUND)
    return updated_group


@group_router.delete("/{group_id}", status_code=status.HTTP_200_OK)
async def delete_group(group_id: int, current_user: TokenData = Depends(allow_manager)):
    """
        Role:  Manager.
        Function: Delete a group
    """
    try:
        GroupController.delete(group_id)
    except Exception as err:
        print("Error when delete group")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return {"success": True}




