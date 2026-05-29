import base64
import uuid
from pathlib import Path

import httpx
from databases import Database
from openai import APIError, AsyncOpenAI

from src.config import config
from src.database import post_table

# Generated images go in this folder so paths stay consistent.
GENERATED_IMAGES_DIR = Path("src/libs/images/generated")


class APIResponseError(Exception):
    # Single app exception for external API/HTTP failures.
    pass


async def send_simple_email(to: str, subject: str, body: str) -> None:
    # Sends an email with Mailgun; failed responses are mapped to APIResponseError.
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"https://api.mailgun.net/v3/{config.MAILGUN_DOMAIN}/messages",
                auth=("api", config.MAILGUN_API_KEY),
                data={
                    "from": f"Social-Media-Feed <mailgun@{config.MAILGUN_DOMAIN}>",
                    "to": [to],
                    "subject": subject,
                    "text": body,
                },
            )
            response.raise_for_status()  # raise exception if response is not 2 (ok) or 3 (redirection), 4 or 5 (error)
            return response
        except httpx.HTTPStatusError as e:
            raise APIResponseError(
                f"API request failed with status code {e.response.status_code}"
            ) from e


async def send_user_registration_email(email: str, confirmation_url: str) -> None:
    return await send_simple_email(
        email,
        "Successfully signed up",
        f"Hi {email},\n\nPlease confirm your email by clicking the link below:\n\n{confirmation_url}",
    )


async def _generate_cute_creature_api(prompt: str):
    # Calls OpenAI, decodes base64 image data, saves a PNG, and returns the saved path.
    client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)

    try:
        response = await client.images.generate(
            model="gpt-image-1-mini",
            prompt=prompt,
            size="1024x1024",
            quality="low",
            n=1,
        )

        image_base64 = response.data[0].b64_json
        if not image_base64:
            raise APIResponseError("No image data returned from OpenAI")
        image_bytes = base64.b64decode(image_base64)
        GENERATED_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

        filename = f"{uuid.uuid4()}.png"
        file_path = GENERATED_IMAGES_DIR / filename

        file_path.write_bytes(image_bytes)

        return {"output_url": str(file_path)}
    except (APIError, IndexError, AttributeError, TypeError) as e:
        raise APIResponseError("API response could not be parsed") from e


async def generate_and_add_post(
    email: str,
    post_id: int,
    post_url: str,
    database: Database,
    prompt: str = "A lazha apso white dog is sleeping on the couch.",
):
    # If generation fails, only an error email is sent.
    # If it succeeds, image_url is saved on the post and a success email is sent.
    try:
        response = await _generate_cute_creature_api(prompt)
    except APIResponseError:
        return await send_simple_email(
            email,
            "Error generating image",
            f"Hi {email},\n there was an error generating your post.",
        )

    query = (
        post_table.update()
        .where(post_table.c.id == post_id)
        .values(image_url=response["output_url"])
    )

    await database.execute(query)
    return await send_simple_email(
        email,
        "Post generated",
        f"Hi {email},\n image generated and added to your post: {post_url}",
    )
