# Generated by Django 5.0.6 on 2024-08-03 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0005_emaildevice'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactions',
            name='TC_balance',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
