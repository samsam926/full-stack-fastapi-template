import uuid
from typing import Any

from app.core.security import get_password_hash, verify_password
from app.models import Item, ItemCreate, User, UserCreate, UserUpdate

async def create_user(user_create: UserCreate) -> User:
    """Create a new user in MongoDB."""
    user_data = user_create.dict(exclude={"password"})
    user_data["hashed_password"] = get_password_hash(user_create.password)
    
    user = User(**user_data)
    await user.insert()
    return user


async def update_user(db_user: User, user_in: UserUpdate) -> Any:
    """Update an existing user in MongoDB."""
    update_data = user_in.dict(exclude_unset=True)
    
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    await db_user.set(update_data)
    return db_user


async def get_user_by_email(email: str) -> User | None:
    """Find a user by email in MongoDB."""
    print(f"Searching for user with email: {email}")
    return await User.find_one(User.email == email)


async def authenticate(email: str, password: str) -> User | None:
    """Authenticate user by email and password."""
    user = await get_user_by_email(email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


async def create_item(item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    """Create a new item in MongoDB."""
    item = Item(**item_in.dict(), owner_id=owner_id)
    await item.insert()
    return item
