from sqlalchemy.orm import Session
from datetime import datetime
from db.models import DbPost, PostLike


def like_post_db(db: Session, post_id: int, user_id: int):
    # Create and commit the like
    new_like = PostLike(post_id=post_id, user_id=user_id, created_at=datetime.utcnow())
    db.query(DbPost).filter(DbPost.id == post_id).update(
        {DbPost.like_count: DbPost.like_count + 1}
    )
    db.add(new_like)
    db.commit()
    return new_like


def unlike_post_db(db: Session, post_id: int, user_id: int):
    """Handles the database operations for unliking a post."""
    like = (
        db.query(PostLike)
        .filter(PostLike.post_id == post_id, PostLike.user_id == user_id)
        .first()
    )
    db.query(DbPost).filter(DbPost.id == post_id).update(
        {DbPost.like_count: DbPost.like_count - 1}
    )

    db.delete(like)
    db.commit()
    return


def get_likes_count_db(db: Session, post_id: int) -> int:
    """Returns the total like count for a post."""
    return db.query(PostLike).filter(PostLike.post_id == post_id).count()
