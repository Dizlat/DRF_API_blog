from django.contrib import admin

from main.models import *


class PostImageInLine(admin.TabularInline):
    model = Image
    max_num = 5
    min_num = 1


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = [PostImageInLine, ]


admin.site.register(Category)
