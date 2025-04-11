# app/routers/post_likes.py
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Response,
    status as STATUS,
)
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import DbPost, DbUser, PostLike
from auth.oauth2 import get_current_user
from schemas import LikeCreate, LikeResponse
from db.db_like import get_likes_count_db, like_post_db, unlike_post_db


router = APIRouter(prefix="/likes", tags=["Post Likes"])


@router.post(
    "/",
    response_model=LikeResponse,
    status_code=STATUS.HTTP_201_CREATED,
)
def like_post(
    request: LikeCreate,
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user),
):
    """
    Like another user's post.
    - Checks ownership and existing likes in DB layer
    - Checks if user is trying to like their own post
    - Checks if user is trying to like a post on behalf of another user
    """

    if request.user_id != current_user.id:
        raise HTTPException(
            status_code=STATUS.HTTP_403_FORBIDDEN,
            detail="You cannot like a post on behalf of another user",
        )

    post = db.query(DbPost).filter(DbPost.id == request.post_id).first()
    if not post:
        raise HTTPException(
            status_code=STATUS.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    # Check if user is trying to like their own post
    if post.user_id == request.user_id:
        raise HTTPException(
            status_code=STATUS.HTTP_403_FORBIDDEN,
            detail="Cannot like your own post",
        )

    # Check for existing like
    if (
        db.query(PostLike)
        .filter(
            PostLike.post_id == request.post_id, PostLike.user_id == request.user_id
        )
        .first()
    ):
        raise HTTPException(
            status_code=STATUS.HTTP_409_CONFLICT, detail="Post already liked"
        )

    # Database operation
    like_post_db(db, request.post_id, request.user_id)

    # Get updated counts
    likes_count = get_likes_count_db(db, request.post_id)

    return LikeResponse(
        message="Post liked successfully", likes_count=likes_count, liked_by_user=True
    )


@router.delete(
    "/{like_id}",
    status_code=STATUS.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Successfully unliked the post"},
        404: {"description": "Like not found"},
        403: {"description": "Not authorized to unlike this post"},
    },
)
def unlike_post(
    like_id: int = Path(..., description="The ID of the like to remove", gt=0),
    db: Session = Depends(get_db),
    current_user: DbUser = Depends(get_current_user),
):
    """
    Unlike a post you've previously liked.

    - Checks if the like exists
    - Verifies the like belongs to current user
    - Deletes the like record
    - Returns 204 No Content on success
    """
    # First get the like without user_id filter to properly check ownership
    like = db.query(PostLike).filter(PostLike.id == like_id).first()

    if not like:
        raise HTTPException(
            status_code=STATUS.HTTP_404_NOT_FOUND, detail="Like not found"
        )

    # Now verify ownership
    if like.user_id != current_user.id:
        raise HTTPException(
            status_code=STATUS.HTTP_403_FORBIDDEN,
            detail="You can only remove your own likes",
        )

    # Database operation - simplified since we've already verified everything
    unlike_post_db(db, like.post_id, current_user.id)

    return Response(status_code=STATUS.HTTP_204_NO_CONTENT)
