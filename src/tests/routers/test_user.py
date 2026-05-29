import pytest
from fastapi import BackgroundTasks
from httpx import AsyncClient

from src import security


async def register_user(async_client: AsyncClient, email: str, password: str):
    return await async_client.post("/register", json={"email": email, "password": password})


@pytest.mark.anyio
async def test_register_user(async_client: AsyncClient):
    response = await register_user(async_client, "test@example.com", "1234")
    assert response.status_code == 201
    # assert response.json() == {"detail": "User created"}
    assert "User created" in response.json()["detail"]


@pytest.mark.anyio
async def test_register_user_already_exists(async_client: AsyncClient, registered_user: dict):
    response = await register_user(
        async_client, registered_user["email"], registered_user["password"]
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "User with that email already exists"}


@pytest.mark.anyio
async def test_login_user_not_exists(async_client: AsyncClient):
    response = await async_client.post(
        "/token",
        json={
            "email": "test@example.com",
            "password": "1234",
        },
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_login_user_not_confirmed(async_client: AsyncClient, registered_user: dict):
    response = await async_client.post(
        "/token",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 401


@pytest.mark.anyio
async def test_login(async_client: AsyncClient, confirmed_user: dict):
    response = await async_client.post(
        "/token",
        json={
            "email": confirmed_user["email"],
            "password": confirmed_user["password"],
        },
    )
    assert response.status_code == 200


@pytest.mark.anyio
async def test_authenticate_user(confirmed_user: dict):
    user = await security.authenticate_user(confirmed_user["email"], confirmed_user["password"])
    assert user.email == confirmed_user["email"]


@pytest.mark.anyio
async def test_authenticate_user_not_found():
    with pytest.raises(security.HTTPException):  # receive an exception to pass
        await security.authenticate_user("test@example.com", "1234")


@pytest.mark.anyio
async def test_authenticate_user_wrong_password(registered_user: dict):
    with pytest.raises(security.HTTPException):
        await security.authenticate_user(registered_user["email"], "wrongpassword")


@pytest.mark.anyio
async def test_confirm_user(async_client: AsyncClient, mocker):
    spy = mocker.spy(BackgroundTasks, "add_task")
    await register_user(async_client, "test@example.com", "1234")
    confirmation_url = str(spy.call_args[1]["confirmation_url"])
    response = await async_client.get(confirmation_url)
    assert response.status_code == 200
    assert response.json() == {"detail": "User confirmed"}


@pytest.mark.anyio
async def test_confirm_user_invalid_token(async_client: AsyncClient):
    response = await async_client.get("/confirm/invalidtoken")
    assert response.status_code == 401


@pytest.mark.anyio
async def test_confirm_user_expired_token(async_client: AsyncClient, mocker):
    mocker.patch("src.security.confirm_token_expire_minute", return_value=-1)
    spy = mocker.spy(BackgroundTasks, "add_task")
    await register_user(async_client, "test@example.com", "1234")
    confirmation_url = str(spy.call_args[1]["confirmation_url"])
    response = await async_client.get(confirmation_url)
    assert response.status_code == 401
    assert response.json() == {"detail": "Token expired"}
