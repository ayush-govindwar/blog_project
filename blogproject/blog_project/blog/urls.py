from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # Authentication endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('users/me/', views.UserProfileView.as_view(), name='user-profile'),
    
    # Blog endpoints
    path('blogs/', views.BlogListCreateView.as_view(), name='blog-list-create'),
    path('blogs/<int:pk>/', views.BlogDetailView.as_view(), name='blog-detail'),
    path('users/<int:user_id>/blogs/', views.UserBlogsView.as_view(), name='user-blogs'),
]