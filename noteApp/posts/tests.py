from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Post
import time

class PostSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_post_list_requires_login(self):
        """Test that post list requires authentication"""
        response = self.client.get('/posts/')
        self.assertEqual(response.status_code, 302)  # Should redirect to login
        self.assertIn('/accounts/login/', response.url)

    def test_user_can_only_see_own_posts(self):
        """Test user isolation in web interface"""
        user2 = User.objects.create_user(
            username='testuser2',
            password='testpass123'
        )
        
        # Create posts for both users
        Post.objects.create(
            title='User 1 Post',
            content='This belongs to user 1',
            author=self.user
        )
        
        Post.objects.create(
            title='User 2 Post', 
            content='This belongs to user 2',
            author=user2
        )
        
        # Login as user 1
        self.client.login(username='testuser', password='testpass123')
        
        # Get post list
        response = self.client.get('/posts/')
        self.assertEqual(response.status_code, 200)
        
        # Should see own post but not other user's post
        self.assertContains(response, 'User 1 Post')
        self.assertNotContains(response, 'User 2 Post')

    def test_post_string_representation(self):
        """Test that Post model returns correct string representation"""
        post = Post.objects.create(
            title='My Study Notes',
            content='These are my chemistry notes',
            author=self.user
        )
        
        # The __str__ method should return the title
        self.assertEqual(str(post), 'My Study Notes')

    def test_post_detail_requires_login(self):
        """Test that post detail requires authentication"""
        post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user
        )
        
        response = self.client.get(f'/posts/{post.id}/')
        self.assertEqual(response.status_code, 302)  # Should redirect to login

    def test_post_detail_authorization(self):
        """Test users can only view their own posts"""
        user2 = User.objects.create_user(username='user2', password='pass123')
        
        # Create post by user2
        post = Post.objects.create(
            title='User 2 Post',
            content='Private content',
            author=user2
        )
        
        # Login as user1
        self.client.login(username='testuser', password='testpass123')
        
        # Try to access user2's post
        response = self.client.get(f'/posts/{post.id}/')
        self.assertEqual(response.status_code, 404)  # Should not find it

    def test_post_create_requires_login(self):
        """Test that creating posts requires authentication"""
        response = self.client.get('/posts/create/')
        self.assertEqual(response.status_code, 302)
        
        response = self.client.post('/posts/create/', {
            'title': 'Test Post',
            'content': 'Test content'
        })
        self.assertEqual(response.status_code, 302)

    def test_post_create_functionality(self):
        """Test creating posts through web interface"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post('/posts/create/', {
            'title': 'New Web Post',
            'content': 'Created through web form'
        })
        
        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        
        # Verify post was created
        self.assertTrue(Post.objects.filter(title='New Web Post').exists())
        created_post = Post.objects.get(title='New Web Post')
        self.assertEqual(created_post.author, self.user)

    def test_post_edit_authorization(self):
        """Test users can only edit their own posts"""
        user2 = User.objects.create_user(username='user2', password='pass123')
        
        # Create post by user2
        post = Post.objects.create(
            title='User 2 Post',
            content='Original content',
            author=user2
        )
        
        # Login as user1
        self.client.login(username='testuser', password='testpass123')
        
        # Try to edit user2's post
        response = self.client.get(f'/posts/{post.id}/edit/')
        self.assertEqual(response.status_code, 404)
        
        # Try to update via POST
        response = self.client.post(f'/posts/{post.id}/edit/', {
            'title': 'Hacked Title',
            'content': 'Hacked content'
        })
        self.assertEqual(response.status_code, 404)
        
        # Verify post wasn't changed
        post.refresh_from_db()
        self.assertEqual(post.title, 'User 2 Post')

    def test_post_delete_authorization(self):
        """Test users can only delete their own posts"""
        user2 = User.objects.create_user(username='user2', password='pass123')
        
        # Create post by user2
        post = Post.objects.create(
            title='User 2 Post',
            content='Should not be deleted',
            author=user2
        )
        
        # Login as user1
        self.client.login(username='testuser', password='testpass123')
        
        # Try to delete user2's post
        response = self.client.get(f'/posts/{post.id}/delete/')
        self.assertEqual(response.status_code, 404)
        
        response = self.client.post(f'/posts/{post.id}/delete/')
        self.assertEqual(response.status_code, 404)
        
        # Verify post still exists
        self.assertTrue(Post.objects.filter(id=post.id).exists())

    def test_search_functionality(self):
        """Test search only returns user's own posts"""
        user2 = User.objects.create_user(username='user2', password='pass123')
        
        # Create posts with same keyword
        Post.objects.create(
            title='Chemistry Notes User 1',
            content='My chemistry study notes',
            author=self.user
        )
        
        Post.objects.create(
            title='Chemistry Notes User 2',
            content='Other user chemistry notes',
            author=user2
        )
        
        # Login and search
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/posts/search/', {'q': 'chemistry'})
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Chemistry Notes User 1')
        self.assertNotContains(response, 'Chemistry Notes User 2')


class PostModelTests(TestCase):
    """Test Post model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

    def test_post_creation(self):
        """Test basic post creation"""
        post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user
        )
        
        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.content, 'Test content')
        self.assertEqual(post.author, self.user)
        self.assertTrue(post.created_at)
        self.assertTrue(post.updated_at)

    def test_post_ordering(self):
        """Test posts are ordered by creation date"""
        post1 = Post.objects.create(
            title='First Post',
            content='Content 1',
            author=self.user
        )
        time.sleep(0.01)
        post2 = Post.objects.create(
            title='Second Post',
            content='Content 2',
            author=self.user
        )
        
        posts = list(Post.objects.filter(author=self.user).order_by('-created_at'))
    
        # Test that we have 2 posts and they're ordered correctly
        self.assertEqual(len(posts), 2)
        # The second post should have a created_at >= first post
        self.assertGreaterEqual(posts[0].created_at, posts[1].created_at)
        # Or just check that second post is first in the list
        self.assertEqual(posts[0].title, 'Second Post')

    def test_post_title_length_limits(self):
        """Test business rule: Post titles have reasonable length limits"""
        # Test minimum length
        with self.assertRaises(Exception):
            Post.objects.create(
                title='A',  # Too short for study notes
                content='Valid content here',
                author=self.user
            )
        
        # Test maximum length (business rule: titles should be concise)
        very_long_title = 'A' * 300  # 300 characters
        with self.assertRaises(Exception):
            Post.objects.create(
                title=very_long_title,
                content='Valid content',
                author=self.user
            )

    def test_post_content_not_empty(self):
        """Test business rule: Posts must have meaningful content"""
        # Empty content should fail
        with self.assertRaises(Exception):
            Post.objects.create(
                title='Valid Title',
                content='',  # Empty content
                author=self.user
            )
        
        # Only whitespace should fail
        with self.assertRaises(Exception):
            Post.objects.create(
                title='Valid Title',
                content='   \n\t   ',  # Only whitespace
                author=self.user
            )

    def test_post_timestamps_business_logic(self):
        """Test business rule: Updated timestamp changes on edits"""
        post = Post.objects.create(
            title='Original Title',
            content='Original content',
            author=self.user
        )
        
        original_created = post.created_at
        original_updated = post.updated_at
        
        # Small delay to ensure timestamp difference
        time.sleep(0.01)
        
        # Update the post
        post.title = 'Updated Title'
        post.save()
        
        # Business rule: created_at should NOT change
        self.assertEqual(post.created_at, original_created)
        
        # Business rule: updated_at SHOULD change
        self.assertGreater(post.updated_at, original_updated)

    def test_duplicate_titles_allowed_per_user(self):
        """Test business rule: Users can have multiple posts with same title"""
        # Create first post
        Post.objects.create(
            title='Chemistry Notes',
            content='First set of chemistry notes',
            author=self.user
        )
        
        # Create second post with same title (should be allowed)
        post2 = Post.objects.create(
            title='Chemistry Notes',  # Same title
            content='Second set of chemistry notes',
            author=self.user
        )
        
        # Should succeed - users can have duplicate titles
        self.assertTrue(Post.objects.filter(title='Chemistry Notes', author=self.user).count() == 2)

class PostViewTests(TestCase):
    """Test view functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user
        )

    def test_post_list_view_authenticated(self):
        """Test post list view for authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/posts/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')
        self.assertContains(response, self.user.username)

    def test_post_detail_view_authenticated(self):
        """Test post detail view for authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(f'/posts/{self.post.id}/')
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')
        self.assertContains(response, 'Test content')

    def test_post_edit_view(self):
        """Test post edit functionality"""
        self.client.login(username='testuser', password='testpass123')
        
        # GET edit form
        response = self.client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')
        
        # POST edit form
        response = self.client.post(f'/posts/{self.post.id}/edit/', {
            'title': 'Updated Title',
            'content': 'Updated content'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Verify changes
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Title')
        self.assertEqual(self.post.content, 'Updated content')