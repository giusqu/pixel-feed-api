from unittest.mock import AsyncMock, Mock

import httpx
import pytest
from databases import Database

from src.database import database, post_table
from src.tasks import (
    APIResponseError,
    _generate_cute_creature_api,
    generate_and_add_post,
    send_simple_email,
)


@pytest.mark.anyio
async def test_send_simple_email(mock_httpx_client):
    await send_simple_email("test@example.com", "Test Subject", "Test Body")
    mock_httpx_client.post.assert_called()  # check if post method was called


@pytest.mark.anyio
async def test_send_simple_email_server_error(mock_httpx_client):
    mock_httpx_client.post.return_value = httpx.Response(
        status_code=500, content="", request=httpx.Request("POST", "//")
    )

    with pytest.raises(APIResponseError):
        await send_simple_email("test@example.com", "Test Subject", "Test Body")


@pytest.mark.anyio
async def test_generate_cute_creature_api_success(monkeypatch):
    # Mocking AsyncOpenAI here keeps this test offline and stable.
    fake_b64 = "aGVsbG8="
    mock_client = Mock()
    mock_client.images = Mock()
    mock_client.images.generate = AsyncMock(return_value=Mock(data=[Mock(b64_json=fake_b64)]))
    monkeypatch.setattr("src.tasks.AsyncOpenAI", Mock(return_value=mock_client))

    result = await _generate_cute_creature_api("A dog on the couch.")
    # Path check is OS-safe: Windows uses "\" while Linux/macOS use "/".
    assert "generated" in result["output_url"]
    assert result["output_url"].endswith(".png")


@pytest.mark.anyio
async def test_generate_cute_creature_api_server_error(monkeypatch):
    # Empty data simulates a bad API payload and should trigger APIResponseError.
    mock_client = Mock()
    mock_client.images = Mock()
    mock_client.images.generate = AsyncMock(return_value=Mock(data=[]))
    monkeypatch.setattr("src.tasks.AsyncOpenAI", Mock(return_value=mock_client))

    with pytest.raises(APIResponseError, match="API response could not be parsed"):
        await _generate_cute_creature_api("A dog on the couch.")


@pytest.mark.anyio
async def test_generate_and_add_post_success(
    created_post: dict, confirmed_user: dict, db: Database, monkeypatch
):
    # Image generation is mocked so this test checks only DB update + email flow.
    json_data = {"output_url": "https://example.com/image.jpg"}

    async def fake_generate_cute_creature_api(prompt: str):
        return json_data

    sent_emails = []

    async def fake_send_simple_email(to: str, subject: str, body: str):
        sent_emails.append({"to": to, "subject": subject, "body": body})

    monkeypatch.setattr("src.tasks._generate_cute_creature_api", fake_generate_cute_creature_api)
    monkeypatch.setattr("src.tasks.send_simple_email", fake_send_simple_email)

    await generate_and_add_post(
        confirmed_user["email"],
        created_post["id"],
        "/post/1",
        db,
        "A dog on the couch.",
    )
    query = post_table.select().where(post_table.c.id == created_post["id"])
    update_post = await database.fetch_one(query)

    assert update_post.image_url == json_data["output_url"]
    assert len(sent_emails) == 1
    assert sent_emails[0]["to"] == confirmed_user["email"]
