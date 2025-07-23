
import graphene
from graphene_django import DjangoObjectType
from .models import *
from .models import CustomUser as User
from django.conf import settings



class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = "__all__"


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = "__all__"

    def resolve_profile_picture_url(self, info):
        if self.profile_picture:
            return f"{settings.MEDIA_URL}{self.profile_picture}"
        return None



class SubCategoryType(DjangoObjectType):
    class Meta:
        model = SubCategory
        fields = "__all__"


class TagType(DjangoObjectType):
    class Meta:
        model = Tag
        fields = "__all__"




class CommentType(DjangoObjectType):
    class Meta:
        model = Comment
        fields = "__all__"


class LikeType(DjangoObjectType):
    class Meta:
        model = Like
        fields = "__all__"


class NewsType(DjangoObjectType):
    class Meta:
        model = News
        fields = "__all__"