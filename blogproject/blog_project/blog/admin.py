from django.contrib import admin
from .models import Blog, Category, Tag, Comment, UserFollow, BlogAnalytics

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'is_published', 'is_featured', 'created_at', 'updated_at', 'view_count')
    list_filter = ('is_published', 'is_featured', 'created_at', 'updated_at', 'category')
    search_fields = ('title', 'content', 'author__username', 'category__name')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('tags',)
    
    def view_count(self, obj):
        return obj.view_count
    view_count.short_description = 'Views'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'blog', 'parent', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('content', 'author__username', 'blog__title')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(UserFollow)
class UserFollowAdmin(admin.ModelAdmin):
    list_display = ('follower', 'followed', 'created_at')
    search_fields = ('follower__username', 'followed__username')
    readonly_fields = ('created_at',)

@admin.register(BlogAnalytics)
class BlogAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'view_count', 'last_viewed')
    readonly_fields = ('content_object', 'view_count', 'last_viewed')