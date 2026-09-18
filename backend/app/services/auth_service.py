"""
Authentication service — business logic for registration and login.

Orchestrates password hashing, duplicate checks, JWT creation.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, ConflictError
from app.core.logging import get_logger
from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.user_repository import UserRepository
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse

logger = get_logger(__name__)


class AuthService:
    """Authentication business logic."""

    def __init__(self, db: AsyncSession) -> None:
        self.repo = UserRepository(db)

    async def register(self, data: UserCreate) -> TokenResponse:
        """
        Register a new user account.

        Args:
            data: Validated registration data.

        Returns:
            JWT token and user profile.

        Raises:
            ConflictError: If email is already registered.
        """
        existing = await self.repo.get_by_email(data.email)
        if existing is not None:
            raise ConflictError("A user with this email already exists")

        hashed = hash_password(data.password)
        user = await self.repo.create(
            email=data.email,
            hashed_password=hashed,
            name=data.name,
        )
        logger.info("User registered: %s", user.email)

        token = create_access_token(subject=str(user.id))
        return TokenResponse(
            access_token=token,
            user=UserResponse.model_validate(user),
        )

    async def login(self, data: UserLogin) -> TokenResponse:
        """
        Authenticate a user and return a JWT.

        Args:
            data: Validated login credentials.

        Returns:
            JWT token and user profile.

        Raises:
            AuthenticationError: If credentials are invalid.
        """
        user = await self.repo.get_by_email(data.email)
        if user is None or not verify_password(data.password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")

        logger.info("User logged in: %s", user.email)

        token = create_access_token(subject=str(user.id))
        return TokenResponse(
            access_token=token,
            user=UserResponse.model_validate(user),
        )
