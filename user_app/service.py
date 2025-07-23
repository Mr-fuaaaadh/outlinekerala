from django.contrib.auth import authenticate
from graphql import GraphQLError
from .models import *
from django.contrib.auth import update_session_auth_hash
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.auth import get_user_model
from graphql_jwt.utils import jwt_encode, jwt_payload


User = get_user_model()

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
    print(f"Attempting to authenticate user: {username}")
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




from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from graphql import GraphQLError

class UserService:
    @staticmethod
    def update_user_profile(user, username=None, email=None, bio=None, password=None, profile_picture=None):
        sensitive_change = False
        username_changed = False
        password_changed = False

        # ✅ Username update
        if username and username != user.username:
            if user.__class__.objects.filter(username=username).exclude(id=user.id).exists():
                raise GraphQLError("Username already taken.")
            user.username = username
            sensitive_change = True
            username_changed = True

        # ✅ Email update
        if email and email != user.email:
            if user.__class__.objects.filter(email=email).exclude(id=user.id).exists():
                raise GraphQLError("Email already in use.")
            user.email = email

        # ✅ Bio update
        if bio is not None:
            user.bio = bio

        # ✅ Password update
        if password:
            user.set_password(password)
            sensitive_change = True
            password_changed = True

        # ✅ Profile picture update
        print(f"Profile picture received: {profile_picture} (type: {type(profile_picture)})")  # Debug print

        if profile_picture and isinstance(profile_picture, (InMemoryUploadedFile, TemporaryUploadedFile)):
            user.profile_picture = profile_picture

        user.save()

        # ✅ JWT Token
        token = jwt_encode(jwt_payload(user)) if sensitive_change else None

        # ✅ Message Logic
        if username_changed and password_changed:
            message = "Username and password updated. Please log in again."
        elif username_changed:
            message = "Username updated. Please log in again."
        elif password_changed:
            message = "Password updated. Please log in again."
        else:
            message = "Profile updated successfully."

        return user, token, message

    
    @staticmethod
    def admin_update_user_profile(user, user_id, username=None, email=None, role=None, bio=None, profile_picture=None):
        if user.role != 'admin':
            raise GraphQLError("You do not have permission to update user profiles.")

        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise GraphQLError("User not found.")

        if username:
            if User.objects.filter(username=username).exclude(id=target_user.id).exists():
                raise GraphQLError("Username already taken.")
            target_user.username = username

        if email:
            if User.objects.filter(email=email).exclude(id=target_user.id).exists():
                raise GraphQLError("Email already in use.")
            target_user.email = email

        if role:
            target_user.role = role

        if bio is not None:
            target_user.bio = bio

        if profile_picture:
            target_user.profile_picture = profile_picture

        target_user.save()

        return target_user, "User profile updated successfully."
    


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