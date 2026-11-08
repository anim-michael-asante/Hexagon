from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('signup', '0003_case_insensitive_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='accent',
            field=models.CharField(default='navy', max_length=20),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='background',
            field=models.CharField(default='panel', max_length=20),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='foreground',
            field=models.CharField(default='navy', max_length=20),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='mfa_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='mode',
            field=models.CharField(default='Light', max_length=20),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user_image',
            field=models.FileField(blank=True, upload_to='profile-images/'),
        ),
    ]