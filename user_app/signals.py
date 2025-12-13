from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Category, SubCategory, Tag, News, Comment, Like

@receiver([post_save, post_delete], sender=Category)
def clear_category_cache(sender, **kwargs):
    cache.incr("categories_version", ignore_key_check=True)

@receiver([post_save, post_delete], sender=SubCategory)
def clear_subcategory_cache(sender, **kwargs):
    cache.incr("subcategories_version", ignore_key_check=True)

@receiver([post_save, post_delete], sender=Tag)
def clear_tag_cache(sender, **kwargs):
    cache.incr("tags_version", ignore_key_check=True)

@receiver([post_save, post_delete], sender=News)
def clear_news_cache(sender, **kwargs):
    cache.incr("news_version", ignore_key_check=True)


@receiver([post_save, post_delete], sender=Comment)
def clear_comment_cache(sender, instance, **kwargs):
    news_id = instance.news_id
    cache.incr(f"comments_news_{news_id}_version", ignore_key_check=True)

@receiver(post_delete, sender=News)
def clear_comments_on_news_delete(sender, instance, **kwargs):
    cache.delete_pattern(f"comments_news_{instance.id}_*")

@receiver([post_save, post_delete], sender=Like)
def clear_likes_cache(sender, instance, **kwargs):
    cache.incr(
        f"likes_news_{instance.news_id}_version",
        ignore_key_check=True
    )
    