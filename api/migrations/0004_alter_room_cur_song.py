# Generated by Django 4.2.6 on 2023-11-02 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_room_cur_song'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='cur_song',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
