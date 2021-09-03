from typing import List, Optional

from fastapi import APIRouter, HTTPException, status, Depends

from controllers.EventController import EventController
from pydantics.Event import EventIn, EventOut, EventOutDetail, EventUpdate, EventDetailUpdate, EventParticipant\
    , EventOfUser, EventRegister, Feedback
from pydantics.Token import TokenData
from utils import error_messages
from utils.auth_util import allow_manager, allow_any_role, allow_student

event_router = APIRouter(prefix="/events", tags=["events"])


@event_router.get("/", response_model=List[EventOut], status_code=status.HTTP_200_OK)
async def get_events(
        keyword: Optional[str] = "",
        page: Optional[int] = None,
        current_user: TokenData = Depends(allow_any_role)
):
    """
        Role:  Student + Manager.
        Function: Get all event
    """
    try:
        events = EventController.search(
            keyword=keyword,
            page=page)
    except Exception as err:
        print(">> Error when get events:" + str(err))
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return events


@event_router.get("/of-user/{user_id}", response_model=List[EventOfUser], status_code=status.HTTP_200_OK)
async def get_events_of_user(user_id: int, current_user: TokenData = Depends(allow_manager)):
    """
        Role: Manager.
        Function:  Get all event which user registered
    """
    try:
        events = EventController.get_event_of_user(user_id)
    except Exception as err:
        print(">> Error when get event of user")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return events


@event_router.get("/of-user", response_model=List[EventOfUser], status_code=status.HTTP_200_OK)
async def get_my_events(current_user: TokenData = Depends(allow_student)):
    """
        Role:  Student.
        Function: Get all events which current user registerd
    """
    try:
        events = EventController.get_event_of_user(current_user.ID)
    except Exception as err:
        print(">> Error when get event of user")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return events


@event_router.get("/{event_id}", response_model=EventOutDetail, status_code=status.HTTP_200_OK)
async def get_event(event_id: int, current_user: TokenData = Depends(allow_any_role)):
    """
        Role:  Student + Manager.
        Function: Get detail of event
    """
    try:
        event = EventController.get_by_id(event_id)
    except Exception as err:
        print(">> Error when get event")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    if event is None:
        raise HTTPException(status_code=404)
    return EventOutDetail.from_orm_load(event)


@event_router.get("/{event_id}/register-status", response_model=EventRegister, status_code=status.HTTP_200_OK)
async def get_events_of_user(event_id: int, current_user: TokenData = Depends(allow_student)):
    """
        Role: student.
        Function: get register status of current user for event
    """
    user_id = current_user.ID
    try:
        events = EventController.get_event_of_user(user_id, event_id)
    except Exception as err:
        print(">> Error when get event of user")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    if events:
        return events[0]
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)


@event_router.get("/{event_id}/participants", response_model=List[EventParticipant], status_code=status.HTTP_200_OK)
async def get_participants(event_id: int, current_user: TokenData = Depends(allow_any_role)):
    """
        Role:  Student + Manager.
        Function: Get all student who registered an event
    """
    try:
        participants = EventController.get_participants(event_id)
    except Exception as err:
        print(">> Error when get participants")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return participants


@event_router.post("/", response_model=EventOut, status_code=status.HTTP_201_CREATED)
async def create_event(event: EventIn, current_user: TokenData = Depends(allow_manager)):
    """
        Role:  Manager.
        Function: create a event
    """
    event.created_by = current_user.ID
    try:
        created_event = EventController.create(event.dict())
    except Exception as err:
        print(">> Error when create event")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return created_event


@event_router.post("/{event_id}/register", status_code=status.HTTP_200_OK)
async def register_event(event_id: int, current_user: TokenData = Depends(allow_student)):
    """
        Role:  Student.
        Function: Register an event for current user
    """
    try:
        EventController.register_event(event_id=event_id, user_id=current_user.ID)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))
    except Exception as err:
        print(">> Error when register event")
        print(err)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_messages.DATABASE_ERROR)
    return {"success": True}


@event_router.post("/{event_id}/register/{user_id}", status_code=status.HTTP_200_OK)
async def add_participant(event_id: int, user_id: int, current_user: TokenData = Depends(allow_manager)):
    """
        Role: Manager.
        Function: Register an event for special user
    """
    try:
        EventController.register_event(event_id=event_id, user_id=user_id, add_by=current_user.ID)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))
    except Exception as err:
        print(">> Error when register event")
        print(err)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_messages.DATABASE_ERROR)
    return {"success": True}


@event_router.put("/{event_id}", response_model=EventOut, status_code=status.HTTP_200_OK)
async def update_event(
        event_id: int,
        detail: Optional[EventDetailUpdate] = None,
        event: Optional[EventUpdate] = None,
        current_user: TokenData = Depends(allow_manager)
):
    """
        Role:  Manager.
        Function: Update an event
    """
    # to dict
    detail = detail.dict(exclude_unset=True) if detail else {}
    event = event.dict(exclude_unset=True) if event else {}
    try:
        updated_event = EventController.update(event_id, event, detail)
    except Exception as err:
        print("Error when update event")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    if updated_event is None:
        raise HTTPException(status_code=404, detail=error_messages.USER_NOT_FOUND)
    return updated_event


@event_router.put("/{event_id}/unregister", status_code=status.HTTP_200_OK)
async def unregister_event_for_user(event_id: int, current_user: TokenData = Depends(allow_student)):
    """
        Role: Student.
        Function: Unregister an event for current event
    """
    try:
        EventController.unregister_event(event_id=event_id, user_id=current_user.ID)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))
    except Exception as err:
        print(">> Error when register event")
        print(err)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_messages.DATABASE_ERROR)
    return {"success": True}


@event_router.put("/{event_id}/unregister/{user_id}", status_code=status.HTTP_200_OK)
async def register_event(event_id: int, user_id: int, current_user: TokenData = Depends(allow_manager)):
    """
        Role:  Manager.
        Function: Unregister an event for special user
    """
    try:
        EventController.unregister_event(event_id=event_id, user_id=current_user.ID)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))
    except Exception as err:
        print(">> Error when register event")
        print(err)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_messages.DATABASE_ERROR)
    return {"success": True}


@event_router.put("/{event_id}/feedback", status_code=status.HTTP_200_OK)
async def feedback_event(event_id: int, feedback: Feedback, current_user: TokenData = Depends(allow_student)):
    """
        Role:   Student.
        Function: Feedback to an event which registered
    """
    try:
        EventController.feedback(event_id=event_id, user_id=current_user.ID, content=feedback.content)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))
    except Exception as err:
        print(">> Error when feedback event")
        print(err)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_messages.DATABASE_ERROR)
    return {"success": True}


@event_router.put("/{event_id}/block-user/{user_id}", status_code=status.HTTP_200_OK)
async def block_register(
        event_id: int,
        user_id: int,
        feedback: Feedback,
        current_user: TokenData = Depends(allow_manager)
):
    """
        Role:  Manager.
        Function: Block a special user for register an event
    """
    try:
        EventController.block(event_id=event_id, user_id=user_id, note=feedback.content)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))
    except Exception as err:
        print(">> Error when feedback event")
        print(err)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_messages.DATABASE_ERROR)
    return {"success": True}


@event_router.put("/{event_id}/add-group/{group_id}", status_code=status.HTTP_200_OK)
async def add_group_to_event(
        event_id: int, group_id: int,
        current_user: TokenData = Depends(allow_manager)
):
    """
        Role: Manager.
        Function: add a group whose member can register special event
    """
    try:
        EventController.add_limit_group(event_id, group_id)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))
    except Exception as err:
        print(">> Error when add group to event")
        print(err)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_messages.DATABASE_ERROR)
    return {"success": True}


@event_router.put("/{event_id}/remove-group/{group_id}", status_code=status.HTTP_200_OK)
async def add_group_to_event(
        event_id: int, group_id: int,
        current_user: TokenData = Depends(allow_manager)
):
    """
        Role:  Manager.
        Function: Remove a group whose member can register special event
    """
    try:
        EventController.remove_limit_group(event_id, group_id)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))
    except Exception as err:
        print(">> Error when remove group to event")
        print(err)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=error_messages.DATABASE_ERROR)
    return {"success": True}


@event_router.delete("/{event_id}", status_code=status.HTTP_200_OK)
async def delete_event(event_id: int, current_user: TokenData = Depends(allow_manager)):
    """
        Role:  Manager.
        Function: Delete an event
    """
    try:
        EventController.delete(event_id)
    except Exception as err:
        print("Error when delete event")
        print(err)
        raise HTTPException(status_code=500, detail=error_messages.DATABASE_ERROR)
    return {"success": True}


