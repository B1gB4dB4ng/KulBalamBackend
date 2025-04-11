# crud.py
from sqlalchemy.orm.session import Session
from db.models import DbPost, DbUser, PostLike
from schemas import PostBase, PostUpdate
from fastapi import HTTPException, Response, status
import datetime
from typing import List


def create_post(db: Session, request: PostBase):
    new_post = DbPost(
        content=request.content,
        user_id=request.user_id,
        username=request.username,
        timestamp=datetime.datetime.now(),
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


def get_all(db: Session) -> List[DbPost]:
    posts = db.query(DbPost).all()
    return posts


def get_post(db: Session, id: int):
    post = db.query(DbPost).filter(DbPost.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found"
        )  # stop the code running
    return post


"""def get_posts_by_user(db: Session, user_id: int) -> List[DbPost]:
    user_posts = db.query(DbPost).filter(DbPost.user_id == user_id).all()
    if not user_posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No posts found for user with ID {user_id}")
    return user_posts """


def update_post(
    db: Session, id: int, request: PostUpdate
):  # Update post function now accepts PostUpdate model
    post = db.query(DbPost).filter(DbPost.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found"
        )

    # Update the post content and image_url if provided
    post.content = request.content
    post.image_url = request.image_url

    db.commit()
    return post


def delete_post(db: Session, id: int):
    post = db.query(DbPost).filter(DbPost.id == id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {id} not found"
        )
    db.delete(post)
    db.commit()
    return Response(status_code=204)


def check_user_liked_post(db: Session, post_id: int, user_id: int) -> bool:
    """Check if a user has liked a specific post"""
    return (
        db.query(PostLike)
        .filter(PostLike.post_id == post_id, PostLike.user_id == user_id)
        .first()
        is not None
    )
