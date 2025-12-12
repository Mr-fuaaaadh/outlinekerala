from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Category, SubCategory, Tag

@receiver([post_save, post_delete], sender=Category)
def clear_category_cache(sender, **kwargs):
    cache.delete("categories")

@receiver([post_save, post_delete], sender=SubCategory)
def clear_subcategory_cache(sender, **kwargs):
    cache.delete("subcategories")

@receiver([post_save, post_delete], sender=Tag)
def clear_tag_cache(sender, **kwargs):
    cache.delete("tags")



