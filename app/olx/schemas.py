from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel
from enum import Enum as PyEnum

from app.olx.models import FieldType


class SCategoryFieldChoiceCreate(BaseModel):
    name: str
    field_id: int


class SCategoryFieldCreate(BaseModel):
    name: str
    field_type: FieldType
    required: bool = False
    category_id: int


class SCategoryCreate(BaseModel):
    name: str
    description: str
    parent_id: int or None


class SAdvertisementCreate(BaseModel):
    title: str
    description: str
    price: float
    category_id: int


class SCategoryFieldValueCreate(BaseModel):
    value: str
    field_id: int
    advertisement_id: int


class SAdvertisementResponse(BaseModel):
    id: int
    title: str
    description: str
    created_at: datetime
    price: float
    category_id: int


class SFavoriteResponse(BaseModel):
    id: int
    user_id: int
    advertisement: SAdvertisementResponse







