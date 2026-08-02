from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from fastapi import Request
from fastapi.exceptions import HTTPException
from starlette.middleware.sessions import SessionMiddleware
from functools import wraps
from typing import Callable
import secrets

pwd_context = PasswordHash([Argon2Hasher()])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def require_login(request: Request):
    if not request.session.get("user"):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return request.session["user"]

# for CSRF: generate token and store in session
def generate_csrf_token(request: Request) -> str:
    token = secrets.token_hex(16)
    request.session["csrf_token"] = token
    return token

def validate_csrf(request: Request, token: str):
    session_token = request.session.get("csrf_token")
    if not session_token or session_token != token:
        raise HTTPException(status_code=403, detail="CSRF token invalid")