import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from beanie import PydanticObjectId

from app.models import (
    User,
    UserCreate,
    UserPublic,
    UserRegister,
    UserUpdate,
    UserUpdateMe,
    Message,
)
from app.core.security import get_password_hash, verify_password
from app.api.deps import get_current_active_superuser, get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", dependencies=[Depends(get_current_active_superuser)], response_model=list[UserPublic])
async def read_users(skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """
    users = await User.find().skip(skip).limit(limit).to_list()
    count = await User.find().count()
    return {"data": users, "count": count}


@router.post("/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic)
async def create_user(user_in: UserCreate) -> Any:
    """
    Create a new user.
    """
    existing_user = await User.find_one(User.email == user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="The user with this email already exists.")
    
    hashed_password = get_password_hash(user_in.password)
    user = User(**user_in.dict(), hashed_password=hashed_password)
    await user.insert()
    return user


@router.get("/me", response_model=UserPublic)
async def read_user_me(current_user: User = Depends(get_current_user)) -> Any:
    """
    Get current user.
    """
    return current_user


@router.patch("/me", response_model=UserPublic)
async def update_user_me(user_in: UserUpdateMe, current_user: User = Depends(get_current_user)) -> Any:
    """
    Update own user.
    """
    if user_in.email:
        existing_user = await User.find_one(User.email == user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=409, detail="User with this email already exists")

    update_data = user_in.dict(exclude_unset=True)
    await current_user.set(update_data)
    return current_user


@router.patch("/me/password", response_model=Message)
async def update_password_me(body: dict, current_user: User = Depends(get_current_user)) -> Any:
    """
    Update own password.
    """
    if not verify_password(body["current_password"], current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")

    if body["current_password"] == body["new_password"]:
        raise HTTPException(status_code=400, detail="New password cannot be the same as the current one")

    hashed_password = get_password_hash(body["new_password"])
    await current_user.set({"hashed_password": hashed_password})
    
    return Message(message="Password updated successfully")


@router.delete("/me", response_model=Message)
async def delete_user_me(current_user: User = Depends(get_current_user)) -> Any:
    """
    Delete own user.
    """
    if current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Super users cannot delete themselves")
    
    await current_user.delete()
    return Message(message="User deleted successfully")


@router.post("/signup", response_model=UserPublic)
async def register_user(user_in: UserRegister) -> Any:
    """
    Create a new user without authentication.
    """
    existing_user = await User.find_one(User.email == user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="The user with this email already exists")
    
    hashed_password = get_password_hash(user_in.password)
    user = User(**user_in.dict(), hashed_password=hashed_password)
    await user.insert()
    return user


@router.get("/{user_id}", response_model=UserPublic)
async def read_user_by_id(user_id: PydanticObjectId, current_user: User = Depends(get_current_user)) -> Any:
    """
    Get a specific user by ID.
    """
    user = await User.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id or current_user.is_superuser:
        return user

    raise HTTPException(status_code=403, detail="Insufficient privileges")


@router.patch("/{user_id}", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic)
async def update_user(user_id: PydanticObjectId, user_in: UserUpdate) -> Any:
    """
    Update a user.
    """
    user = await User.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_in.email:
        existing_user = await User.find_one(User.email == user_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=409, detail="User with this email already exists")

    update_data = user_in.dict(exclude_unset=True)
    await user.set(update_data)
    return user


@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)], response_model=Message)
async def delete_user(user_id: PydanticObjectId, current_user: User = Depends(get_current_user)) -> Message:
    """
    Delete a user.
    """
    user = await User.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(status_code=403, detail="Super users cannot delete themselves")

    await user.delete()
    return Message(message="User deleted successfully")
