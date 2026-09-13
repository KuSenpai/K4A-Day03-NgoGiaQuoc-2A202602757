"""FastAPI web prototype with protected, observable Agentic AI administration."""

from __future__ import annotations

import asyncio
import os
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from starlette.middleware.sessions import SessionMiddleware

from src.agent_execution import ExecutionStore

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
load_dotenv(BASE_DIR.parent / ".env")

password_hash = os.getenv("ADMIN_PASSWORD_HASH", "")
session_secret = os.getenv("SESSION_SECRET", "")
if not session_secret:
    raise RuntimeError("SESSION_SECRET must be configured in .env before starting the web application.")
if not password_hash:
    raise RuntimeError("ADMIN_PASSWORD_HASH must be configured in .env before starting the web application.")

is_local = os.getenv("APP_ENV", "development").lower() == "development"
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
store = ExecutionStore()
login_attempts: dict[str, deque[float]] = defaultdict(deque)

app = FastAPI(title="Agentic AI Admin Prototype", docs_url=None, redoc_url=None)
app.add_middleware(
    SessionMiddleware,
    secret_key=session_secret,
    session_cookie="agentic_admin_session",
    max_age=60 * 60,
    same_site="lax",
    https_only=not is_local,
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class LoginRequest(BaseModel):
    password: str = Field(min_length=1, max_length=256)


class ExecutionRequest(BaseModel):
    message: str = Field(min_length=3, max_length=1000)
    file_name: str | None = Field(default=None, max_length=255)


def require_admin(request: Request) -> None:
    if not request.session.get("is_admin"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin authentication required")


def client_key(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def check_login_rate_limit(request: Request) -> None:
    now = time.monotonic()
    attempts = login_attempts[client_key(request)]
    while attempts and now - attempts[0] > 60:
        attempts.popleft()
    if len(attempts) >= 5:
        raise HTTPException(status_code=429, detail="Too many login attempts. Please try again later.")


@app.get("/", include_in_schema=False)
def user_page() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/login", include_in_schema=False)
def login_page(request: Request):
    if request.session.get("is_admin"):
        return RedirectResponse("/admin", status_code=status.HTTP_303_SEE_OTHER)
    return FileResponse(STATIC_DIR / "login.html")


@app.get("/admin", include_in_schema=False)
@app.get("/admin/dashboard", include_in_schema=False)
@app.get("/admin/agent-trace", include_in_schema=False)
@app.get("/admin/tools", include_in_schema=False)
@app.get("/admin/logs", include_in_schema=False)
@app.get("/admin/settings", include_in_schema=False)
def admin_page(request: Request):
    if not request.session.get("is_admin"):
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
    return FileResponse(STATIC_DIR / "admin.html")


@app.post("/api/auth/login")
def login(payload: LoginRequest, request: Request):
    check_login_rate_limit(request)
    if not password_context.verify(payload.password, password_hash):
        login_attempts[client_key(request)].append(time.monotonic())
        raise HTTPException(status_code=401, detail="Mật khẩu không chính xác. Vui lòng thử lại.")
    login_attempts.pop(client_key(request), None)
    request.session.clear()
    request.session["is_admin"] = True
    request.session["role"] = "administrator"
    return {"authenticated": True, "role": "administrator"}


@app.post("/api/auth/logout")
def logout(request: Request):
    request.session.clear()
    return {"authenticated": False}


@app.get("/api/auth/me")
def auth_me(request: Request):
    return {
        "authenticated": bool(request.session.get("is_admin")),
        "role": "administrator" if request.session.get("is_admin") else None,
    }


@app.post("/api/executions", status_code=202)
async def create_execution(payload: ExecutionRequest):
    execution = store.create(payload.message, payload.file_name)
    asyncio.create_task(store.simulate(execution["id"]))
    return store.public_view(execution["id"])


@app.get("/api/executions/{execution_id}")
def public_execution(execution_id: str):
    execution = store.public_view(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution


@app.get("/api/admin/dashboard", dependencies=[Depends(require_admin)])
def admin_dashboard():
    return store.dashboard()


@app.get("/api/admin/executions", dependencies=[Depends(require_admin)])
def admin_executions():
    return {"items": store.history()}


@app.get("/api/admin/executions/{execution_id}", dependencies=[Depends(require_admin)])
def admin_execution(execution_id: str):
    execution = store.admin_view(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution
