
from fastapi import APIRouter, Request, Response, HTTPException, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from datetime import datetime, timedelta
from typing import Dict, Set
import uuid

from .settings import settings

router = APIRouter()

# In-memory session store (per process)
SESSIONS: Dict[str, datetime] = {}

COOKIE_NAME = "session_id"

def is_authenticated(request: Request) -> bool:
    sid = request.cookies.get(COOKIE_NAME)
    if not sid:
        return False
    exp = SESSIONS.get(sid)
    if not exp:
        return False
    if exp < datetime.utcnow():
        SESSIONS.pop(sid, None)
        return False
    return True

def require_auth(request: Request):
    if not is_authenticated(request):
        raise HTTPException(status_code=401, detail="Not authenticated")

@router.post("/login")
async def login(request: Request):
    form = await request.form()
    username = form.get("username", "")
    password = form.get("password", "")
    if username == settings.ADMIN_USERNAME and password == settings.ADMIN_PASSWORD:
        sid = str(uuid.uuid4())
        expire = datetime.utcnow() + timedelta(hours=settings.SESSION_EXPIRE_HOURS)
        SESSIONS[sid] = expire
        resp = RedirectResponse(url="/static/index.html", status_code=303)
        resp.set_cookie(COOKIE_NAME, sid, httponly=True, max_age=int(settings.SESSION_EXPIRE_HOURS*3600), samesite="lax")
        return resp
    return RedirectResponse(url="/static/login.html?error=1", status_code=303)

@router.get("/logout")
async def logout(request: Request):
    sid = request.cookies.get(COOKIE_NAME)
    if sid and sid in SESSIONS:
        SESSIONS.pop(sid, None)
    resp = RedirectResponse(url="/static/login.html", status_code=303)
    resp.delete_cookie(COOKIE_NAME)
    return resp
