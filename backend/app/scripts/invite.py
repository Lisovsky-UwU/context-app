"""Создаёт код приглашения без входа в приложение — им регистрируется первый участник.

    uv run python -m app.scripts.invite
"""

import secrets

from app.db.session import SessionLocal
from app.models import Invite


def main() -> None:
    with SessionLocal() as db:
        invite = Invite(code=secrets.token_hex(4).upper())
        db.add(invite)
        db.commit()
        print(f"Код приглашения: {invite.code}")


if __name__ == "__main__":
    main()
