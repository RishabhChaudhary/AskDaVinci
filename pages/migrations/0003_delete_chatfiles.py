# Generated by Django 4.2.5 on 2024-01-22 12:03

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("pages", "0002_chatfiles"),
    ]

    operations = [
        migrations.DeleteModel(
            name="ChatFiles",
        ),
    ]