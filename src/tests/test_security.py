import pytest
from jose import jwt

from src import security


@pytest.mark.anyio
async def test_access_token_expire_minute():
    return security.access_token_expire_minute() == 30


@pytest.mark.anyio
async def test_confirm_token_expire_minute():
    return security.confirm_token_expire_minute() == 1440


@pytest.mark.anyio
async def test_create_access_token():
    token = security.create_access_token("email@example.com")
    payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    assert {"sub": "email@example.com", "type": "access"}.items() <= payload.items()


@pytest.mark.anyio
async def test_create_confirmation_token():
    token = security.create_confirmation_token("email@example.com")
    payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    assert {"sub": "email@example.com", "type": "confirmation"}.items() <= payload.items()


@pytest.mark.anyio
async def test_get_subject_for_token_type_valid_confirmation():
    email = "email@example.com"
    token = security.create_confirmation_token(email)
    assert email == security.get_subject_for_token_type(token, "confirmation")


@pytest.mark.anyio
async def test_get_subject_for_token_type_valid_access():
    email = "email@example.com"
    token = security.create_access_token(email)
    assert email == security.get_subject_for_token_type(token, "access")


@pytest.mark.anyio
async def test_get_subject_for_token_type_expired(mocker):
    mocker.patch("src.security.access_token_expire_minute", return_value=-1)
    email = "email@example.com"
    token = security.create_access_token(email)
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "access")
    assert "Token expired" == exc_info.value.detail


@pytest.mark.anyio
async def test_get_subject_for_token_type_invalid_token():
    token = "invalid token"
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "access")
    assert "Invalid token" == exc_info.value.detail


@pytest.mark.anyio
async def test_get_subject_for_token_type_missing_sub():
    email = "email@example.com"
    token = security.create_access_token(email)
    payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
    del payload["sub"]
    token = jwt.encode(payload, key=security.SECRET_KEY, algorithm=security.ALGORITHM)
    # simplier:
    # exp = int(time.time()) + 3600
    # payload = {"exp": exp, "type": "access"}
    # token = jwt.encode(payload, key=security.SECRET_KEY, algorithm=security.ALGORITHM)
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "access")
    assert "Token is missing 'sub' field" == exc_info.value.detail


@pytest.mark.anyio
async def test_get_subject_for_token_type_wrong_token_type():
    email = "email@example.com"
    token = security.create_access_token(email)
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "confirmation")
    assert "Incorrect token type: expected: confirmation got: access" == exc_info.value.detail


@pytest.mark.anyio
async def test_password_hashes():
    password = "anypassword"
    assert security.verify_password(password, security.get_password_hash(password))


@pytest.mark.anyio
async def test_get_user(registered_user: dict):
    user = await security.get_user(registered_user["email"])
    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_get_user_not_found():
    user = await security.get_user("test@example.com")
    assert user is None


@pytest.mark.anyio
async def test_get_current_user(registered_user: dict):
    token = security.create_access_token(registered_user["email"])
    user = await security.get_current_user(token)
    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_get_current_user_invalid_token():
    with pytest.raises(security.HTTPException):
        await security.get_current_user("invalid token")


@pytest.mark.anyio
async def test_get_current_user_wrong_token_type():
    token = security.create_confirmation_token("email@example.com")
    with pytest.raises(security.HTTPException):
        await security.get_current_user(token)
