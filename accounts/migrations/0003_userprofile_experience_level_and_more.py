# Generated by Django 5.0.6 on 2024-08-11 13:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='experience_level',
            field=models.CharField(blank=True, choices=[('BEGINNER', 'Beginner'), ('INTERMEDIATE_ADVANCED', 'Intermediate & Advanced')], max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='weakness_points',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='age',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='body_fat',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female')], max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='goal',
            field=models.CharField(blank=True, choices=[('weight_loss', 'Weight Loss'), ('weight_gain', 'Weight Gain'), ('muscle_gain', 'Muscle Gain')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='height',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='lifestyle_intensity',
            field=models.CharField(blank=True, choices=[('sedentary', 'Sedentary'), ('moderate', 'Moderate'), ('intensive', 'Intensive')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='recommended_calories',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='weight',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
