# Generated by Django 4.2.20 on 2025-05-15 14:07

from django.db import migrations, models
import django_cryptography.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_utilisateur_code_utilisateur'),
    ]

    operations = [
        migrations.AddField(
            model_name='utilisateur',
            name='is_2fa_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='utilisateur',
            name='totp_secret',
            field=django_cryptography.fields.encrypt(models.CharField(blank=True, max_length=32, null=True)),
        ),
    ]
