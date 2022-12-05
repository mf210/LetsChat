from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse


def user_directory_path(instance, filename):
    return f'user_{instance.id}/profile_image.png'

def get_default_image_path():
    return "default_images/profile_image.png"


class User(AbstractUser):
    profile_image = models.ImageField(
        max_length=255,
        null=True,
        blank=False,
        upload_to=user_directory_path,
        default=get_default_image_path
    )
    hide_email = models.BooleanField(default=True)

    class Meta:
        ordering = ['-id']

    
    def save(self, *args, **kwargs) -> None:
        if self.pk:
            # Delete old profile image before save the new one
            profile_image = User.objects.get(pk=self.pk).profile_image
            if profile_image.name != get_default_image_path():
                profile_image.delete(save=False)
        return super().save(*args, **kwargs)


    def get_absolute_url(self):
        return reverse('accounts:profile', kwargs={'username': self.username})
