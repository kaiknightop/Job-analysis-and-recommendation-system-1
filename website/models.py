from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.


class Job(models.Model):
    job_id = models.IntegerField(primary_key=True)
    job = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    work_type = models.CharField(max_length=100)
    full_time_remote = models.CharField(max_length=100)
    job_details = models.TextField()

    def __str__(self):
        return self.job
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    skills = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='default.jpg', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
