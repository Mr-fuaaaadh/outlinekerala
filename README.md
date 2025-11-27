# Outline Kerala - Production-Ready GraphQL News API

A high-performance Django GraphQL API for news management with advanced optimization features.

## 🚀 Features

### Core Functionality
- **User Management**: Registration, authentication (JWT), profile management
- **News System**: Create, read, update news articles with rich text content
- **Categories & Tags**: Hierarchical categorization with subcategories
- **Social Features**: Comments, likes, user interactions
- **Admin Panel**: Bulk import/export with django-import-export

### Performance Optimizations
- ✅ **Smart Caching**: Redis-based caching with automatic invalidation
- ✅ **Query Optimization**: `select_related`, `prefetch_related`, `only()`, `defer()`
- ✅ **DataLoaders**: Batch loading for comments and likes (N+1 prevention)
- ✅ **Pagination**: Offset-based pagination for all list queries
- ✅ **Async Tasks**: Celery for image processing and email notifications
- ✅ **Performance Monitoring**: Query timing, N+1 detection, slow query logging
- ✅ **Query Complexity Limits**: Prevent expensive nested queries

## 📋 Prerequisites

- Python 3.10+
- PostgreSQL 12+
- Redis 6+
- Node.js 16+ (for frontend, optional)

## 🛠️ Installation

### 1. Clone and Setup Environment

```bash
git clone https://github.com/yourusername/outlinekerala.git
cd outlinekerala

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Install Additional Dependencies

```bash
pip install celery[redis]
pip install Pillow  # For image processing
pip install graphene-django-optimizer  # Optional: automatic query optimization
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb outlinekerala_db

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 4. Redis Setup

```bash
# Install Redis (Ubuntu/Debian)
sudo apt-get install redis-server

# Start Redis
redis-server

# Verify Redis is running
redis-cli ping  # Should return PONG
```

### 5. Environment Configuration

Create `.env` file:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgresql://postgres:password@localhost:5432/outlinekerala_db
REDIS_URL=redis://127.0.0.1:6379/1
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
```

### 6. Run Development Server

```bash
# Terminal 1: Django server
python manage.py runserver

# Terminal 2: Celery worker
celery -A outlinekerala worker -l info

# Terminal 3: Celery beat (for scheduled tasks, optional)
celery -A outlinekerala beat -l info
```

## 📊 GraphQL API

### Endpoint
```
http://localhost:8000/graphql/
```

### Example Queries

#### Get News List (Paginated)
```graphql
query {
  newses(page: 1, pageSize: 10) {
    id
    title
    slug
    publishDate
    author {
      username
    }
    category {
      name
    }
    tags {
      name
    }
    likesCount
    commentsCount
  }
}
```

#### Get Single News with Comments
```graphql
query {
  news(id: 1) {
    id
    title
    content
    image
    author {
      username
      profilePictureUrl
    }
    comments {
      id
      content
      user {
        username
      }
      createdAt
    }
  }
}
```

#### Create Comment
```graphql
mutation {
  commentNews(newsId: 1, content: "Great article!") {
    comment {
      id
      content
      user {
        username
      }
    }
  }
}
```

#### Like News
```graphql
mutation {
  likeNews(newsId: 1) {
    liked
    like {
      id
    }
  }
}
```

## 🔧 Configuration

### Cache Settings

Cache timeouts can be configured in `user_app/cache_utils.py`:

```python
CACHE_TIMEOUT_SHORT = 300  # 5 minutes
CACHE_TIMEOUT_MEDIUM = 1800  # 30 minutes
CACHE_TIMEOUT_LONG = 3600  # 1 hour
```

### Query Performance Limits

Configure in `settings.py`:

```python
GRAPHQL_QUERY_MAX_DEPTH = 5
GRAPHQL_QUERY_MAX_COMPLEXITY = 1000
```

### Celery Tasks

Available async tasks:
- `process_profile_picture_task`: Resize and optimize profile images
- `send_welcome_email_task`: Send welcome email to new users
- `send_comment_notification_task`: Notify authors of new comments
- `generate_news_thumbnail_task`: Generate thumbnails for news images

## 📈 Performance Monitoring

### Logging

Logs are written to:
- `logs/django.log`: General application logs
- `logs/graphql.log`: GraphQL query performance logs

### Slow Query Detection

Queries taking > 1000ms are automatically logged as warnings.

### N+1 Query Detection

Resolvers executing > 10 database queries trigger warnings.

## 🧪 Testing

```bash
# Run tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

## 🚀 Production Deployment

### 1. Update Settings

```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']

# Use production cache backend
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://your-redis-server:6379/1",
    }
}

# Configure email backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
```

### 2. Collect Static Files

```bash
python manage.py collectstatic
```

### 3. Run with Gunicorn

```bash
pip install gunicorn
gunicorn outlinekerala.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### 4. Setup Celery as Service

Create systemd service files for Celery worker and beat.

## 📦 Dependencies

Core:
- Django 5.1+
- graphene-django
- django-graphql-jwt
- django-redis
- celery[redis]
- Pillow
- psycopg2-binary

Optional:
- graphene-django-optimizer
- django-silk (for query profiling)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- Django community
- Graphene-Python team
- Contributors and testers