from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Blog, Category, Tag, Comment, UserFollow, BlogAnalytics

class UserSerializer(serializers.ModelSerializer):
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'follower_count', 'following_count']
    
    def get_follower_count(self, obj):
        return obj.followers.count()
    
    def get_following_count(self, obj):
        return obj.following.count()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class CategorySerializer(serializers.ModelSerializer):
    blog_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'blog_count', 'created_at']
        read_only_fields = ['slug']
    
    def get_blog_count(self, obj):
        return obj.blogs.count()

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'blog', 'author', 'parent', 'content', 'created_at', 'updated_at', 'replies']
        read_only_fields = ['author', 'created_at', 'updated_at']
    
    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.filter(is_approved=True), many=True).data
        return []
    
    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

class BlogSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()
    view_count = serializers.SerializerMethodField()
    category_id = serializers.IntegerField(write_only=True, required=False)
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(), 
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Blog
        fields = [
            'id', 'title', 'slug', 'content', 'featured_image', 'image_caption',
            'author', 'created_at', 'updated_at', 'category', 'category_id',
            'tags', 'tag_ids', 'is_published', 'is_featured', 'excerpt',
            'comments_count', 'view_count'
        ]
        read_only_fields = ['author', 'created_at', 'updated_at', 'slug']

    def get_comments_count(self, obj):
        return obj.comments.filter(is_approved=True, parent=None).count()
    
    def get_view_count(self, obj):
        return obj.view_count
    
    def create(self, validated_data):
        tag_ids = validated_data.pop('tag_ids', [])
        validated_data['author'] = self.context['request'].user
        blog = super().create(validated_data)
        
        # Add tags if provided
        if tag_ids:
            blog.tags.set(Tag.objects.filter(id__in=tag_ids))
        
        return blog
    
    def update(self, instance, validated_data):
        tag_ids = validated_data.pop('tag_ids', None)
        blog = super().update(instance, validated_data)
        
        # Update tags if provided
        if tag_ids is not None:
            blog.tags.set(Tag.objects.filter(id__in=tag_ids))
            
        return blog

class BlogDetailSerializer(BlogSerializer):
    comments = serializers.SerializerMethodField()
    
    class Meta(BlogSerializer.Meta):
        fields = BlogSerializer.Meta.fields + ['comments']
    
    def get_comments(self, obj):
        # Only get top-level comments (no parent)
        return CommentSerializer(
            obj.comments.filter(is_approved=True, parent=None),
            many=True
        ).data

class UserFollowSerializer(serializers.ModelSerializer):
    follower = UserSerializer(read_only=True)
    followed = UserSerializer(read_only=True)
    followed_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = UserFollow
        fields = ['id', 'follower', 'followed', 'followed_id', 'created_at']
        read_only_fields = ['follower', 'created_at']
    
    def create(self, validated_data):
        validated_data['follower'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate(self, attrs):
        if self.context['request'].user.id == attrs.get('followed_id'):
            raise serializers.ValidationError({"followed": "You cannot follow yourself."})
        return attrs