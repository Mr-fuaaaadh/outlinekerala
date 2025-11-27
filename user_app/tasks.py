"""
Async tasks for heavy operations
Uses Celery for background processing
"""
from celery import shared_task
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def process_profile_picture_task(self, user_id, image_path):
    """
    Process and optimize profile picture
    - Resize to 300x300
    - Optimize quality
    - Generate thumbnail
    """
    try:
        from user_app.models import CustomUser
        
        user = CustomUser.objects.get(id=user_id)
        
        if not user.profile_picture:
            return
        
        # Open image
        img = Image.open(user.profile_picture.path)
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize to 300x300
        img.thumbnail((300, 300), Image.Resampling.LANCZOS)
        
        # Save optimized image
        output = BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)
        
        # Update user profile picture
        user.profile_picture.save(
            user.profile_picture.name,
            ContentFile(output.read()),
            save=True
        )
        
        logger.info(f"Profile picture processed for user {user_id}")
        
    except Exception as exc:
        logger.error(f"Error processing profile picture for user {user_id}: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task
def send_welcome_email_task(user_id, username, email):
    """Send welcome email to new user"""
    try:
        subject = f"Welcome to Outline Kerala, {username}!"
        message = f"""
        Hi {username},
        
        Welcome to Outline Kerala! We're excited to have you on board.
        
        You can now:
        - Read the latest news
        - Comment on articles
        - Like your favorite stories
        
        Best regards,
        The Outline Kerala Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        
        logger.info(f"Welcome email sent to {email}")
        
    except Exception as exc:
        logger.error(f"Error sending welcome email to {email}: {exc}")


@shared_task
def send_comment_notification_task(news_id, commenter_username):
    """Notify news author about new comment"""
    try:
        from user_app.models import News
        
        news = News.objects.select_related('author').get(id=news_id)
        
        if not news.author or not news.author.email:
            return
        
        subject = f"New comment on your article: {news.title}"
        message = f"""
        Hi {news.author.username},
        
        {commenter_username} just commented on your article "{news.title}".
        
        Check it out at: {settings.SITE_URL}/news/{news.slug}
        
        Best regards,
        The Outline Kerala Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [news.author.email],
            fail_silently=True,
        )
        
        logger.info(f"Comment notification sent to {news.author.email}")
        
    except Exception as exc:
        logger.error(f"Error sending comment notification for news {news_id}: {exc}")


@shared_task
def generate_news_thumbnail_task(news_id):
    """Generate thumbnail for news image"""
    try:
        from user_app.models import News
        
        news = News.objects.get(id=news_id)
        
        if not news.image:
            return
        
        # Open image
        img = Image.open(news.image.path)
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Create thumbnail (600x400)
        img.thumbnail((600, 400), Image.Resampling.LANCZOS)
        
        # Save thumbnail
        output = BytesIO()
        img.save(output, format='JPEG', quality=90, optimize=True)
        output.seek(0)
        
        # Save with _thumb suffix
        thumb_name = f"thumb_{news.image.name.split('/')[-1]}"
        news.image.save(
            thumb_name,
            ContentFile(output.read()),
            save=False
        )
        news.save()
        
        logger.info(f"Thumbnail generated for news {news_id}")
        
    except Exception as exc:
        logger.error(f"Error generating thumbnail for news {news_id}: {exc}")
