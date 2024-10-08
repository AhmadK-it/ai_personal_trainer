# Generated by Django 5.0.6 on 2024-08-09 21:58

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('age', models.IntegerField()),
                ('gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female')], max_length=10)),
                ('weight', models.FloatField()),
                ('height', models.FloatField()),
                ('body_fat', models.FloatField()),
                ('goal', models.CharField(choices=[('weight_loss', 'Weight Loss'), ('weight_gain', 'Weight Gain'), ('muscle_gain', 'Muscle Gain')], max_length=20)),
                ('lifestyle_intensity', models.CharField(choices=[('sedentary', 'Sedentary'), ('moderate', 'Moderate'), ('intensive', 'Intensive')], max_length=20)),
                ('recommended_calories', models.FloatField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
