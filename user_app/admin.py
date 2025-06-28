from django.contrib import admin
from .models import *


admin.site.register(CustomUser)
# admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(News)
admin.site.register(Comment)
admin.site.register(Like)
# admin.site.register(SubCategory)


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
