from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('signup', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='institution',
            new_name='projector_id',
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='projector_id',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='phone_number',
            field=models.CharField(default='', max_length=30),
            preserve_default=False,
        ),
    ]
