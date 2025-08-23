from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
import os
import json
import re

# Import the Post model
from .models import Post

# 1. Display a list
@login_required
def post_list(request):
    # Fixed: Only show posts by the current user
    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'posts/post_list.html', {'posts': posts})

# 2. Display details functionality
@login_required
def post_detail(request, post_id):
    # Get the post, ensuring it belongs to the current user
    post = get_object_or_404(Post, id=post_id, author=request.user)
    return render(request, 'posts/post_detail.html', {'post': post})

# 3. Create new note functionality
@login_required
def post_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        
        if title and content:
            post = Post.objects.create(
                title=title,
                content=content,
                author=request.user
            )
            return redirect('post_list')
    
    return render(request, 'posts/post_form.html')

# 4. Edit a note functionality
@login_required
def post_edit(request, post_id):
    # FIXED: Authorization check to prevent IDOR
    post = get_object_or_404(Post, id=post_id, author=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        
        if title and content:
            post.title = title
            post.content = content
            post.save()
            return redirect('post_list')
    
    return render(request, 'posts/post_edit.html', {'post': post})

# 5. Delete a note functionality
@login_required
def post_delete(request, post_id):
    # Get the post, ensuring it belongs to the current user
    post = get_object_or_404(Post, id=post_id, author=request.user)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, f'Note "{post.title}" has been deleted successfully.')
        return redirect('post_list')
    
    return render(request, 'posts/post_delete.html', {'post': post})

# 6. Export functionality
@login_required
def export_notes(request):
    if request.method == 'POST':
        export_format = request.POST.get('export_format', 'txt')
        custom_template = request.POST.get('custom_template', '')
          # Get user's notes
        posts = Post.objects.filter(author=request.user)
        
        if export_format == 'txt':
            # Simple text export
            output = []
            for post in posts:
                output.append(f"Title: {post.title}")
                output.append(f"Content: {post.content}")
                output.append(f"Created: {post.created_at}")
                output.append("-" * 50)
            response_content = '\n'.join(output)
            
        elif export_format == 'json':
            # JSON export
            import json
            posts_data = []
            for post in posts:
                posts_data.append({
                    'title': post.title,
                    'content': post.content,
                    'created_at': post.created_at.isoformat()
                })
            response_content = json.dumps(posts_data, indent=2)
            
        elif export_format == 'custom':
            from string import Template
            if not custom_template:
                custom_template = "Title: $title\nContent: $content\nCreated: $created_at\n---\n"
            
            output = []
            for post in posts:
                try:
                    template = Template(custom_template)
                    formatted_line = template.safe_substitute(
                        title=post.title,
                        content=post.content,
                        id=post.id,
                        created_at=post.created_at.strftime('%Y-%m-%d')
                    )
                    output.append(formatted_line)
                    
                except Exception as e:
                    output.append(f"Template Error: {e}")
            
            response_content = '\n'.join(output)
        
        else:
            response_content = "Invalid export format"
        
        # Return as downloadable file
        response = HttpResponse(response_content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="notes_export.{export_format}"'
        return response
    
    return render(request, 'posts/export_notes.html')

# 7. Import functionality 
@login_required
def import_notes(request):
    if request.method == 'POST':
        if 'notes_file' in request.FILES:
            uploaded_file = request.FILES['notes_file']
            file_extension = uploaded_file.name.lower().split('.')[-1]
            
            try:
                if file_extension == 'txt':
                    # Import from plain text file
                    content = uploaded_file.read().decode('utf-8')
                    lines = content.split('\n')
                    
                    current_title = ""
                    current_content = ""
                    imported_count = 0
                    
                    for line in lines:
                        line = line.strip()
                        if line.startswith('Title: '):
                            if current_title and current_content:
                                Post.objects.create(
                                    title=current_title,
                                    content=current_content,
                                    author=request.user
                                )
                                imported_count += 1
                            current_title = line[7:]  # Remove "Title: "
                            current_content = ""
                        elif line.startswith('Content: '):
                            current_content = line[9:]  # Remove "Content: "
                        elif line and not line.startswith('Created:') and not line.startswith('-'):
                            if current_content:
                                current_content += "\n" + line
                            else:
                                current_content = line
                    
                    # Don't forget the last note
                    if current_title and current_content:
                        Post.objects.create(
                            title=current_title,
                            content=current_content,
                            author=request.user
                        )
                        imported_count += 1
                        
                elif file_extension == 'json':
                    # Import from JSON file
                    import json
                    content = uploaded_file.read().decode('utf-8')
                    data = json.loads(content)
                    imported_count = 0
                    
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and 'title' in item and 'content' in item:
                                Post.objects.create(
                                    title=item['title'][:200],  # Limit title length
                                    content=item['content'],
                                    author=request.user
                                )
                                imported_count += 1
                    
                elif file_extension == 'csv':
                    # Import from CSV file
                    import csv
                    import io
                    content = uploaded_file.read().decode('utf-8')
                    csv_file = io.StringIO(content)
                    reader = csv.DictReader(csv_file)
                    imported_count = 0
                    
                    for row in reader:
                        if 'title' in row and 'content' in row:
                            Post.objects.create(
                                title=row['title'][:200],  # Limit title length
                                content=row['content'],
                                author=request.user
                            )
                            imported_count += 1
                else:
                    messages.error(request, 'Unsupported file format. Please use TXT, JSON, or CSV files.')
                    return render(request, 'posts/import_notes.html')
                
                messages.success(request, f'Successfully imported {imported_count} notes from {uploaded_file.name}.')
                return redirect('post_list')
                
            except Exception as e:
                messages.error(request, f'Error processing file: {str(e)}')
                return render(request, 'posts/import_notes.html')
        else:
            messages.error(request, 'Please select a file to upload.')
    
    return render(request, 'posts/import_notes.html')

# 8. Search functionality
@login_required
def search_posts(request):
    posts = []
    query = request.GET.get('q', '').strip()
    error_message = None
    
    if query:
        try:
            with connection.cursor() as cursor:
                sql = "SELECT id, title, content, author_id FROM posts_post WHERE title LIKE %s AND author_id = %s"
                cursor.execute(sql, [f'%{query}%', request.user.id])
                results = cursor.fetchall()
                
                # Convert results to objects
                for row in results:
                    post_data = {
                        'id': row[0],
                        'title': row[1], 
                        'content': row[2],
                        'author_id': row[3]
                    }
                    posts.append(post_data)
        except Exception as e:
            error_message = f"Search error: {str(e)}"
            posts = []
    
    return render(request, 'posts/search_results.html', {
        'posts': posts, 
        'query': query,
        'error_message': error_message
    })
 
# 9. Backup functionality
@login_required
def backup_files(request):
    # FIXED: Add proper authorization check
    if not request.user.is_superuser:
        return HttpResponse("Unauthorized", status=401)
    
    # Only get current user's data (no longer a vulnerability)
    user_posts = Post.objects.filter(author=request.user)
    
    backup_info = {
        'message': 'StudyPad Personal Backup',
        'timestamp': timezone.now().isoformat(),
        'user': request.user.username,
        'total_notes': user_posts.count(),
        'notes': [
            {
                'id': post.id,
                'title': post.title,
                'preview': post.content[:100] + '...' if len(post.content) > 100 else post.content,
                'created_at': post.created_at.isoformat()
            } for post in user_posts
        ]
    }
    
    return JsonResponse(backup_info, json_dumps_params={'indent': 2})

# 10. File upload functionality
@login_required
def upload_file(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        category = request.POST.get('category', 'documents')
        subfolder = request.POST.get('subfolder', '').strip()
        
        if uploaded_file:
            base_dir = 'uploads' 
            
            import re
            if subfolder:
                subfolder = re.sub(r'[<>:"/\\|?*]', '', subfolder)  # Remove dangerous chars
                subfolder = re.sub(r'\.\.', '', subfolder)          # Remove ..
                subfolder = subfolder.replace('/', '').replace('\\', '')  # Remove slashes
                subfolder = subfolder[:50]  # Limit length
                
                # Only allow alphanumeric, dash, underscore
                subfolder = re.sub(r'[^a-zA-Z0-9\-_]', '', subfolder)
                
                # If nothing valid remains, use default
                if not subfolder:
                    subfolder = 'safe_uploads'
                
                upload_path = f'{base_dir}/{category}/{subfolder}'
            else:
                upload_path = f'{base_dir}/{category}'
            
            # Validate final path
            allowed_base = os.path.abspath('media/uploads')
            resolved_path = os.path.abspath(os.path.join('media', upload_path))
            if not resolved_path.startswith(allowed_base):
                messages.error(request, 'Invalid upload path detected.')
                return render(request, 'posts/upload_file.html')
            
            try:
                # Create full path (relative to media directory)
                full_path = os.path.join('media', upload_path)
                
                # Create directory if it doesn't exist
                os.makedirs(full_path, exist_ok=True)
                
                # Save file
                final_path = os.path.join(full_path, uploaded_file.name)
                with open(final_path, 'wb') as f:
                    for chunk in uploaded_file.chunks():
                        f.write(chunk)
                
                # Success
                context = {
                    'filename': uploaded_file.name,
                    'category': category,
                    'file_size': uploaded_file.size,
                    'file_path': os.path.abspath(final_path),
                    'subfolder': subfolder
                }
                return render(request, 'posts/upload_success.html', context)
                
            except Exception as e:
                messages.error(request, f'Upload failed: {str(e)}')
                return render(request, 'posts/upload_file.html')
        else:
            messages.error(request, 'Please select a file to upload.')
    
    return render(request, 'posts/upload_file.html')

@login_required
@require_POST
@csrf_protect
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('homepage')