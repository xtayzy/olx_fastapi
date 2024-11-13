import os
import shutil
from datetime import datetime
from typing import List
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends

from app.olx.models import Category, CategoryField, FieldChoice, Advertisement, AdvertisementImage, CategoryFieldValue, \
    Favorite, RecentlyViewed
from app.olx.schemas import SCategoryCreate, SCategoryFieldCreate, SCategoryFieldChoiceCreate, SAdvertisementCreate, \
    SCategoryFieldValueCreate, SFavoriteResponse
from app.users.dependencies import get_current_user
from app.users.models import User

router = APIRouter(prefix="/olx", tags=["olx"])


# @router.post('/add_category')
# async def add_category( SAddCategory):
#     if parent_id:
#         category = await Category.create(name=name, parent_id=parent_id)
#     else:
#         category = await Category.create(name=name)
#
#     return {
#         'category': category
#     }
#
#
# @router.get('/get_category/{cat_id}')
# async def get_category_by_id(cat_id: int):
#     category = await Category.find_one_or_none(filter=Category.id == cat_id)
#
#     return category


@router.post('/category/create')
async def create_category(
        name: str,
        description: str,
        parent_id: int = 0,
        image: UploadFile = File(...)
):
    parent_id = parent_id if parent_id != 0 else None

    if parent_id:
        category = await Category.find_by_id_or_fail(parent_id)
        print(1111)

    path = f'media/{image.filename}'

    with open(path, 'wb') as f:
        f.write(await image.read())

    category = await Category.create(
        name=name,
        description=description,
        parent_id=parent_id,
        image_url=f'127.0.0.1:8000/{path}'
    )

    return {
        'created_category': category
    }


@router.post('/category/field/create')
async def category_field_create(field_data: SCategoryFieldCreate):
    if field_data.category_id:
        category = await Category.find_by_id_or_fail(field_data.category_id)

    field = await CategoryField.create(
        name=field_data.name,
        field_type=field_data.field_type,
        required=field_data.required,
        category_id=field_data.category_id
    )

    return field


@router.post('/category/field/choice/create')
async def category_field_choice_create(choice_data: SCategoryFieldChoiceCreate):
    if choice_data.field_id:
        field = await CategoryField.find_by_id_or_fail(choice_data.field_id)
        if field.field_type.value != 'choice':
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="field.field_type должен быть choices"
            )

    choice = await FieldChoice.create(
        name=choice_data.name,
        field_id=choice_data.field_id
    )

    return choice


@router.get('/category')
async def get_categories():
    categories = await Category.get_all(includes=['subcategories', 'fields', 'fields.choices', 'advertisements'])
    categories = list(filter(lambda x: x.parent_id is None, categories))

    return categories


@router.get('/category/{cat_id}')
async def get_categories(cat_id: int):
    category = await Category.get_all(includes=['subcategories', 'fields', 'fields.choices', 'advertisements'])
    category = list(filter(lambda x: x.id == cat_id, category))

    return category


@router.post('/advertisement/create')
async def advertisement_create(advertisement_data: SAdvertisementCreate, user: User = Depends(get_current_user)):
    if advertisement_data.category_id:
        category = await Category.find_by_id_or_fail(advertisement_data.category_id)

    advertisement = await Advertisement.create(
        title=advertisement_data.title,
        description=advertisement_data.description,
        price=advertisement_data.price,
        user_id=user.id,
        category_id=advertisement_data.category_id
    )

    return advertisement


@router.post('/advertisement/image/create')
async def advertisement_image_create(advertisement_id: int, image: UploadFile = File(...)):
    if advertisement_id:
        advertisement = await Advertisement.find_by_id_or_fail(advertisement_id)

    path = f'media/{image.filename}'

    with open(path, 'wb') as f:
        f.write(await image.read())

    advertisement_image = await AdvertisementImage.create(
        image_url=f'127.0.0.1:8000/{path}',
        advertisement_id=advertisement_id
    )

    return advertisement_image


@router.post('/advertisement/category/field/value/create')
async def advertisement_category_field_value_create(data: SCategoryFieldValueCreate):
    if data.advertisement_id or data.field_id:
        advertisement = await Advertisement.find_by_id_or_fail(data.advertisement_id)
        field = await CategoryField.find_by_id_or_fail(data.field_id)

    value = await CategoryFieldValue.create(
        value=data.value,
        advertisement_id=data.advertisement_id,
        field_id=data.field_id
    )

    return value


@router.get('/advertisement')
async def advertisements_get():
    advertisements = await Advertisement.get_all(includes=['category', 'images', 'category.fields'])

    return advertisements


@router.get('/advertisement/{adv_id}')
async def get_advertisement_by_id(adv_id: int):
    advertisement = await Advertisement.get_all(includes=['category', 'images', 'category.fields'],
                                                filter=Advertisement.id == adv_id)

    return advertisement


@router.post('/advertisement/favorite/add')
async def add_favorite_advertisement(advertisement_id: int, user: User = Depends(get_current_user)):
    if advertisement_id:
        advertisement = await Advertisement.find_by_id_or_fail(advertisement_id)
        favorite = await Favorite.find_one_or_none(
            filter=(Favorite.user_id == user.id) & (Favorite.advertisement_id == advertisement_id)
        )
        if favorite:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='запись уже существует'
            )

    favorite = await Favorite.create(
        advertisement_id=advertisement_id,
        user_id=user.id
    )

    return favorite


@router.get('/advertisements/favorite', response_model=List[SFavoriteResponse])
async def get_favorite_advertisements(user: User = Depends(get_current_user)):
    favorites = await Favorite.get_all(filter=Favorite.user_id == user.id, includes=['advertisement'])

    return favorites


@router.get('/advertisements/favorite/{favorite_id}', response_model=List[SFavoriteResponse])
async def get_favorite_advertisements(favorite_id: int, user: User = Depends(get_current_user)):
    favorite = await Favorite.get_all(filter=(Favorite.user_id == user.id) & (Favorite.id == favorite_id),
                                      includes=['advertisement'])

    return favorite


@router.post('/advertisement/recently_viewed/add')
async def add_recently_viewed(advertisement_id: int, user: User = Depends(get_current_user)):
    if advertisement_id:
        advertisement = await Advertisement.find_by_id_or_fail(advertisement_id)
        recently_viewed = await RecentlyViewed.find_one_or_none(
            filter=(RecentlyViewed.advertisement_id == advertisement_id) &
                   (RecentlyViewed.user_id == user.id))

        if recently_viewed:
            recently_viewed = await RecentlyViewed.update(model_id=recently_viewed.id, viewed_at=datetime.utcnow())

            return recently_viewed

    recently_viewed = await RecentlyViewed.create(
        user_id=user.id,
        advertisement_id=advertisement_id
    )

    return recently_viewed



