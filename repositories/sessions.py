from __future__ import annotations

import json
from typing import Any, Literal, Mapping
from datetime import datetime, timedelta
from uuid import UUID
from utils import services



SESSION_EXPIRY = 60 * 60

def make_key(session_id: UUID | Literal["*"]) -> str:
    return f"server:sessions:{session_id}"


def serialize(session: Mapping[str, Any]) -> str:
    return json.dumps(
        {
            "session_id": str(session["session_id"]),
            "account_id": str(session["account_id"]),
            # "user_agent": session["user_agent"],
            "expires_at": session["expires_at"].isoformat(),
            "created_at": session["created_at"].isoformat(),
            "updated_at": session["updated_at"].isoformat(),
        }
    )


def deserialize(raw_session: str) -> dict[str, Any]:
    session = json.loads(raw_session)

    assert isinstance(session, dict)

    session["session_id"] = UUID(session["session_id"])
    session["account_id"] = UUID(session["account_id"])
    session["expires_at"] = datetime.fromisoformat(session["expires_at"])
    session["created_at"] = datetime.fromisoformat(session["created_at"])
    session["updated_at"] = datetime.fromisoformat(session["updated_at"])

    return session


async def create(
    session_id: UUID,
    account_id: UUID,
    # user_agent: str,
) -> dict[str, Any]:
    now = datetime.now()
    expires_at = now + timedelta(seconds = SESSION_EXPIRY)
    session = {
        "session_id": session_id,
        "account_id": account_id,
        # "user_agent": user_agent,
        "expires_at": expires_at,
        "created_at": now,
        "updated_at": now,
    }

    await services.redis.set(name=make_key(session_id), value=serialize(session), ex=SESSION_EXPIRY)

    return session


async def fetch_by_id(session_id: UUID) -> dict[str, Any] | None:
    session_key = make_key(session_id)
    session = await services.redis.get(session_key)
    return deserialize(session) if session is not None else None
