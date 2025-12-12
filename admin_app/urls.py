from django.urls import path
from .views import *

urlpatterns = [
    # path('register/', RegisterUserView.as_view(), name='register_user'),
    path('login/', LoginUserView.as_view(), name='login_user'),
    path('news/create/', CreateNewsView.as_view(), name='create_news'),
    path('news/<int:pk>/', NewsDetailView.as_view(), name='news_detail'),
    path('news/<int:pk>/update/', UpdateNewsView.as_view(), name='update_news'),
    path('news/<int:pk>/delete/', UpdateNewsView.as_view(), name='delete_news'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category_detail'),
    path('tags/', TagListView.as_view(), name='tag_list'),
    path('tags/<int:pk>/', TagDetailView.as_view(), name='tag_detail'),
    path('subcategories/', SubCategoryListView.as_view(), name='subcategory_list'),
    path('subcategories/<int:pk>/', SubCategoryDetailView.as_view(), name='subcategory_detail'),
    path('comments/', CommentListView.as_view(), name='comment_list'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment_detail'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),


    # ----- WARD -----
    path("wards/", WardListCreateView.as_view(), name="ward_list_create"),
    path("wards/<int:pk>/", WardDetailEditDeleteView.as_view(), name="ward_detail"),

    # ----- CANDIDATES / ELECTION RESULTS -----
    path("candidates/", ElectionResultListCreateView.as_view(), name="candidate_list_create"),
    path("candidates/<int:pk>/", ElectionResultDetailEditDeleteView.as_view(), name="candidate_detail"),

]