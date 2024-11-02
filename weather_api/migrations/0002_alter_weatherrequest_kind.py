# Generated by Django 5.1.2 on 2024-11-02 12:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('weather_api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weatherrequest',
            name='kind',
            field=models.CharField(choices=[('tg', 'Telegram'), ('api', 'Web API')], max_length=3),
        ),
    ]
