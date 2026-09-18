"""
Authentication dependency for protected API routes.

Extracts and validates the JWT bearer token from the Authorization header,
then resolves the current user from the database.
"""

import uuid

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    FastAPI dependency: extract JWT from Authorization header and return the
    authenticated User model instance.

    Raises:
        AuthenticationError: If the token is invalid or the user doesn't exist.
    """
    token = credentials.credentials
    user_id_str = decode_access_token(token)
    if user_id_str is None:
        raise AuthenticationError("Invalid or expired token")

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise AuthenticationError("Invalid token payload")

    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    if user is None:
        raise AuthenticationError("User not found")

    return user
