from fastapi import APIRouter, HTTPException, status, Depends
from utils import error_messages
from pydantics.Location import LocationOut, LocationIn, LocationUpdate
from typing import Optional, List
from controllers.LocationController import LocationController
from utils.auth_util import allow_manager
from pydantics.Token import TokenData

location_router = APIRouter(prefix="/locations", tags=["locations"])


@location_router.get("/", response_model=List[LocationOut], status_code=status.HTTP_200_OK)
async def get_locations(
        keyword: Optional[str] = "",
        page: Optional[int] = None,
        current_user: TokenData = Depends(allow_manager)
):
    """
        Role:  Manager.
        Function: Get all location
    """
    try:
        locations = LocationController.search(
            keyword=keyword,
            page=page)
    except Exception as err:
        print(">> Error when get location:" + str(err))
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return locations


@location_router.get("/{location_id}", response_model=LocationOut, status_code=status.HTTP_200_OK)
async def get_location(location_id: int, current_user: TokenData = Depends(allow_manager)):
    """
        Role:  Manager.
        Function: Get location detail
    """
    try:
        location = LocationController.get_by_id(location_id)
    except Exception as err:
        print(">> Error when get location")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    if location is None:
        raise HTTPException(status_code=404, detail=error_messages.USER_NOT_FOUND)
    return location


@location_router.post("/", response_model=LocationOut, status_code=status.HTTP_201_CREATED)
async def create_location(detail: LocationIn, current_user: TokenData = Depends(allow_manager)):
    """
        Role:  Manager.
        Function: Create a location
    """
    try:
        created_location = LocationController.create(detail.dict())
    except Exception as err:
        print(">> Error when create location")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return created_location


@location_router.put("/{location_id}", response_model=LocationOut, status_code=status.HTTP_200_OK)
async def update_location(location_id: int, detail: LocationUpdate, current_user: TokenData = Depends(allow_manager)):
    """
        Role:  Manager.
        Function: Update a location
    """
    # to dict
    detail = detail.dict(exclude_unset=True)
    try:
        updated_location = LocationController.update(location_id, detail)
    except Exception as err:
        print("Error when update location")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    if updated_location is None:
        raise HTTPException(status_code=404, detail=error_messages.USER_NOT_FOUND)
    return updated_location


@location_router.delete("/{location_id}", status_code=status.HTTP_200_OK)
async def delete_location(location_id: int, current_user: TokenData = Depends(allow_manager)):
    """
        Role:  Manager.
        Function: Delete a location
    """
    try:
        LocationController.delete(location_id)
    except Exception as err:
        print("Error when delete location")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return {"success": True}



