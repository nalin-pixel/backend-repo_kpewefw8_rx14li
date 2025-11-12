"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List
import datetime as dt

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Event management portal schemas

class Event(BaseModel):
    """
    Events collection schema
    Collection name: "event"
    """
    title: str = Field(..., description="Event title")
    description: str = Field(..., description="Detailed description of the event")
    event_date: dt.date = Field(..., description="Event date")
    event_time: str = Field(..., description="Event time (e.g., 5:00 PM)")
    location: str = Field(..., description="Venue or location")
    category: str = Field(..., description="Category such as Tech, Cultural, Sports, Workshop")
    cover_image: Optional[str] = Field(None, description="Cover image URL")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    is_featured: bool = Field(False, description="Whether this is a featured event")
