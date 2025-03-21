# Generated by Django 5.1.6 on 2025-03-17 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='survey',
            name='activity_suggestion',
        ),
        migrations.RemoveField(
            model_name='survey',
            name='description',
        ),
        migrations.RemoveField(
            model_name='survey',
            name='name',
        ),
        migrations.RemoveField(
            model_name='survey',
            name='updated_at',
        ),
        migrations.AlterField(
            model_name='survey',
            name='security_features',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AlterField(
            model_name='survey',
            name='technology',
            field=models.JSONField(default=list),
        ),
        migrations.AlterField(
            model_name='survey',
            name='web_backend',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AlterField(
            model_name='survey',
            name='web_database',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AlterField(
            model_name='survey',
            name='web_frontend',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AlterField(
            model_name='survey',
            name='web_hosting',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
    ]
