# Generated by Django 5.0.6 on 2024-06-23 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exercises', '0002_exercise_groupid_exercise_groupname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exercise',
            name='groupName',
            field=models.CharField(blank=True, default=None, max_length=255, null=True, verbose_name='Exercise group name'),
        ),
    ]
