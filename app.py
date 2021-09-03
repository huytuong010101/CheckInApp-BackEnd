from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import user, authentication, event, location, manager, group, identity_image, checkin


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(user.user_router)
app.include_router(event.event_router)
app.include_router(location.location_router)
app.include_router(identity_image.identity_image_router)
app.include_router(checkin.checkin_router)
app.include_router(group.group_router)
app.include_router(manager.manager_router)
app.include_router(authentication.authentication_router)
