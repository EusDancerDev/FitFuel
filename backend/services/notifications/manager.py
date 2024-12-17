from typing import Dict, List, Optional
import logging
omeVirewfrom datetime import datetime, timedelta
from ...database.models import User, Notification, NotificationType
from ...config import settings
from ..ai.llm_manager import LLMManager

logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self, db_session, llm_manager: LLMManager):
        self.db = db_session
        self.llm = llm_manager
        self.notification_cooldown = settings.NOTIFICATION_COOLDOWN_MINUTES
        self.max_daily_notifications = settings.MAX_DAILY_NOTIFICATIONS

    async def create_notification(
        self,
        user_id: int,
        notification_type: NotificationType,
        content: Dict,
        priority: int = 1
    ) -> Dict:
        """Create and send a new notification"""
        try:
            # Check notification limits
            if not await self._can_send_notification(user_id):
                logger.info(f"Notification limit reached for user {user_id}")
            return {
                    "success": False,
                    "error": "Notification limit reached"
                }

            # Enhance notification content with AI
            enhanced_content = await self._enhance_content(
                content,
                notification_type
            )

            # Create notification record
            notification = await self._create_notification_record(
                user_id,
                notification_type,
                enhanced_content,
                priority
            )

            # Send notification
            send_result = await self._send_notification(notification)

            if send_result["success"]:
            return {
                "success": True,
                "notification_id": notification.id,
                    "sent_at": notification.created_at.isoformat()
            }
            else:
                raise ValueError(send_result["error"])

        except Exception as e:
            logger.error(f"Error creating notification: {str(e)}")
                return {
                    "success": False,
                "error": str(e)
            }

    async def _can_send_notification(self, user_id: int) -> bool:
        """Check if notification can be sent based on limits"""
        try:
            # Check cooldown
            latest_notification = await self.db.query(Notification).filter(
                Notification.user_id == user_id
            ).order_by(
                Notification.created_at.desc()
            ).first()

            if latest_notification:
                cooldown_time = latest_notification.created_at + timedelta(
                    minutes=self.notification_cooldown
                )
                if datetime.now() < cooldown_time:
                return False

            # Check daily limit
            today_count = await self.db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.created_at >= datetime.now().date()
            ).count()

            return today_count < self.max_daily_notifications

        except Exception as e:
            logger.error(f"Error checking notification limits: {str(e)}")
            return False

    async def _enhance_content(
        self,
        content: Dict,
        notification_type: NotificationType
    ) -> Dict:
        """Enhance notification content using LLM"""
        try:
            prompt = self._create_enhancement_prompt(
                content,
                notification_type
            )

            result = await self.llm.process_request(
                prompt=prompt,
                context={
                    "notification_type": notification_type,
                    "original_content": content
                }
            )

            return result.get("enhanced_content", content)

        except Exception as e:
            logger.error(f"Error enhancing content: {str(e)}")
            return content

    def _create_enhancement_prompt(
        self,
        content: Dict,
        notification_type: NotificationType
    ) -> str:
        """Create prompt for content enhancement"""
        return f"""Enhance this notification content:
        Type: {notification_type}
        Content: {content}
        
        Requirements:
        1. Keep message clear and concise
        2. Use engaging but professional tone
        3. Include actionable information
        4. Maintain original meaning
        5. Optimize for mobile display
        
        Return enhanced content in JSON format."""

    async def _create_notification_record(
        self,
        user_id: int,
        notification_type: NotificationType,
        content: Dict,
        priority: int
    ) -> Notification:
        """Create notification record in database"""
        try:
            notification = Notification(
                user_id=user_id,
                type=notification_type,
                content=content,
                priority=priority,
                created_at=datetime.now()
            )
            
            self.db.add(notification)
            await self.db.commit()
            await self.db.refresh(notification)
            
            return notification

        except Exception as e:
            logger.error(f"Error creating notification record: {str(e)}")
            await self.db.rollback()
            raise

    async def _send_notification(self, notification: Notification) -> Dict:
        """Send notification through appropriate channel"""
        try:
            user = await self.db.query(User).filter(
                User.id == notification.user_id
            ).first()

            if not user:
                raise ValueError(f"User not found: {notification.user_id}")

            # Send based on user preferences
            if user.notification_preferences.get("push_enabled", True):
                await self._send_push_notification(notification, user)

            if user.notification_preferences.get("email_enabled", False):
                await self._send_email_notification(notification, user)

            return {"success": True}

        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _send_push_notification(
        self,
        notification: Notification,
        user: User
    ) -> None:
        """Send push notification"""
        # Implementation for push notification
        pass

    async def _send_email_notification(
        self,
        notification: Notification,
        user: User
    ) -> None:
        """Send email notification"""
        # Implementation for email notification
        pass 