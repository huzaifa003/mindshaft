# Generated by Django 5.1.3 on 2024-11-24 13:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rag", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="document",
            name="file",
            field=models.FileField(max_length=255, upload_to="documents/"),
        ),
    ]