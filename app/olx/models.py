from datetime import datetime

from sqlalchemy import Column, String, ForeignKey, Integer, Text, Enum, Boolean, Float, DateTime
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from app.repository.base import Base


class Catsegory(Base):
    name = Column(String(length=255))

    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    parent = relationship('Category', remote_side='Category.id')


class Category(Base):
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    image_url = Column(String, nullable=True)
    parent = relationship('Category', remote_side='Category.id', back_populates='subcategories')
    subcategories = relationship('Category', back_populates='parent')
    fields = relationship('CategoryField', back_populates='category')
    advertisements = relationship('Advertisement', back_populates='category')


class FieldType(PyEnum):
    CHOICE = 'choice'
    BOOLEAN = 'boolean'
    INTEGER = 'integer'


class FieldChoice(Base):
    name = Column(String, nullable=False)
    field_id = Column(Integer, ForeignKey('categoryfields.id'), nullable=False)
    field = relationship("CategoryField", back_populates="choices")


class CategoryField(Base):
    name = Column(String, nullable=False)
    field_type = Column(Enum(FieldType), nullable=False)
    required = Column(Boolean, default=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    category = relationship("Category", back_populates="fields")
    choices = relationship('FieldChoice', back_populates='field')


class Advertisement(Base):
    title = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    user = relationship("User", back_populates='advertisements')
    category = relationship('Category', back_populates='advertisements')
    field_values = relationship('CategoryFieldValue', back_populates='advertisement')
    images = relationship('AdvertisementImage', back_populates='advertisement')


class AdvertisementImage(Base):
    image_url = Column(String)
    advertisement_id = Column(Integer, ForeignKey('advertisements.id'))
    advertisement = relationship('Advertisement', back_populates='images')


class CategoryFieldValue(Base):
    value = Column(String, nullable=False)
    field_id = Column(Integer, ForeignKey('categoryfields.id'), nullable=False)
    advertisement_id = Column(Integer, ForeignKey('advertisements.id'), nullable=False)
    field = relationship("CategoryField")
    advertisement = relationship('Advertisement', back_populates='field_values')


class Favorite(Base):
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    advertisement_id = Column(Integer, ForeignKey('advertisements.id'), nullable=False)
    user = relationship('User', back_populates='favorites')
    advertisement = relationship('Advertisement')


class RecentlyViewed(Base):
    viewed_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    advertisement_id = Column(Integer, ForeignKey('advertisements.id'), nullable=False)
    user = relationship('User', back_populates='recently_viewed')
    advertisement = relationship('Advertisement')



