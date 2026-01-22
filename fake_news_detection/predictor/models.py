from django.db import models
from django.contrib.auth.models import User


class NewsCheck(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()
    result_text = models.CharField(max_length=255) 
    created_at = models.DateTimeField(auto_now_add=True) 

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        username = self.user.username if self.user else 'Guest'
        return f"{username} - {self.text[:30]}..."