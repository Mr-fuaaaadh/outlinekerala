import graphene
from django.contrib.auth import get_user_model
from graphql import GraphQLError
from .type import UserType, CategoryType, TagType , NewsType, CommentType, LikeType, SubCategoryType
from .models import Category, Tag ,News, Comment, Like, SubCategory
from graphene_file_upload.scalars import Upload
from graphql_jwt.decorators import login_required
from .service import *
from user_app.db_utils import get_object_or_error

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
        user, token = register_user(
            username=username,
            email=email,
            password=password,
            role=role,
            bio=bio or ""
        )
        return RegisterUser(user=user, token=token)


class LoginUser(graphene.Mutation):
    user = graphene.Field(UserType)
    token = graphene.String()

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, username, password):
        user, token = login_user(username, password)
        return LoginUser(user=user, token=token)
    



    
class CommentNews(graphene.Mutation):
    comment = graphene.Field(CommentType)

    class Arguments:
        news_id = graphene.Int(required=True)
        content = graphene.String(required=True)
        parent_id = graphene.Int()

    def mutate(self, info, news_id, content, parent_id=None):
        user = info.context.user

        # Validation and comment creation via service
        CommentService.validate_user(user)
        news = CommentService.get_news(news_id)
        parent = CommentService.get_parent_comment(parent_id, news_id) if parent_id else None
        comment = CommentService.create_comment(news, user, content, parent)

        return CommentNews(comment=comment)



class UpdateUserProfile(graphene.Mutation):
    user = graphene.Field(UserType)
    token = graphene.String()
    message = graphene.String()

    class Arguments:
        username = graphene.String()
        email = graphene.String()
        bio = graphene.String()
        password = graphene.String()
        profile_picture = Upload()

    @login_required
    def mutate(self, info, username=None, email=None, bio=None, password=None, profile_picture=None):
        user = info.context.user
        updated_user, token, message = UserService.update_user_profile(
            user=user,
            username=username,
            email=email,
            bio=bio,
            password=password,
            profile_picture=profile_picture
        )
        return UpdateUserProfile(user=updated_user, token=token, message=message)

    




class LogoutUser(graphene.Mutation):
    success = graphene.Boolean()

    @login_required
    def mutate(self, info):
        user = info.context.user
        AuthService.logout_user(user)
        return LogoutUser(success=True)


class LikeNews(graphene.Mutation):
    like = graphene.Field(LikeType)
    liked = graphene.Boolean()

    class Arguments:
        news_id = graphene.Int(required=True)

    @login_required
    def mutate(self, info, news_id):
        user = info.context.user
        like, liked = LikeService.toggle_like(user, news_id)
        return LikeNews(like=like, liked=liked)
    

class AdminUpdateUserProfile(graphene.Mutation):
    user = graphene.Field(UserType)
    message = graphene.String()

    class Arguments:
        user_id = graphene.Int(required=True)
        username = graphene.String()
        email = graphene.String()
        role = graphene.String()
        bio = graphene.String()
        profile_picture = Upload()  # Optional file

    @login_required
    def mutate(self, info, user_id, username=None, email=None, role=None, bio=None, profile_picture=None):
        user = info.context.user
        if user.role != 'admin':
            raise GraphQLError("You do not have permission to update user profiles.")

        updated_user, message = UserService.admin_update_user_profile(
            user=user,
            user_id=user_id,
            username=username,
            email=email,
            role=role,
            bio=bio,
            profile_picture=profile_picture
        )
        return AdminUpdateUserProfile(user=updated_user, message=message)




class LoggedInUser(graphene.ObjectType):
    user = graphene.Field(UserType)

    def resolve_user(self, info):
        user = info.context.user
        if user.is_authenticated:
            return user
        raise GraphQLError("User is not authenticated.")
    
    

    


class Query(graphene.ObjectType):
    # Existing fields
    categories = graphene.List(CategoryType)
    category = graphene.Field(CategoryType, id=graphene.Int(required=True))

    subcategories = graphene.List(SubCategoryType)
    subcategory = graphene.Field(SubCategoryType, id=graphene.Int(required=True))

    tags = graphene.List(TagType)
    tag = graphene.Field(TagType, id=graphene.Int(required=True))

    newses = graphene.List(NewsType)
    news = graphene.Field(NewsType, id=graphene.Int(required=True))

    comments = graphene.List(CommentType)
    comment = graphene.List(CommentType, news_id=graphene.Int(required=True))

    me = graphene.Field(UserType)

    users = graphene.List(UserType)
    all_main_categories = graphene.List(CategoryType)
    all_subcategories = graphene.List(SubCategoryType)


    # ---------------- Resolvers ----------------

    def resolve_categories(self, info):
        return Category.objects.all()

    def resolve_category(self, info, id):
        return get_object_or_error(Category, id=id)

    def resolve_subcategories(self, info):
        return SubCategory.objects.all()

    def resolve_subcategory(self, info, id):
        return get_object_or_error(SubCategory, id=id)

    def resolve_tags(self, info):
        return Tag.objects.all()

    def resolve_tag(self, info, id):
        return get_object_or_error(Tag, id=id)

    def resolve_newses(self, info):
        return News.objects.all()

    def resolve_news(self, info, id):
        return get_object_or_error(News, id=id)

    def resolve_comments(self, info):
        return Comment.objects.all()

    def resolve_comment(self, info, news_id):
        news = get_object_or_error(News, id=news_id)
        return news.comment.all()

    def resolve_me(self, info):
        user = info.context.user
        if user and user.is_authenticated:
            return user
        raise GraphQLError("User is not authenticated.")

    def resolve_users(self, info):
        user = info.context.user
        if user.is_authenticated and user.role == 'admin':
            return User.objects.all()
        raise GraphQLError("You are not authenticated or do not have permission to view all users.")
    

    def resolve_all_main_categories(self, info):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required.")
        if getattr(user, "role", None) != "admin":
            raise GraphQLError("You do not have permission.")
        return Category.objects.all()
    

    def resolve_all_subcategories(self, info):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required.")
        if getattr(user, "role", None) != "admin":
            raise GraphQLError("You do not have permission.")
        return SubCategory.objects.all()

    
    

