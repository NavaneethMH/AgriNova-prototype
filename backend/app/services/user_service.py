"""
User service — CRUD operations for the User model.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.core.security import get_password_hash, verify_password
from app.schemas.auth import UserRegisterRequest


class UserService:
    """Business logic for user management."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Retrieve a user by UUID."""
        result = await self.db.execute(
            select(User).where(User.id == uuid.UUID(user_id), User.is_active == True)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by email address."""
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def create(self, data: UserRegisterRequest) -> User:
        """Create a new user with hashed password."""
        user = User(
            email=data.email.lower(),
            hashed_password=get_password_hash(data.password),
            full_name=data.full_name,
            organization=data.organization,
            phone=data.phone,
            role="farmer",
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by email/password.
        Returns User on success, None on failure.
        """
        user = await self.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        # Update last login timestamp
        user.last_login_at = datetime.now(timezone.utc)
        await self.db.flush()
        return user

    async def update_last_login(self, user: User) -> None:
        """Update last login timestamp."""
        user.last_login_at = datetime.now(timezone.utc)
        await self.db.flush()
