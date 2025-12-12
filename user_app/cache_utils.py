"""
Cache utilities for GraphQL API
Provides cache key generation and invalidation functions
"""
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

# Cache timeouts
CACHE_TIMEOUT_SHORT = 300  # 5 minutes
CACHE_TIMEOUT_MEDIUM = 1800  # 30 minutes
CACHE_TIMEOUT_LONG = 3600  # 1 hour

# ==================== Cache Key Generators ====================

def get_news_cache_key(page=1, page_size=10):
    """Generate cache key for news list"""
    return f"news_page_{page}_size_{page_size}"

def get_news_detail_cache_key(news_id):
    """Generate cache key for single news item"""
    return f"news_detail_{news_id}"

def get_category_cache_key(page=1, page_size=10):
    """Generate cache key for categories list"""
    return f"categories_page_{page}_size_{page_size}"

def get_subcategory_cache_key(page=1, page_size=10):
    """Generate cache key for subcategories list"""
    return f"subcategories_page_{page}_size_{page_size}"

def get_subcategory_news_cache_key(subcategory_id, page=1):
    """Generate cache key for news by subcategory"""
    return f"subcategory_{subcategory_id}_news_page_{page}"

def get_category_subcategories_cache_key(category_id, page=1):
    """Generate cache key for subcategories by category"""
    return f"category_{category_id}_subcategories_page_{page}"

def get_comments_cache_key(news_id, page=1):
    """Generate cache key for comments"""
    return f"comments_news_{news_id}_page_{page}"

def get_tags_cache_key(page=1, page_size=10):
    """Generate cache key for tags"""
    return f"tags_page_{page}_size_{page_size}"

def get_news_likes_count_cache_key(news_id):
    """Generate cache key for news likes count"""
    return f"news_{news_id}_likes_count"

def get_news_comments_count_cache_key(news_id):
    """Generate cache key for news comments count"""
    return f"news_{news_id}_comments_count"

def get_news_tags_cache_key(news_id):
    """Generate cache key for news tags"""
    return f"news_{news_id}_tags"

def get_user_cache_key(user_id):
    """Generate cache key for user profile"""
    return f"user_profile_{user_id}"

# ==================== Cache Key Generators ====================

def get_wards_cache_key(page=1, page_size=10):
    """Generate cache key for wards list"""
    return f"wards_page_{page}_size_{page_size}"

# ==================== Cache Invalidation Functions ====================

def invalidate_news_list_cache():
    """Invalidate all news list caches"""
    logger.info("Invalidating news list cache")
    # Invalidate common page sizes
    for page in range(1, 11):  # First 10 pages
        for page_size in [10, 20, 50]:
            cache.delete(get_news_cache_key(page, page_size))

def invalidate_news_detail_cache(news_id):
    """Invalidate cache for specific news item"""
    logger.info(f"Invalidating news detail cache for news_id={news_id}")
    cache.delete(get_news_detail_cache_key(news_id))
    cache.delete(get_news_likes_count_cache_key(news_id))
    cache.delete(get_news_comments_count_cache_key(news_id))
    cache.delete(get_news_tags_cache_key(news_id))

def invalidate_news_cache(news_id=None):
    """Invalidate news caches (list and/or detail)"""
    invalidate_news_list_cache()
    if news_id:
        invalidate_news_detail_cache(news_id)

def invalidate_comments_cache(news_id):
    """Invalidate comments cache for a news item"""
    logger.info(f"Invalidating comments cache for news_id={news_id}")
    # Invalidate first few pages of comments
    for page in range(1, 6):
        cache.delete(get_comments_cache_key(news_id, page))
    
    # Also invalidate news comments count
    cache.delete(get_news_comments_count_cache_key(news_id))

def invalidate_likes_cache(news_id):
    """Invalidate likes cache for a news item"""
    logger.info(f"Invalidating likes cache for news_id={news_id}")
    cache.delete(get_news_likes_count_cache_key(news_id))

def invalidate_category_cache():
    """Invalidate category list cache"""
    logger.info("Invalidating category cache")
    for page in range(1, 11):
        for page_size in [10, 20, 50]:
            cache.delete(get_category_cache_key(page, page_size))

def invalidate_subcategory_cache(category_id=None):
    """Invalidate subcategory caches"""
    logger.info(f"Invalidating subcategory cache for category_id={category_id}")
    # Invalidate subcategory list
    for page in range(1, 11):
        for page_size in [10, 20, 50]:
            cache.delete(get_subcategory_cache_key(page, page_size))
    
    # Invalidate category's subcategories if category_id provided
    if category_id:
        for page in range(1, 6):
            cache.delete(get_category_subcategories_cache_key(category_id, page))

def invalidate_tags_cache():
    """Invalidate tags cache"""
    logger.info("Invalidating tags cache")
    for page in range(1, 11):
        for page_size in [10, 20, 50]:
            cache.delete(get_tags_cache_key(page, page_size))

def invalidate_user_cache(user_id):
    """Invalidate user profile cache"""
    logger.info(f"Invalidating user cache for user_id={user_id}")
    cache.delete(get_user_cache_key(user_id))

# ==================== Bulk Invalidation ====================

def invalidate_all_caches():
    """Nuclear option: clear all caches"""
    logger.warning("Clearing ALL caches")
    cache.clear()
