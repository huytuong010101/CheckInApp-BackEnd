from jose import JWTError, jwt
from passlib.context import CryptContext
import config
from datetime import datetime, timedelta
from typing import Optional, Union
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from pydantics.Token import TokenData, Token
from models.User import User
from models.Manager import Manager

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth")
credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
)
not_permission_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not allow with your role",
        headers={"WWW-Authenticate": "Bearer"},
)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str) -> User:
    user = User.get_or_none(username=username)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def authenticate_manager(username: str, password: str) -> Manager:
    user = Manager.get_or_none(username=username)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def create_access_token(user: Union[User, Manager]):
    data = {
        "ID": user.ID,
        "fullname": user.fullname,
    }
    if type(user) == User:
        data["role"] = "student"
    else:
        data["role"] = "admin" if user.is_admin else "manager"
    expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expire})
    encoded_jwt = jwt.encode(data, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt


async def allow_student(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        if payload.get("ID") is None:
            raise credentials_exception
        if payload.get("role") != "student":
            raise not_permission_exception
        token_data = TokenData(**payload)
    except JWTError:
        raise credentials_exception
    return token_data


async def allow_manager(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        if payload.get("ID") is None:
            raise credentials_exception
        role = payload.get("role")
        if role != "manager" and role != "admin":
            raise not_permission_exception
        token_data = TokenData(**payload)
    except JWTError:
        raise credentials_exception
    return token_data


async def allow_admin(user: TokenData = Depends(allow_manager)):
    if user.role != "admin":
        raise not_permission_exception
    return user


async def allow_any_role(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        if payload.get("ID") is None:
            raise credentials_exception
        token_data = TokenData(**payload)
    except JWTError:
        raise credentials_exception
    return token_data

