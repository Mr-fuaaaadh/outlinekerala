import graphene
from django.contrib.auth import get_user_model
from graphql_jwt.shortcuts import get_token
from graphql import GraphQLError
from .type import UserType, CategoryType, TagType , NewsType, CommentType, LikeType
from .models import Category, Tag ,News, Comment, Like
from django.contrib.auth import authenticate

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

        token = get_token(user)
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



class LikeNews(graphene.Mutation):
    like = graphene.Field(LikeType)

    class Arguments:
        news_id = graphene.Int(required=True)

    def mutate(self, info, news_id):
        user = info.context.user

        if not user or not user.is_authenticated:
            raise GraphQLError("Authentication required to like a news article.")

        try:
            news = News.objects.get(id=news_id)
        except News.DoesNotExist:
            raise GraphQLError("The specified news article was not found.")

        like, created = Like.objects.get_or_create(user=user, news=news)

        if not created:
            raise GraphQLError("You have already liked this news article.")

        return LikeNews(like=like)

    


class Query(graphene.ObjectType):

    categories = graphene.List(CategoryType)
    category = graphene.Field(CategoryType, id=graphene.Int(required=True))

    tags = graphene.List(TagType)
    tag = graphene.Field(TagType, id=graphene.Int(required=True))

    newses = graphene.List(NewsType)
    news = graphene.Field(NewsType, id=graphene.Int(required=True))

    comment = graphene.List(CommentType, news_id=graphene.Int(required=True))
    comments = graphene.List(CommentType)


    def resolve_categories(self, info):
        return Category.objects.all()

    def resolve_category(self, info, id):
        try:
            return Category.objects.get(id=id)
        except Category.DoesNotExist:
            raise GraphQLError("Category not found.")
        

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
    
    

