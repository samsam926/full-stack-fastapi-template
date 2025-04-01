import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from beanie import PydanticObjectId

from app.models import Item, ItemCreate, ItemPublic, ItemsPublic, ItemUpdate, Message
from app.api.deps import CurrentUser, get_current_user

router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=ItemsPublic)
async def read_items(
    current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve items.
    """
    if current_user.is_superuser:
        items = await Item.find().skip(skip).limit(limit).to_list()
        count = await Item.find().count()
    else:
        items = await Item.find(Item.owner_id == current_user.id).skip(skip).limit(limit).to_list()
        count = await Item.find(Item.owner_id == current_user.id).count()

    return ItemsPublic(data=items, count=count)


@router.get("/{id}", response_model=ItemPublic)
async def read_item(id: PydanticObjectId, current_user: CurrentUser) -> Any:
    """
    Get item by ID.
    """
    item = await Item.get(id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if not current_user.is_superuser and item.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    return item


@router.post("/", response_model=ItemPublic)
async def create_item(
    item_in: ItemCreate, current_user: CurrentUser
) -> Any:
    """
    Create a new item.
    """
    item = Item(**item_in.dict(), owner_id=current_user.id)
    await item.insert()
    return item


@router.put("/{id}", response_model=ItemPublic)
async def update_item(
    id: PydanticObjectId, item_in: ItemUpdate, current_user: CurrentUser
) -> Any:
    """
    Update an item.
    """
    item = await Item.get(id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if not current_user.is_superuser and item.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    update_data = item_in.dict(exclude_unset=True)
    await item.set(update_data)  # Update fields in the item
    return item


@router.delete("/{id}")
async def delete_item(id: PydanticObjectId, current_user: CurrentUser) -> Message:
    """
    Delete an item.
    """
    item = await Item.get(id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    if not current_user.is_superuser and item.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    await item.delete()
    return Message(message="Item deleted successfully")
