from django.contrib import admin
from .models import *


admin.site.register(CustomUser)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(News)
admin.site.register(Comment)