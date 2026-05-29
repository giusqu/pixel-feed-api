import pathlib

import pytest
from httpx import AsyncClient

FILENAME = "test.png"
UPLOAD_DIR = pathlib.Path("src/tests/images")


@pytest.fixture
def sample_image(tmp_path: pathlib.Path) -> pathlib.Path:  # tmp_path is a pytest fixture
    image_path = tmp_path / FILENAME

    image_path.write_bytes(b"fake image content")

    return image_path


async def call_upload_endpoint(async_client: AsyncClient, token: str, sample_image: pathlib.Path):
    return await async_client.post(
        "/upload",
        files={"file": open(sample_image, "rb")},
        headers={"Authorization": f"Bearer {token}"},
    )


@pytest.mark.anyio
async def test_upload_image(
    async_client: AsyncClient,
    logged_in_token: str,
    sample_image: pathlib.Path,
    tmp_path: pathlib.Path,
    monkeypatch,
):
    test_upload_dir = tmp_path / "images"
    monkeypatch.setattr("src.routers.upload.UPLOAD_DIR", test_upload_dir)

    response = await call_upload_endpoint(async_client, logged_in_token, sample_image)
    assert response.status_code == 201

    saved_file = test_upload_dir / sample_image.name
    assert saved_file.exists()

    data = response.json()
    assert data["file_path"] == str(saved_file)
    assert data["detail"] == f"Successfully uploaded {sample_image.name}"


@pytest.mark.anyio
async def test_upload_image_without_token_fails(
    async_client: AsyncClient,
    sample_image: pathlib.Path,
):
    with open(sample_image, "rb") as image_file:
        response = await async_client.post(
            "/upload",
            files={"file": (sample_image.name, image_file, "image/png")},
        )

    assert response.status_code in {401, 403}
