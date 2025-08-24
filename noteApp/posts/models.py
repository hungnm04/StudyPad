from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxLengthValidator
from django.core.exceptions import ValidationError

class Post(models.Model):
    title = models.CharField(
        max_length=200, 
        validators=[MaxLengthValidator(200, "Title must be less than 200 characters.")]
    )
    content = models.TextField(
        validators=[MaxLengthValidator(10000, "Content must be less than 10,000 characters.")]
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author', '-created_at']),
        ]
    
    def clean(self):
        # Business rule: Title must be meaningful length
        if not self.title or len(self.title.strip()) < 3:
            raise ValidationError({'title': 'Title must be at least 3 characters long.'})
        
        if not self.content or len(self.content.strip()) < 1:
            raise ValidationError({'content': 'Content must be at least 1 character long.'})

    def save(self, *args, **kwargs):
        self.full_clean()  
        super().save(*args, **kwargs)
    
