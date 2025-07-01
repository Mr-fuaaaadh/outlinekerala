import graphene
from django.contrib.auth import get_user_model
from graphql_jwt.shortcuts import get_token
from graphql import GraphQLError
from .type import UserType, CategoryType, TagType , NewsType, CommentType, LikeType, SubCategoryType
from .models import Category, Tag ,News, Comment, Like, SubCategory
from django.contrib.auth import authenticate
from graphql_jwt.utils import jwt_encode, jwt_payload

import base64
import uuid
from django.core.files.base import ContentFile
from graphene_file_upload.scalars import Upload
from graphql_jwt.decorators import login_required

User = get_user_model()

class RegisterUser(graphene.Mutation):
    user = graphene.Field(UserType)
    token = graphene.String()

    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        role = graphene.String(default_value="reader")
        bio = graphene.String()

    def mutate(self, info, username, email, password, role, bio=None):
        if User.objects.filter(username=username).exists():
            raise GraphQLError("Username already exists.")
        if User.objects.filter(email=email).exists():
            raise GraphQLError("Email already registered.")

        user = User(
            username=username,
            email=email,
            role=role,
            bio=bio or ""
        )
        user.set_password(password)
        user.save()

        token = get_token(user)

        return RegisterUser(user=user, token=token)

class LoginUser(graphene.Mutation):
    user = graphene.Field(UserType)
    token = graphene.String()

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, username, password):
        user = authenticate(username=username, password=password)

        if user is None:
            raise GraphQLError("Invalid username or password.")

        if not user.is_active:
            raise GraphQLError("User account is inactive.")

        # Generate JWT token
        payload = jwt_payload(user)
        token = jwt_encode(payload)

        return LoginUser(user=user, token=token)
    
class CommentNews(graphene.Mutation):
    comment = graphene.Field(CommentType)

    class Arguments:
        news_id = graphene.Int(required=True)
        content = graphene.String(required=True)
        parent_id = graphene.Int()

    def mutate(self, info, news_id, content, parent_id=None):
        user = info.context.user

        if not user or not user.is_authenticated:
            raise GraphQLError("Authentication required to add a comment.")

        if not content.strip():
            raise GraphQLError("Comment content cannot be empty.")

        try:
            news = News.objects.get(id=news_id)
        except News.DoesNotExist:
            raise GraphQLError("The specified news article was not found.")

        parent = None
        if parent_id is not None:
            try:
                parent = Comment.objects.get(id=parent_id)
                if parent.news_id != news_id:
                    raise GraphQLError("Parent comment does not belong to the same news article.")
            except Comment.DoesNotExist:
                raise GraphQLError("Parent comment not found.")

        try:
            comment = Comment(
                news=news,
                user=user,
                content=content.strip(),
                parent=parent
            )
            comment.save()
        except Exception as e:
            raise GraphQLError(f"Failed to add comment: {str(e)}")

        return CommentNews(comment=comment)



class UpdateUserProfile(graphene.Mutation):
    user = graphene.Field(UserType)
    token = graphene.String()

    class Arguments:
        username = graphene.String()
        email = graphene.String()
        bio = graphene.String()
        password = graphene.String()
        profile_picture = Upload()

    @login_required
    def mutate(self, info, username=None, email=None, bio=None, password=None, profile_picture=None):
        user = info.context.user

        if username and User.objects.filter(username=username).exclude(id=user.id).exists():
            raise GraphQLError("Username already taken.")
        if username:
            user.username = username

        if email and User.objects.filter(email=email).exclude(id=user.id).exists():
            raise GraphQLError("Email already in use.")
        if email:
            user.email = email

        if bio is not None:
            user.bio = bio

        if password:
            user.set_password(password)

        if profile_picture:
            user.profile_picture = profile_picture  # file-like object

        user.save()

        # 🔁 Return new token in case username or password changed
        payload = jwt_payload(user)
        new_token = jwt_encode(payload)

        return UpdateUserProfile(user=user, token=new_token)


class LogoutUser(graphene.Mutation):
    success = graphene.Boolean()

    def mutate(self, info):
        user = info.context.user
        if user.is_authenticated:

            # Invalidate the user's session or token here if needed
            return LogoutUser(success=True)
        raise GraphQLError("User is not authenticated.")


class LikeNews(graphene.Mutation):
    like = graphene.Field(LikeType)
    liked = graphene.Boolean()  # True if liked, False if unliked

    class Arguments:
        news_id = graphene.Int(required=True)

    def mutate(self, info, news_id):
        user = info.context.user

        if not user or not user.is_authenticated:
            raise GraphQLError("Authentication required to like/unlike a news article.")

        try:
            news = News.objects.get(id=news_id)
        except News.DoesNotExist:
            raise GraphQLError("The specified news article was not found.")

        like = Like.objects.filter(user=user, news=news).first()

        if like:
            # Already liked → unlike
            like.delete()
            return LikeNews(like=None, liked=False)
        else:
            # Not liked yet → like it
            new_like = Like.objects.create(user=user, news=news)
            return LikeNews(like=new_like, liked=True)



class LoggedInUser(graphene.ObjectType):
    user = graphene.Field(UserType)

    def resolve_user(self, info):
        user = info.context.user
        if user.is_authenticated:
            return user
        raise GraphQLError("User is not authenticated.")
    

    


class Query(graphene.ObjectType):

    categories = graphene.List(CategoryType)
    category = graphene.Field(CategoryType, id=graphene.Int(required=True))


    subcategories = graphene.List(SubCategoryType)
    subcategory = graphene.Field(SubCategoryType, id=graphene.Int(required=True))

    tags = graphene.List(TagType)
    tag = graphene.Field(TagType, id=graphene.Int(required=True))

    newses = graphene.List(NewsType)
    news = graphene.Field(NewsType, id=graphene.Int(required=True))

    comment = graphene.List(CommentType, news_id=graphene.Int(required=True))
    comments = graphene.List(CommentType)


    me = graphene.Field(UserType)


    def resolve_categories(self, info):
        return Category.objects.all()

    def resolve_category(self, info, id):
        try:
            return Category.objects.get(id=id)
        except Category.DoesNotExist:
            raise GraphQLError("Category not found.")
        

    def resolve_subcategories(self, info):
        return SubCategory.objects.all()
    
    def resolve_subcategory(self, info, id):
        try:
            return SubCategory.objects.get(id=id)
        except SubCategory.DoesNotExist:
            raise GraphQLError("SubCategory not found.")
        

    def resolve_tags(self, info):
        return Tag.objects.all()
    
    def resolve_tag(self, info, id):
        try:
            return Tag.objects.get(id=id)
        except Tag.DoesNotExist:
            raise GraphQLError("Tag not found.")
        

    def resolve_newses(self, info):
        return News.objects.all()
    
    def resolve_news(self, info, id):
        try:
            return News.objects.get(id=id)
        except News.DoesNotExist:
            raise GraphQLError("News not found.")
        

    def resolve_comment(self, info, news_id):
        try:
            news = News.objects.get(id=news_id)
            return news.comment.all()
        except News.DoesNotExist:
            raise GraphQLError("News not found.")
        
    def resolve_comments(self, info):
        return Comment.objects.all()
    

    def resolve_me(self, info):
        user = info.context.user
        if user.is_authenticated:
            return user
        raise GraphQLError("User is not authenticated.")
    
    

