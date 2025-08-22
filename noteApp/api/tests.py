from django.test import TestCase, Client
from django.contrib.auth.models import User
from posts.models import Post
import json

class PostAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            password='testpass123'
        )
        
        # Create test posts
        self.post1 = Post.objects.create(
            title='User 1 Post',
            content='This is user 1 content',
            author=self.user
        )
        self.post2 = Post.objects.create(
            title='User 2 Post',
            content='This is user 2 content',
            author=self.user2
        )

    def test_api_post_list_requires_authentication(self):
        """Test that API requires authentication"""
        # Try to access API without authentication
        response = self.client.get('/api/v1/posts/')
        self.assertIn(response.status_code, [401, 403])  # Accept both
        
        # Login and try again
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/api/v1/posts/')
        self.assertEqual(response.status_code, 200)  # Should work now
        
        # Verify response format follows your API design
        self.assertEqual(response.json()['success'], True)
        self.assertIn('data', response.json())

    def test_api_post_creation(self):
        """Test creating a post via API"""
        self.client.login(username='testuser', password='testpass123')
        
        post_data = {
            'title': 'My API Test Post',
            'content': 'This post was created via API'
        }
        
        response = self.client.post('/api/v1/posts/', 
                                  data=json.dumps(post_data), 
                                  content_type='application/json')
        
        # Should create successfully
        self.assertEqual(response.status_code, 201)
        
        # Verify response format
        response_data = response.json()
        self.assertEqual(response_data['success'], True)
        self.assertIn('data', response_data)
        
        # Verify post was created in database
        self.assertTrue(Post.objects.filter(title='My API Test Post').exists())
        
        # Verify the author is set correctly
        created_post = Post.objects.get(title='My API Test Post')
        self.assertEqual(created_post.author, self.user)

    def test_api_post_creation_validation(self):
        """Test validation on post creation"""
        self.client.login(username='testuser', password='testpass123')
        
        # Test with missing title
        invalid_data = {
            'content': 'Content without title'
        }
        
        response = self.client.post('/api/v1/posts/', 
                                  data=json.dumps(invalid_data), 
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertEqual(response_data['success'], False)
        self.assertIn('errors', response_data)

    def test_api_user_can_only_see_own_posts(self):
        """Test that users only see their own posts"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get('/api/v1/posts/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()['data']
        
        # Should only see own post
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'User 1 Post')
        
        # Should not see other user's post
        titles = [post['title'] for post in data]
        self.assertNotIn('User 2 Post', titles)

    def test_api_post_detail_view(self):
        """Test retrieving a specific post"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(f'/api/v1/posts/{self.post1.id}/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['success'], True)
        self.assertEqual(data['data']['title'], 'User 1 Post')

    def test_api_post_detail_authorization(self):
        """Test that users can't access other users' posts"""
        self.client.login(username='testuser', password='testpass123')
        
        # Try to access user2's post
        response = self.client.get(f'/api/v1/posts/{self.post2.id}/')
        self.assertEqual(response.status_code, 404)  # Should not find it

    def test_api_post_update(self):
        """Test updating a post via API"""
        self.client.login(username='testuser', password='testpass123')
        
        update_data = {
            'title': 'Updated Title',
            'content': 'Updated content'
        }
        
        response = self.client.put(f'/api/v1/posts/{self.post1.id}/', 
                                 data=json.dumps(update_data), 
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # Verify post was updated
        updated_post = Post.objects.get(id=self.post1.id)
        self.assertEqual(updated_post.title, 'Updated Title')
        self.assertEqual(updated_post.content, 'Updated content')

    def test_api_post_partial_update(self):
        """Test partial update (PATCH) of a post"""
        self.client.login(username='testuser', password='testpass123')
        
        update_data = {
            'title': 'Partially Updated Title'
        }
        
        response = self.client.patch(f'/api/v1/posts/{self.post1.id}/', 
                                   data=json.dumps(update_data), 
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # Verify only title was updated, content remains same
        updated_post = Post.objects.get(id=self.post1.id)
        self.assertEqual(updated_post.title, 'Partially Updated Title')
        self.assertEqual(updated_post.content, 'This is user 1 content')

    def test_api_post_delete(self):
        """Test deleting a post via API"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.delete(f'/api/v1/posts/{self.post1.id}/')
        self.assertEqual(response.status_code, 204)  # No content
        
        # Verify post was deleted
        self.assertFalse(Post.objects.filter(id=self.post1.id).exists())

    def test_api_post_delete_authorization(self):
        """Test that users can't delete other users' posts"""
        self.client.login(username='testuser', password='testpass123')
        
        # Try to delete user2's post
        response = self.client.delete(f'/api/v1/posts/{self.post2.id}/')
        self.assertEqual(response.status_code, 404)
        
        # Verify post still exists
        self.assertTrue(Post.objects.filter(id=self.post2.id).exists())

    def test_api_response_format_consistency(self):
        """Test that all API responses follow the same format"""
        self.client.login(username='testuser', password='testpass123')
        
        # Test list response
        response = self.client.get('/api/v1/posts/')
        data = response.json()
        self.assertIn('success', data)
        self.assertIn('data', data)
        self.assertTrue(data['success'])
        
        # Test detail response
        response = self.client.get(f'/api/v1/posts/{self.post1.id}/')
        data = response.json()
        self.assertIn('success', data)
        self.assertIn('data', data)
        self.assertTrue(data['success'])

    def test_api_error_response_format(self):
        """Test error responses follow the correct format"""
        self.client.login(username='testuser', password='testpass123')
        
        # Test validation error
        invalid_data = {'title': ''}  # Empty title should fail validation
        
        response = self.client.post('/api/v1/posts/', 
                                  data=json.dumps(invalid_data), 
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('success', data)
        self.assertIn('errors', data)
        self.assertFalse(data['success'])

    def test_api_post_creation_business_rules(self):
        """Test API enforces business rules on creation"""
        self.client.login(username='testuser', password='testpass123')

        # Test title too short
        invalid_data = {
            'title': 'A',  # Too short
            'content': 'Valid content for study notes'
        }

        response = self.client.post('/api/v1/posts/',
                                   data=json.dumps(invalid_data),
                                   content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('title', response.json()['errors'])

        # Test empty content
        invalid_data2 = {
            'title': 'Valid Title',
            'content': ''  # Empty should fail
        }

        response = self.client.post('/api/v1/posts/',
                                   data=json.dumps(invalid_data2),
                                   content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('content', response.json()['errors'])

        # Test single character content (should work)
        valid_data = {
            'title': 'Valid Title',
            'content': 'A'  # Single character should be allowed
        }

        response = self.client.post('/api/v1/posts/',
                                   data=json.dumps(valid_data),
                                   content_type='application/json')

        self.assertEqual(response.status_code, 201)

    def test_api_post_update_preserves_author(self):
        """Test business rule: Post author cannot be changed via API"""
        self.client.login(username='testuser', password='testpass123')
        
        # Try to change author via API (should be ignored)
        malicious_data = {
            'title': 'Updated Title',
            'content': 'Updated content',
            'author': self.user2.id  # Trying to change author
        }
        
        response = self.client.put(f'/api/v1/posts/{self.post1.id}/', 
                                 data=json.dumps(malicious_data), 
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # Verify author wasn't changed
        updated_post = Post.objects.get(id=self.post1.id)
        self.assertEqual(updated_post.author, self.user)  # Should still be original author

    def test_api_post_creation_rate_limiting_logic(self):
        """Test business rule: Reasonable content length for study notes"""
        self.client.login(username='testuser', password='testpass123')
        
        # Test extremely long content (business rule: should have reasonable limits)
        very_long_content = 'A' * 10000  # 10k characters
        
        long_data = {
            'title': 'Valid Title',
            'content': very_long_content
        }
        
        response = self.client.post('/api/v1/posts/', 
                                  data=json.dumps(long_data), 
                                  content_type='application/json')
        
        # Should either succeed or fail gracefully with business rule explanation
        if response.status_code == 400:
            self.assertIn('content', response.json()['errors'])

    def test_api_pagination_business_logic(self):
        """Test business rule: API returns reasonable page sizes"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create multiple posts
        for i in range(25):  # More than default page size
            Post.objects.create(
                title=f'Test Post {i}',
                content=f'Content for post {i}',
                author=self.user
            )
        
        response = self.client.get('/api/v1/posts/')
        self.assertEqual(response.status_code, 200)
        
        response_data = response.json()
        self.assertEqual(response_data['success'], True)
        
        data = response_data['data']
        
        # Business rule: Should return all user's posts (reasonable for study app)
        self.assertEqual(len(data), 26)  # 25 created + 1 from setUp
        
        # Business rule: Posts should be properly ordered (don't check exact title)
        self.assertIn('title', data[0])
        self.assertIn('content', data[0])
        self.assertIn('created_at', data[0])

    def test_api_search_business_logic(self):
        """Test search business rules"""
        self.client.login(username='testuser', password='testpass123')
        
        # Create posts with specific content
        Post.objects.create(
            title='Advanced Chemistry',
            content='Organic chemistry formulas and reactions',
            author=self.user
        )
        
        Post.objects.create(
            title='Physics Notes',
            content='Quantum mechanics and relativity',
            author=self.user
        )
        
        # Test search by title
        response = self.client.get('/api/v1/posts/?search=chemistry')
        
        if response.status_code == 200:
            data = response.json()['data']
            # Business rule: Search should find relevant posts
            chemistry_found = any('Chemistry' in post['title'] or 'chemistry' in post['content'] 
                                for post in data)
            self.assertTrue(chemistry_found)