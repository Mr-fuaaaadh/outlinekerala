from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from .models import *
from django.contrib import admin

admin.site.site_header = "Outline Kerala Admin Dashboard"
admin.site.site_title = "Outline Kerala Admin Portal"
admin.site.index_title = "Welcome to Outline Kerala Admin"


admin.site.register(Comment)
admin.site.register(Like)


class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 5 
    min_num = 1
    verbose_name_plural = "Subcategories"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [SubCategoryInline]

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'category']
    prepopulated_fields = {'slug': ('name',)}



@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'is_active')  # Add the fields you want to show
    search_fields = ('username', 'email')  # Optional: Add search box
    list_filter = ('is_active', 'is_staff')  # Optional: Add filters


@admin.register(Tag)
class TagAdmin(ImportExportModelAdmin):
    list_display = ['name', 'slug']


@admin.register(News)
class NewsAdmin(ImportExportModelAdmin):
    list_display = ['title', 'category', 'created_at']
    search_fields = ['title', 'content']
    list_filter = ['category', 'created_at']
    readonly_fields = ['created_at']
    