from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from .models import *


admin.site.register(Comment)
admin.site.register(Like)


class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 5  # Number of empty subcategory rows shown
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



<<<<<<< HEAD
=======
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'is_active')  # Add the fields you want to show
    search_fields = ('username', 'email')  # Optional: Add search box
    list_filter = ('is_active', 'is_staff')  # Optional: Add filters

>>>>>>> eca0cc0d752d91affd5d9eee45764fc3fb5eecc3

@admin.register(Tag)
class TagAdmin(ImportExportModelAdmin):
    list_display = ['name', 'slug']


@admin.register(News)
class NewsAdmin(ImportExportModelAdmin):
    list_display = ['title', 'category', 'created_at']
    search_fields = ['title', 'content']
    list_filter = ['category', 'created_at']
