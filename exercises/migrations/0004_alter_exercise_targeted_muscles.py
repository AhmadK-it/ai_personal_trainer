# Generated by Django 5.0.6 on 2024-06-23 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exercises', '0003_alter_exercise_groupname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exercise',
            name='targeted_muscles',
            field=models.TextField(verbose_name='targeted muscles'),
        ),
    ]
