from django.db import models
import face_recognition

# Create your models here.

class Personal(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    city = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    avatar = models.ImageField(
        upload_to='personal/avatars/',
        blank=True,
        null=True,
    )
    video = models.FileField(
        upload_to='personal/videos/',
        blank=True,
        null=True,
    )
    face_coordinates = models.JSONField(null=True, blank=True)
    face_encoding = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Personal'
        verbose_name_plural = 'Persons'