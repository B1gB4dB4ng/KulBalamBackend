from typing import List
from db.models import DbPost, DbUser, PostLike
from schemas import PostBase, PostDisplay, PostImage, PostUpdate, UserBase
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from db.database import get_db
from db import db_post, db_user, db_post_images
from auth.oauth2 import get_current_user
from datetime import datetime

router = APIRouter(tags=["userwall"])


@router.post("/posts")
def create_post(content: str, user_id: int, db: Session = Depends(get_db)):
    # Fetch the username associated with the provided user_id
    username = db_user.get_username(db=db, user_id=user_id)
    if not username:
        raise HTTPException(status_code=404, detail="User not found")

    # Create the post with the provided user_id and fetched username
    new_post = db_post.create_post(
        db=db,
        request=PostBase(
            content=content,
            user_id=user_id,
            username=username,
            timestamp=datetime.now(),
        ),
    )
    return new_post


# Inert image
@router.post("/posts/{id}/images", response_model=PostImage)
def upload_post_image(
    id: int, image: UploadFile = File(...), db: Session = Depends(get_db)
):
    return db_post_images.upload_post_image(db, id, image)


# This endpoint is used to retrieve posts # Get all posts from User
@router.get("/posts/all", response_model=List[PostDisplay])
def get_all_posts(
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user),
):
    # Get all posts
    posts = db.query(DbPost).all()

    # Get all likes by current user in one query
    user_liked_post_ids = {
        like.post_id
        for like in db.query(PostLike.post_id)
        .filter(PostLike.user_id == current_user.id)
        .all()
    }

    result = []
    for post in posts:
        post_data = {
            "id": post.id,
            "content": post.content,
            "user": post.user,  # Assuming this relationship exists
            "user_id": post.user_id,
            "timestamp": post.timestamp,
            "likes_count": getattr(post, "like_count", 0),
            "liked_by_user": post.id in user_liked_post_ids,
            "images": getattr(post, "images", []),
        }
        result.append(PostDisplay(**post_data))

    return result


@router.get("/posts/{id}", response_model=PostDisplay)
def get_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user),
):
    post = db.query(DbPost).filter(DbPost.id == id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Check if current user liked this specific post
    liked_by_user = (
        db.query(PostLike)
        .filter(PostLike.post_id == post.id, PostLike.user_id == current_user.id)
        .first()
        is not None
    )

    post_data = {
        "id": post.id,
        "content": post.content,
        "user": post.user,
        "user_id": post.user_id,
        "timestamp": post.timestamp,
        "likes_count": getattr(post, "like_count", 0),
        "liked_by_user": liked_by_user,
        "images": getattr(post, "images", []),
    }

    return PostDisplay(**post_data)


# Update Post
@router.put("/posts/{id}", response_model=PostDisplay)
def update_post(
    id: int,
    request: PostUpdate,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    # Check if the post exists
    post = db_post.get_post(db, id)
    if not post:
        raise HTTPException(status_code=404, detail=f"Post with id {id} not found")

    # Update the post content and image_url
    post = db_post.update_post(db, id, request)

    return post


# Delete Post
@router.delete("/posts/{id}")
def delete_post(id: int, db: Session = Depends(get_db)):
    return db_post.delete_post(db, id)


@router.get("/postimages/{id}")
def get_image(id: int, db: Session = Depends(get_db)):
    return db_post_images.get_post_image(db, id)


@router.delete("/postimages/{id}")
def delete_image(id: int, db: Session = Depends(get_db)):
    return db_post_images.delete_post_image(db, id)
