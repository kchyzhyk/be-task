# Generated by Django 5.1.3 on 2024-11-24 16:32

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("tasks", "0005_utilityrate_schedule_name_utilityrate_uri"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="utilityrate",
            name="energy_rate",
        ),
    ]