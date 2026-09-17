import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import current_user
from app.core.config import settings
from app.core.security import create_token, hash_password, verify_password
from app.db.session import get_db
from app.models import Invite, User
from app.schemas.auth import (
    InvitePublic,
    LoginRequest,
    ProfileUpdate,
    RegisterRequest,
    UserMe,
    UserPublic,
)

router = APIRouter()


def _set_cookie(response: Response, user: User) -> None:
    response.set_cookie(
        settings.cookie_name,
        create_token(user.id),
        max_age=settings.jwt_expires_days * 24 * 3600,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        domain=settings.cookie_domain,
        path="/",
    )


@router.post("/auth/register", response_model=UserMe, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)) -> User:
    code = payload.invite_code.strip().upper()
    invite = db.scalar(select(Invite).where(Invite.code == code))
    now = datetime.now(timezone.utc)
    if invite is None or invite.used_at is not None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Код приглашения не подходит")
    if invite.expires_at and invite.expires_at < now:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Срок действия кода истёк")

    username = payload.username.strip()
    if db.scalar(select(User).where(func.lower(User.username) == username.lower())):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Это имя уже занято, придумайте другое")

    user = User(
        username=username,
        password_hash=hash_password(payload.password),
        display_name=username,
    )
    db.add(user)
    db.flush()
    invite.used_by_id = user.id
    invite.used_at = now
    db.commit()
    db.refresh(user)
    _set_cookie(response, user)
    return user


@router.post("/auth/login", response_model=UserMe)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> User:
    user = db.scalar(select(User).where(func.lower(User.username) == payload.username.strip().lower()))
    if user is None or not verify_password(payload.password, user.password_hash) or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Неверное имя или пароль")
    _set_cookie(response, user)
    return user


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    response.delete_cookie(settings.cookie_name, path="/", domain=settings.cookie_domain)


@router.get("/auth/me", response_model=UserMe)
def me(user: User = Depends(current_user)) -> User:
    return user


@router.patch("/auth/me", response_model=UserMe)
def update_me(
    payload: ProfileUpdate, user: User = Depends(current_user), db: Session = Depends(get_db)
) -> User:
    if payload.display_name:
        user.display_name = payload.display_name.strip()
    if payload.accent:
        user.accent = payload.accent
    db.commit()
    db.refresh(user)
    return user


@router.get("/users", response_model=list[UserPublic])
def users(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[User]:
    return list(db.scalars(select(User).where(User.is_active.is_(True)).order_by(User.display_name)))


@router.get("/invites", response_model=list[InvitePublic])
def my_invites(db: Session = Depends(get_db), user: User = Depends(current_user)) -> list[Invite]:
    return list(
        db.scalars(
            select(Invite).where(Invite.created_by_id == user.id).order_by(Invite.created_at.desc())
        )
    )


@router.post("/invites", response_model=InvitePublic, status_code=status.HTTP_201_CREATED)
def create_invite(db: Session = Depends(get_db), user: User = Depends(current_user)) -> Invite:
    invite = Invite(code=secrets.token_hex(4).upper(), created_by_id=user.id)
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return invite
