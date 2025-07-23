from django.urls import path
from . import views

urlpatterns = [
    # posts/
    path('', views.post_list, name='post_list'),
    
    # posts/create/
    path('create/', views.post_create, name='post_create'),
    
    # posts/search/
    path('search/', views.search_posts, name='search_posts'),
    
    # posts/import/
    path('import/', views.import_notes, name='import_notes'),
    
    # posts/export/
    path('export/', views.export_notes, name='export_notes'),
    
    # posts/123/
    path('<int:post_id>/', views.post_detail, name='post_detail'),
    
    # posts/123/edit/
    path('<int:post_id>/edit/', views.post_edit, name='post_edit'),
    
    # posts/123/delete/
    path('<int:post_id>/delete/', views.post_delete, name='post_delete'),
    
    path('backup/', views.backup_files, name='backup_notes'), 
    
    path('upload/', views.upload_file, name='upload_file'),  # New upload file path
]