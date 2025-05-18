from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # Authentication endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('users/me/', views.UserProfileView.as_view(), name='user-profile'),
    path('users/<int:user_id>/', views.UserDetailView.as_view(), name='user-detail'),
    
    # User follow system
    path('users/<int:user_id>/toggle-follow/', views.toggle_follow_user, name='toggle-follow-user'),
    path('users/<int:user_id>/followers/', views.UserFollowersView.as_view(), name='user-followers'),
    path('users/<int:user_id>/following/', views.UserFollowingView.as_view(), name='user-following'),
    path('follows/', views.UserFollowListCreateView.as_view(), name='follow-list-create'),
    path('follows/<int:pk>/', views.UserFollowDetailView.as_view(), name='follow-detail'),
    
    # Blog endpoints
    path('blogs/', views.BlogListCreateView.as_view(), name='blog-list-create'),
    path('blogs/<slug:slug>/', views.BlogDetailView.as_view(), name='blog-detail'),
    path('users/<int:user_id>/blogs/', views.UserBlogsView.as_view(), name='user-blogs'),
    
    # Category endpoints
    path('categories/', views.CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category-detail'),
    
    # Tag endpoints
    path('tags/', views.TagListCreateView.as_view(), name='tag-list-create'),
    path('tags/<slug:slug>/', views.TagDetailView.as_view(), name='tag-detail'),
    
    # Comment endpoints
    path('blogs/<int:blog_id>/comments/', views.CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', views.CommentDetailView.as_view(), name='comment-detail'),
    
    # Search endpoint
    path('search/', views.SearchView.as_view(), name='search'),
]