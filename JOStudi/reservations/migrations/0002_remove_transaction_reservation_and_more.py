# Generated by Django 4.2.20 on 2025-05-06 16:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='transaction',
            name='reservation',
        ),
        migrations.AddField(
            model_name='reservation',
            name='transaction',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='reservations.transaction'),
        ),
    ]
