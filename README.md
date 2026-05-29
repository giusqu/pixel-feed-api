# PixelFeed

PixelFeed is a REST API built with FastAPI that simulates a small social media feed.
It supports JWT-authenticated users, post/comment/like creation, image uploads, and asynchronous integrations with external services (Mailgun for email and OpenAI for image generation).

## What it does
- User registration with email confirmation.
- Login with Bearer token (JWT) and protection of private endpoints.
- Creation of posts, comments, and likes.
- Post listing with sorting by newest, oldest, or most liked.
- Post detail endpoint with aggregated comments.
- Image file upload to local storage.
- Optional image generation for a post via prompt: the task saves the file, updates the post, and sends a status email.

## Tech stack
- FastAPI + Uvicorn
- SQLite (via SQLAlchemy + `databases`)
- JWT (`python-jose`) + password hashing (`passlib`/Argon2)
- Asynchronous tasks with `BackgroundTasks`
- External integrations: Mailgun, OpenAI Images API
- Tests with Pytest

## Environments
The project is configured for three separate environments:
- `dev`: local development (`DEV_...` variables in `.env`).
- `test`: automated tests with dedicated configuration (separate DB and forced rollback).
- `prod`: production environment (`PROD_...` variables in `.env`).

Environment selection is controlled by `ENV_STATE` (`dev`, `test`, `prod`) in `src/config.py`.

## Quick start
1. Configure `.env` (e.g. `ENV_STATE=dev`, `DEV_DATABASE_URL`, Mailgun/OpenAI keys).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the server:
   ```bash
   uvicorn src.main:app --reload
   ```
4. API docs are available at `/docs`.
