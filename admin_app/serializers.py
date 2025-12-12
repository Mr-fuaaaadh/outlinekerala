from rest_framework import serializers
from user_app.models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = "__all__"


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = Comment
        fields = "__all__"

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = "__all__"



from rest_framework import serializers
from .models import Ward, ElectionResult

class WardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ward
        fields = "__all__"


class ElectionResultSerializer(serializers.ModelSerializer):
    party_logo_url = serializers.SerializerMethodField()
    candidate_photo_url = serializers.SerializerMethodField()

    class Meta:
        model = ElectionResult
        fields = [
            "id",
            "ward",
            "name",
            "age",
            "address",
            "party",
            "party_logo",
            "candidate_photo",
            "vote_count",
            "party_logo_url",
            "candidate_photo_url",
        ]

    def get_party_logo_url(self, obj):
        if obj.party_logo:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.party_logo.url)
        return None

    def get_candidate_photo_url(self, obj):
        if obj.candidate_photo:
            request = self.context.get("request")
            return request.build_absolute_uri(obj.candidate_photo.url)
        return None

