from django.urls import path
from .views import PostListCreateAPIView, PostDetailAPIView

app_name = 'api'

urlpatterns = [
    path('v1/posts/', PostListCreateAPIView.as_view(), name='post_list_create'),
    path('v1/posts/<int:pk>/', PostDetailAPIView.as_view(), name='post_detail'),
]