from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from utils.auth_util import authenticate_user, authenticate_manager, create_access_token
from pydantics.Login import LoginForm, LoginMode

authentication_router = APIRouter(prefix="/auth", tags=["authentication"])


@authentication_router.post("/")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # login as manager
    student = authenticate_manager(form_data.username, form_data.password)
    # login as student
    manager = authenticate_user(form_data.username, form_data.password)
    user = student if student else manager
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sai tên đăng nhập hoặc mật khẩu",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(user)
    return {"access_token": access_token, "token_type": "bearer"}

