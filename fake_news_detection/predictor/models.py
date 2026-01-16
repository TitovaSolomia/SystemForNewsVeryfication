from django.db import models
from django.contrib.auth.models import User


class NewsCheck(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()
    result_text = models.CharField(max_length=255) 
    created_at = models.DateTimeField(auto_now_add=True) 

    def __clstr__(self):
        return f"{self.text[:50]}..."