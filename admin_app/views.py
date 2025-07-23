from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny


# Create your views here.

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user is None:
            raise serializers.ValidationError("Invalid username or password")

        if not hasattr(user, 'role') or user.role != 'admin':
            raise serializers.ValidationError("You are not authorized to log in")

        data['user'] = user
        return data

class LoginUserView(APIView):
    # 👇 THIS is the fix
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Assuming you have a UserSerializer that handles user creation
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        # Use only() if serializer does not require all fields
        return get_object_or_404(CustomUser.objects.only('id', 'username', 'email'), pk=pk)

    def get(self, request, pk):
        user = self.get_object(pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk):
        user = self.get_object(pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    



class CategoryListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CategoryDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Category.objects.get(pk=pk)
        except Category.DoesNotExist:
            return None

    def get(self, request, pk):
        category = self.get_object(pk)
        if category is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    def put(self, request, pk):
        category = self.get_object(pk)
        if category is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        category = self.get_object(pk)
        if category is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


class SubCategoryListView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        subcategories = SubCategory.objects.all()
        serializer = SubCategorySerializer(subcategories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SubCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class SubCategoryDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return SubCategory.objects.get(pk=pk)
        except SubCategory.DoesNotExist:
            return None

    def get(self, request, pk):
        subcategory = self.get_object(pk)
        if subcategory is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = SubCategorySerializer(subcategory)
        return Response(serializer.data)

    def put(self, request, pk):
        subcategory = self.get_object(pk)
        if subcategory is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = SubCategorySerializer(subcategory, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        subcategory = self.get_object(pk)
        if subcategory is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        subcategory.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class TagListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TagSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class TagDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Tag.objects.get(pk=pk)
        except Tag.DoesNotExist:
            return None

    def get(self, request, pk):
        tag = self.get_object(pk)
        if tag is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = TagSerializer(tag)
        return Response(serializer.data)

    def put(self, request, pk):
        tag = self.get_object(pk)
        if tag is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = TagSerializer(tag, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        tag = self.get_object(pk)
        if tag is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        tag.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class NewsListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        news = News.objects.all()
        serializer = NewsSerializer(news, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = NewsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class NewsDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return News.objects.get(pk=pk)
        except News.DoesNotExist:
            return None

    def get(self, request, pk):
        news = self.get_object(pk)
        if news is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = NewsSerializer(news)
        return Response(serializer.data)

    def put(self, request, pk):
        news = self.get_object(pk)
        if news is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = NewsSerializer(news, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        news = self.get_object(pk)
        if news is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        news.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    



class CommentListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class CommentDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return None

    def get(self, request, pk):
        comment = self.get_object(pk)
        if comment is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    def put(self, request, pk):
        comment = self.get_object(pk)
        if comment is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        comment = self.get_object(pk)
        if comment is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


class LikeListView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        likes = Like.objects.all()
        serializer = LikeSerializer(likes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LikeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LikeDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Like.objects.get(pk=pk)
        except Like.DoesNotExist:
            return None

    def get(self, request, pk):
        like = self.get_object(pk)
        if like is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = LikeSerializer(like)
        return Response(serializer.data)

    def put(self, request, pk):
        like = self.get_object(pk)
        if like is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = LikeSerializer(like, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        like = self.get_object(pk)
        if like is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        like.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class CreateNewsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = NewsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        news = News.objects.all()
        serializer = NewsSerializer(news, many=True)
        return Response(serializer.data)
    
class UpdateNewsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        news = News.objects.get(pk=pk)
        serializer = NewsSerializer(news, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        news = News.objects.get(pk=pk)
        news.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

