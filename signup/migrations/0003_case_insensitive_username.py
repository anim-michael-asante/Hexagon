from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('signup', '0002_profile_fields'),
    ]

    operations = [
        migrations.RunSQL(
            sql='CREATE UNIQUE INDEX IF NOT EXISTS auth_user_username_lower_unique ON auth_user (LOWER(username));',
            reverse_sql='DROP INDEX IF EXISTS auth_user_username_lower_unique;',
        ),
    ]
