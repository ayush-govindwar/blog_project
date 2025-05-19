
from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404

from .models import Blog, Category, Tag, Comment, UserFollow
from .serializers import (
    BlogSerializer, BlogDetailSerializer, UserSerializer, 
    UserRegistrationSerializer, CategorySerializer, TagSerializer,
    CommentSerializer, UserFollowSerializer
)
from .permissions import IsAuthorOrReadOnly

class UserRegistrationView(generics.CreateAPIView): #createapiview-> post request
    queryset = User.objects.all() #generic views
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny] #allow anyone

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True) #validate
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data, #convert to json
            "message": "User registered successfully",
        }, status=status.HTTP_201_CREATED)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated] #jwt under the hood
    lookup_url_kwarg = 'user_id'

class BlogListCreateView(generics.ListCreateAPIView):
    serializer_class = BlogSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] #anyone can read
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content', 'tags__name', 'category__name']
    ordering_fields = ['created_at', 'updated_at', 'view_count']
    
    def get_queryset(self):
        queryset = Blog.objects.all()
        
        # Filter by published status (unpublished blogs only visible to their authors)
        if self.request.user.is_authenticated:
            queryset = queryset.filter(
                Q(is_published=True) | Q(author=self.request.user)
            )
        else:
            queryset = queryset.filter(is_published=True)
            
        # Filter by category
        category_slug = self.request.query_params.get('category', None)
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
            
        # Filter by tag
        tag_slug = self.request.query_params.get('tag', None)
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
            
        # Filter by featured status
        featured = self.request.query_params.get('featured', None)
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
            
        # Filter by author
        author_id = self.request.query_params.get('author', None)
        if author_id:
            queryset = queryset.filter(author__id=author_id)
            
        return queryset.distinct()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user) #deserilise

class BlogDetailView(generics.RetrieveUpdateDestroyAPIView): #generic view
    queryset = Blog.objects.all()
    serializer_class = BlogDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    lookup_field = 'slug'
    
    def get(self, request, *args, **kwargs): #when get also increment views
        instance = self.get_object()
        # Increment the view count
        instance.increment_view()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class UserBlogsView(generics.ListAPIView):
    serializer_class = BlogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user_id = self.kwargs.get('user_id') #get user id from params
        user = get_object_or_404(User, id=user_id)
        
        # Only show published blogs unless the requester is the author
        if self.request.user.id == user_id:
            return Blog.objects.filter(author__id=user_id)
        return Blog.objects.filter(author__id=user_id, is_published=True)

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

class TagListCreateView(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class TagDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        blog_id = self.kwargs.get('blog_id')
        return Comment.objects.filter(blog__id=blog_id, parent=None, is_approved=True)

class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

class UserFollowListCreateView(generics.ListCreateAPIView):
    serializer_class = UserFollowSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserFollow.objects.filter(follower=self.request.user) #filter those users where user is follower

class UserFollowDetailView(generics.RetrieveDestroyAPIView): #retrive and destroy follo relationship
    serializer_class = UserFollowSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserFollow.objects.filter(follower=self.request.user)

class UserFollowersView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        user_follows = UserFollow.objects.filter(followed__id=user_id).select_related('follower')
        return [user_follow.follower for user_follow in user_follows]

class UserFollowingView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        user_follows = UserFollow.objects.filter(follower__id=user_id).select_related('followed')
        return [user_follow.followed for user_follow in user_follows]

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def toggle_follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    user = request.user
    
    if user.id == user_to_follow.id:
        return Response(
            {"error": "You cannot follow yourself"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    follow_exists = UserFollow.objects.filter(
        follower=user, 
        followed=user_to_follow
    ).exists() # check if user is already following the user
    # If the follow relationship exists, delete it (unfollow)
    
    if follow_exists:
        UserFollow.objects.filter(follower=user, followed=user_to_follow).delete()
        return Response(
            {"status": "unfollowed", "message": f"You have unfollowed {user_to_follow.username}"},
            status=status.HTTP_200_OK
        )
    else:
        UserFollow.objects.create(follower=user, followed=user_to_follow)
        return Response(
            {"status": "followed", "message": f"You are now following {user_to_follow.username}"},
            status=status.HTTP_201_CREATED
        )

class SearchView(generics.ListAPIView):
    serializer_class = BlogSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content', 'tags__name', 'category__name', 'author__username']
    
    def get_queryset(self):
        query = self.request.query_params.get('q', '').strip()

        if not query:
            return Blog.objects.none()

        base_filter = Q(title__icontains=query) | Q(content__icontains=query) | Q(tags__name__icontains=query) | Q(category__name__icontains=query) | Q(author__username__icontains=query)

        if self.request.user.is_authenticated:
            return Blog.objects.filter(
                base_filter & (Q(is_published=True) | Q(author=self.request.user))
            ).distinct()
        
        return Blog.objects.filter(
            base_filter & Q(is_published=True)
        ).distinct()
