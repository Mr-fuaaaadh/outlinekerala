from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from .models import *

admin.site.site_header = "Outline Kerala Admin Dashboard"
admin.site.site_title = "Outline Kerala Admin Portal"
admin.site.index_title = "Welcome to Outline Kerala Admin"


@admin.register(Comment)
class CommentAdmin(ImportExportModelAdmin):
    list_display = ['user', 'news', 'approved', 'created_at']
    list_filter = ['approved', 'created_at']
    search_fields = ['content', 'user__username', 'news__title']


@admin.register(Like)
class LikeAdmin(ImportExportModelAdmin):
    list_display = ['user', 'news']
    search_fields = ['user__username', 'news__title']


class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 5 
    min_num = 1
    verbose_name_plural = "Subcategories"

@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [SubCategoryInline]

@admin.register(SubCategory)
class SubCategoryAdmin(ImportExportModelAdmin):
    list_display = ['name', 'slug', 'category']
    prepopulated_fields = {'slug': ('name',)}



@admin.register(CustomUser)
class CustomUserAdmin(ImportExportModelAdmin):
    list_display = ('id', 'username', 'email', 'is_active', 'role')
    search_fields = ('username', 'email')
    list_filter = ('is_active', 'is_staff', 'role')


@admin.register(Tag)
class TagAdmin(ImportExportModelAdmin):
    list_display = ['name', 'slug']


@admin.register(News)
class NewsAdmin(ImportExportModelAdmin):
    list_display = ['title', 'category', 'created_at', 'status']
    search_fields = ['title', 'content']
    list_filter = ['category', 'created_at', 'status']
    readonly_fields = ['created_at']