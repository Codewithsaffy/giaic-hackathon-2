from uuid import UUID
from typing import List, Annotated, Optional, Any
from fastapi import APIRouter, Depends, status, Request, HTTPException
from sqlmodel import Session, select

from src.shared.models import Notification, NotificationType, User
from src.shared.exceptions import NotFoundException, ConflictException

router = APIRouter(prefix="/notifications", tags=["notifications"])


# Dependency for database session (will be provided by main app)
def get_session():
    # This will be overridden by dependency injection in the main FastAPI app
    with Session() as session:
        yield session


# Dependency for current user (placeholder for authentication)
def get_current_user() -> User:
    # Placeholder for actual authentication logic
    # In a real app, this would get the user from a JWT token or similar
    # For now, return a dummy user. Replace with actual auth later.
    return User(id=UUID("00000000-0000-0000-0000-000000000001"), username="testuser", email="test@example.com")


# --- Notification Endpoints ---

@router.post("/", response_model=Notification, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notification: Notification,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """
    Creates a new notification.
    """
    notification.user_id = current_user.id
    session.add(notification)
    session.commit()
    session.refresh(notification)
    return notification


@router.get("/{notification_id}", response_model=Notification, status_code=status.HTTP_200_OK)
async def get_notification(
    notification_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """
    Retrieves a notification by its ID.
    """
    notification = session.exec(
        select(Notification).where(Notification.id == notification_id, Notification.user_id == current_user.id)
    ).first()
    if not notification:
        raise NotFoundException(detail=f"Notification with id {notification_id} not found.")
    return notification


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """
    Deletes a notification.
    """
    notification = session.exec(
        select(Notification).where(Notification.id == notification_id, Notification.user_id == current_user.id)
    ).first()
    if not notification:
        raise NotFoundException(detail=f"Notification with id {notification_id} not found.")

    session.delete(notification)
    session.commit()
    return {"message": "Notification deleted successfully."}


@router.get("/", response_model=List[Notification], status_code=status.HTTP_200_OK)
async def get_all_notifications(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)],
    status_filter: Optional[str] = None,
    type_filter: Optional[NotificationType] = None,
):
    """
    Retrieves all notifications for the current user, with optional filtering by status and type.
    """
    statement = select(Notification).where(Notification.user_id == current_user.id)
    if status_filter:
        statement = statement.where(Notification.status == status_filter)
    if type_filter:
        statement = statement.where(Notification.type == type_filter)
    notifications = session.exec(statement).all()
    return notifications
