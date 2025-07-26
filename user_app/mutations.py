import graphene
from django.contrib.auth import get_user_model
from django.core.cache import cache
from graphene_django.filter import DjangoFilterConnectionField
from graphql import GraphQLError
from .type import UserType, CategoryType, TagType , NewsType, CommentType, LikeType, SubCategoryType
from .models import Category, Tag ,News, Comment, Like, SubCategory
from graphene_file_upload.scalars import Upload
from graphql_jwt.decorators import login_required
from .service import *
from user_app.db_utils import get_object_or_error
import logging
logger = logging.getLogger(__name__)

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
        profile_picture = Upload(required=False)

    @login_required
    def mutate(self, info, username=None, email=None, bio=None, password=None, profile_picture=None):
        user = info.context.user

        logger.info("🛠️ UpdateUserProfile mutation triggered")
        logger.info(f"Incoming data: username={username}, email={email}, bio={bio}, password={'****' if password else None}, profile_picture={profile_picture}")

        try:
            updated_user, token, message = UserService.update_user_profile(
                user=user,
                username=username,
                email=email,
                bio=bio,
                password=password,
                profile_picture=profile_picture
            )
            logger.info(f"✅ Update successful: user={updated_user.username}, token={token}, message={message}")
            return UpdateUserProfile(user=updated_user, token=token, message=message)

        except Exception as e:
            logger.error(f"❌ Error in UpdateUserProfile mutation: {e}")
            raise GraphQLError(f"Failed to update profile: {str(e)}")



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
        profile_picture = Upload()

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

    categories = graphene.List(lambda: CategoryType)
    category = graphene.Field(CategoryType, id=graphene.Int(required=True))

    subcategories = graphene.List(lambda: SubCategoryType)
    subcategory = graphene.Field(SubCategoryType, id=graphene.Int(required=True))

    tags = graphene.List(TagType)
    tag = graphene.Field(TagType, id=graphene.Int(required=True))

    newses = DjangoFilterConnectionField(NewsType)
    news = graphene.Field(NewsType, id=graphene.Int(required=True))

    comments = graphene.List(lambda: CommentType, news_id=graphene.ID(required=True))
    comment = graphene.List(CommentType, news_id=graphene.Int(required=True))

    me = graphene.Field(UserType)

    users = graphene.List(UserType)
    all_main_categories = graphene.List(CategoryType)
    all_subcategories = graphene.List(SubCategoryType)


    # ---------------- Resolvers ----------------

    # Categories resolver with caching
    def resolve_categories(self, info):
        categories = cache.get("categories")
        if categories is None:
            categories = list(Category.objects.only("id", "name", "slug"))
            cache.set("categories", categories, 60 * 60)  
        return categories

    def resolve_category(self, info, id):
        return get_object_or_error(Category, id=id)

    # SubCategories resolver with caching and select_related for category
    def resolve_subcategories(self, info):
        subcategories = cache.get("subcategories")
        if subcategories is None:
            subcategories = list(SubCategory.objects.select_related('category').only("id", "name", "slug", "category_id"))
            cache.set("subcategories", subcategories, 60 * 60)
        return subcategories

    def resolve_subcategory(self, info, id):
        return get_object_or_error(SubCategory, id=id)

    # Tags resolver with caching
    def resolve_tags(self, info):
        tags = cache.get("tags")
        if tags is None:
            tags = list(Tag.objects.only("id", "name", "slug"))
            cache.set("tags", tags, 60 * 60)
        return tags

    def resolve_tag(self, info, id):
        return get_object_or_error(Tag, id=id)

    def resolve_newses(self, info):
        return News.objects.all()

    def resolve_news(self, info, id):
        return get_object_or_error(News, id=id)

    def resolve_comments(self, info, news_id):
        return Comment.objects.filter(news_id=news_id, approved=True).select_related('user').order_by('-created_at')

    def resolve_comment(self, info, news_id):
        news = get_object_or_error(News, id=news_id)
        return news.comment.all()

    


    
    

