# Generated by Django 3.2.8 on 2021-10-31 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('films', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='films',
            name='is_voted',
            field=models.BooleanField(default=False),
        ),
    ]