from django.contrib.auth import authenticate
from graphql import GraphQLError
from .models import *
from django.contrib.auth import get_user_model
from graphql_jwt.utils import jwt_encode, jwt_payload


User = get_user_model()

class AuthService:
    @staticmethod
    def register_user(username, email, password, role, bio=""):
        if User.objects.filter(username=username).exists():
            raise GraphQLError("Username already exists.")

        if User.objects.filter(email=email).exists():
            raise GraphQLError("Email already registered.")

        user = User(username=username, email=email, role=role, bio=bio)
        user.set_password(password)
        user.save()

        token = jwt_encode(jwt_payload(user))
        return user, token

    @staticmethod
    def login_user(username, password):
        user = authenticate(username=username, password=password)

        if user is None:
            raise GraphQLError("Invalid username or password.")

        if not user.is_active:
            raise GraphQLError("User account is inactive.")

        token = jwt_encode(jwt_payload(user))
        return user, token
    


class CommentService:
    @staticmethod
    def validate_user(user):
        if not user or not user.is_authenticated:
            raise GraphQLError("Authentication required to add a comment.")

    @staticmethod
    def get_news(news_id):
        try:
            return News.objects.get(id=news_id)
        except News.DoesNotExist:
            raise GraphQLError("The specified news article was not found.")

    @staticmethod
    def get_parent_comment(parent_id, news_id):
        try:
            parent = Comment.objects.get(id=parent_id)
            if parent.news_id != news_id:
                raise GraphQLError("Parent comment does not belong to the same news article.")
            return parent
        except Comment.DoesNotExist:
            raise GraphQLError("Parent comment not found.")

    @staticmethod
    def create_comment(news, user, content, parent=None):
        if not content.strip():
            raise GraphQLError("Comment content cannot be empty.")

        try:
            comment = Comment(
                news=news,
                user=user,
                content=content.strip(),
                parent=parent
            )
            comment.save()
            return comment
        except Exception as e:
            raise GraphQLError(f"Failed to add comment: {str(e)}")




class UserService:
    @staticmethod
    def update_user_profile(user, username=None, email=None, bio=None, password=None, profile_picture=None):
        sensitive_change = False

        if username:
            if User.objects.filter(username=username).exclude(id=user.id).exists():
                raise GraphQLError("Username already taken.")
            user.username = username
            sensitive_change = True

        if email:
            if User.objects.filter(email=email).exclude(id=user.id).exists():
                raise GraphQLError("Email already in use.")
            user.email = email

        if bio is not None:
            user.bio = bio

        if password:
            user.set_password(password)
            sensitive_change = True

        if profile_picture:
            user.profile_picture = profile_picture

        user.save()

        token = jwt_encode(jwt_payload(user)) if sensitive_change else None
        return user, token
    


class AuthService:
    @staticmethod
    def logout_user(user):
        if not user or not user.is_authenticated:
            raise GraphQLError("User is not authenticated.")
        # For session-based auth: logout(request)
        # For JWT: Optionally blacklist token (if supported)
        return True
    


class LikeService:
    @staticmethod
    def toggle_like(user, news_id):
        if not user or not user.is_authenticated:
            raise GraphQLError("Authentication required to like/unlike a news article.")

        try:
            news = News.objects.get(id=news_id)
        except News.DoesNotExist:
            raise GraphQLError("The specified news article was not found.")

        like = Like.objects.filter(user=user, news=news).first()

        if like:
            like.delete()
            return None, False
        else:
            new_like = Like.objects.create(user=user, news=news)
            return new_like, True