"""
Notifications endpoints — list, mark read, dismiss.
"""
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy import select, and_, desc, func
import uuid

from app.core.dependencies import CurrentUser, DBSession
from app.models.models import Notification
from app.schemas.schemas import NotificationResponse, NotificationListResponse

router = APIRouter()


def _notif_to_response(n) -> NotificationResponse:
    return NotificationResponse(
        id=str(n.id), user_id=str(n.user_id),
        farm_id=str(n.farm_id) if n.farm_id else None,
        title=n.title, message=n.message, type=n.type,
        priority=n.priority, action_label=n.action_label,
        action_url=n.action_url, data=n.data or {},
        is_read=n.is_read, read_at=n.read_at,
        is_dismissed=n.is_dismissed, created_at=n.created_at,
    )


@router.get(
    "/",
    response_model=NotificationListResponse,
    summary="Get all notifications for the current user",
)
async def get_notifications(
    current_user: CurrentUser,
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
):
    """Return paginated notifications with unread count."""
    base_filter = and_(
        Notification.user_id == current_user.id,
        Notification.is_dismissed == False,
    )
    if unread_only:
        base_filter = and_(base_filter, Notification.is_read == False)

    # Count unread
    unread_result = await db.execute(
        select(func.count(Notification.id)).where(
            and_(
                Notification.user_id == current_user.id,
                Notification.is_read == False,
                Notification.is_dismissed == False,
            )
        )
    )
    unread_count = unread_result.scalar_one()

    # Fetch paginated
    result = await db.execute(
        select(Notification)
        .where(base_filter)
        .order_by(desc(Notification.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    notifications = list(result.scalars().all())

    # Total count
    total_result = await db.execute(
        select(func.count(Notification.id)).where(base_filter)
    )
    total = total_result.scalar_one()

    return NotificationListResponse(
        items=[_notif_to_response(n) for n in notifications],
        total=total,
        unread_count=unread_count,
    )


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationResponse,
    summary="Mark a notification as read",
)
async def mark_as_read(notification_id: str, current_user: CurrentUser, db: DBSession):
    """Mark a single notification as read."""
    result = await db.execute(
        select(Notification).where(
            and_(
                Notification.id == uuid.UUID(notification_id),
                Notification.user_id == current_user.id,
            )
        )
    )
    notification = result.scalar_one_or_none()
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    notification.is_read = True
    notification.read_at = datetime.now(timezone.utc)
    await db.flush()
    return _notif_to_response(notification)


@router.patch(
    "/read-all",
    summary="Mark all notifications as read",
)
async def mark_all_read(current_user: CurrentUser, db: DBSession):
    """Mark all unread notifications as read for the current user."""
    result = await db.execute(
        select(Notification).where(
            and_(
                Notification.user_id == current_user.id,
                Notification.is_read == False,
            )
        )
    )
    notifications = list(result.scalars().all())
    now = datetime.now(timezone.utc)
    for n in notifications:
        n.is_read = True
        n.read_at = now
    await db.flush()
    return {"marked_read": len(notifications)}


@router.patch(
    "/{notification_id}/dismiss",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Dismiss a notification",
)
async def dismiss_notification(notification_id: str, current_user: CurrentUser, db: DBSession):
    """Dismiss (hide) a notification from the user's feed."""
    result = await db.execute(
        select(Notification).where(
            and_(
                Notification.id == uuid.UUID(notification_id),
                Notification.user_id == current_user.id,
            )
        )
    )
    notification = result.scalar_one_or_none()
    if not notification:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    notification.is_dismissed = True
    notification.dismissed_at = datetime.now(timezone.utc)
    await db.flush()
