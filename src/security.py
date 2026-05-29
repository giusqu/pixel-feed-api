# Function related to users, autontication, jwt and backend things

import datetime
from typing import Annotated, Literal

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext

from src.database import database, user_table

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # get the token (user endpoint)


def create_credentials_exception(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def access_token_expire_minute() -> int:
    return 30


def confirm_token_expire_minute() -> int:
    return 1440


def create_access_token(email: str):  # or id to authenticate
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=access_token_expire_minute()
    )
    jwt_data = {"sub": email, "exp": expire, "type": "access"}
    encode_jwt = jwt.encode(jwt_data, key=SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt


def create_confirmation_token(email: str):  # or id to authenticate
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=confirm_token_expire_minute()
    )
    jwt_data = {"sub": email, "exp": expire, "type": "confirmation"}
    encode_jwt = jwt.encode(jwt_data, key=SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt


def get_subject_for_token_type(token: str, type: Literal["access", "confirmation"]) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    except ExpiredSignatureError:
        raise create_credentials_exception("Token expired")
    except JWTError:
        raise create_credentials_exception("Invalid token")

    email = payload.get("sub")
    if email is None:
        raise create_credentials_exception("Token is missing 'sub' field")

    token_type = payload.get("type")
    if token_type is None or token_type != type:
        raise create_credentials_exception(
            f"Incorrect token type: expected: {type} got: {token_type}"
        )

    return email


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def get_user(email: str):
    query = user_table.select().where(user_table.c.email == email)
    result = await database.fetch_one(query)
    if result:
        return result


async def authenticate_user(email: str, password: str):
    user = await get_user(email)
    if not user:
        raise create_credentials_exception("Invalid email or password")  # do not specify which one
    if not verify_password(password, user["password"]):
        raise create_credentials_exception("Invalid email or password")
    if not user.confirmed:
        raise create_credentials_exception("User has not confirmed email")
    return user


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    email = get_subject_for_token_type(token, "access")
    user = await get_user(email=email)
    if user is None:
        raise create_credentials_exception("User not found for this token")

    return user
