from django.contrib import admin

from posts.models import Comment, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["author", "content", "created_at"]
    search_fields = ["content", "author__username"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["author", "post", "content", "created_at"]
