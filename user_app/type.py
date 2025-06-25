
import graphene
from graphene_django import DjangoObjectType
from .models import *
from .models import CustomUser as User


class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = "__all__"


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = "__all__"



class SubCategoryType(DjangoObjectType):
    class Meta:
        model = SubCategory
        fields = "__all__"
        

class TagType(DjangoObjectType):
    class Meta:
        model = Tag
        fields = "__all__"


class NewsType(DjangoObjectType):
    category = graphene.Field(CategoryType)
    comments = graphene.List(lambda: CommentType)

    class Meta:
        model = News
        fields = "__all__"

    def resolve_comments(self, info):
        return self.comments.all()


class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = "__all__"


class LikeType(DjangoObjectType):
    class Meta:
        model = Like
        fields = "__all__"