from typing import List, Optional
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    validator,
)  # data validation = pydantic = class
import re
from datetime import datetime
from enums import OrderStatus


# Article inside UserDisplay
class Post(BaseModel):
    content: str

    class Config:
        from_attributes = True  # orm_mode is changed to from_attributes


class UserBase(BaseModel):
    username: str
    email: EmailStr
    password: str

    @validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[^\w\s]", v):
            raise ValueError("Password must contain at least one special character")
        return v


class ImageInUser(BaseModel):
    file_path: str
    id: int

    class Config:
        from_attributes = True


class UserDisplay(BaseModel):
    username: str
    email: str
    id: int
    images: List[ImageInUser] = []
    posts: List[Post] = []  # tpye of data which we want return

    class Config:
        from_attributes = True


class UserImage(BaseModel):
    id: int
    file_path: str
    user_id: int


class FriendshipBase(BaseModel):
    user_id: int
    friend_id: int
    sender_username: str


class FriendshipCreate(FriendshipBase):
    pass


class Friendship(FriendshipBase):
    id: int

    class Config:
        from_attributes = True


class FriendRequests(BaseModel):
    friend_requests: List[Friendship]


# user inside article display and ProductDisplay
class User(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class PostBase(BaseModel):  # what we recieve from the user when we are creating post
    content: str
    user_id: int
    username: str
    timestamp: datetime


class ImageInPost(BaseModel):
    file_path: str
    id: int

    class Config:
        from_attributes = True


class PostDisplay(
    BaseModel
):  # a data structure to send to the user when we are creating post
    id: int
    content: str
    user: User
    user_id: int
    images: List[ImageInPost] = []
    timestamp: datetime
    likes_count: int = Field(default=0, description="Total number of likes")
    liked_by_user: bool = Field(
        default=False, description="Whether current user liked this post"
    )

    class Config:  # convert instances of ORM models(db models) into dictionaries whrn serializing the data.
        from_attributes = True


class PostUpdate(BaseModel):
    content: str
    image_url: str = None


class PostImage(BaseModel):
    id: int
    file_path: str
    post_id: int


class UserAuth(BaseModel):
    id: int
    username: str
    email: str


# For Post Display
class CommentDisplay(BaseModel):
    txt: str
    user_id: int
    username: str
    timestamp: datetime

    class Config:  # convert instances of ORM models(db models) into dictionaries whrn serializing the data.
        from_attributes = True


class CommentBase(BaseModel):
    txt: str
    username: str
    post_id: int
    user_id: int


# Group


class GroupBase(BaseModel):
    name: str
    description: str
    created_at: datetime = datetime.now()
    creator_id: int  # ID of the user who created the group
    members: List[int] = []  # List of user IDs representing members of the group
    is_public: bool = True  # Indicates whether the group is public or private
    visibility: str = "public"  # Visibility settings of the group


class GroupDisplay(BaseModel):
    id: int
    name: str
    description: str
    created_at: datetime
    creator_id: int
    members: List[int]
    visibility: str

    class Config:
        from_attributes = True


class GroupMembershipRequest(BaseModel):
    user_id: int


class GroupMembershipResponse(BaseModel):
    message: str


class GroupMembers(BaseModel):
    username: str

    class Config:
        from_attributes = True


class GroupPostBase(BaseModel):
    content: str
    group_id: int
    author_id: int
    created_at: datetime = datetime.now()


class GroupPostCreate(GroupPostBase):
    pass


class GroupPostDisplay(BaseModel):
    content: str
    group_id: int
    author_id: int
    created_at: datetime = datetime.now()

    class Config:
        from_attributes = True


class GroupPostUpdate(BaseModel):
    content: str


class ProductBase(BaseModel):
    product_name: str
    description: str
    price: float
    quantity: int
    published: bool


class TestProductBase(BaseModel):
    product_name: str
    description: str
    price: float
    quantity: int
    published: bool
    seller_id: int


# PRoductReview inside ReviewDisplay
class ProductReview(BaseModel):
    product_name: str
    seller_id: int

    class Config:
        from_attributes = True


# ImageInProduct inside ProductDisplay
class ImageInProduct(BaseModel):
    file_path: str
    id: int

    class Config:
        from_attributes = True


class ProductDisplay(BaseModel):
    product_name: str
    id: int
    description: str
    price: float
    quantity: float
    images: List[ImageInProduct] = []
    published: bool
    user: User

    class Config:
        from_attributes = True


class ProductImage(BaseModel):
    id: int
    file_path: str
    product_id: int


class MinOrderLine(BaseModel):
    product_id: int
    quantity: int


class OrderLine(BaseModel):
    order_id: Optional[int]
    id: int
    product_id: int
    quantity: int
    total: Optional[float]

    class Config:
        from_attributes = True


# Inside Order
class OrderLines(BaseModel):
    id: int
    product_id: int
    quantity: int
    total: Optional[float]

    class Config:
        from_attributes = True


class Order(BaseModel):
    id: int
    order_status: OrderStatus
    user_id: int
    total: float = 0
    order_lines: List[OrderLines] = []

    class Config:
        from_attributes = True


class Review(BaseModel):
    score: int
    comment: str


# Username inside ReviewDisplay
class Username(BaseModel):
    username: str


class ReviewDisplay(BaseModel):
    id: int
    creator_id: int
    creator_username: Username
    product_id: int
    score: int
    comment: str
    product: ProductReview

    class Config:
        from_attributes = True


# Product inside UserProductDisplay
class Product(BaseModel):
    product_name: str
    id: int
    description: str
    price: float
    published: bool

    class Config:
        from_attributes = True


class UserProductDisplay(BaseModel):
    username: str
    email: str
    id: int
    products: List[Product] = []

    class Config:
        from_attributes = True


class LikeCreate(BaseModel):
    post_id: int
    user_id: int


class LikeResponse(BaseModel):
    message: str
    likes_count: int
    liked_by_user: bool
