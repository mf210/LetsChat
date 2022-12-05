# Generated by Django 4.1.3 on 2022-12-05 08:40

import accounts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_user_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_image',
            field=models.ImageField(default=accounts.models.get_default_image_path, max_length=255, null=True, upload_to=accounts.models.user_directory_path),
        ),
    ]
