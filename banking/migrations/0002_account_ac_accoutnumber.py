# Generated by Django 5.0.6 on 2024-07-17 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('banking', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='AC_AccoutNumber',
            field=models.CharField(blank=True, default='000000000000', max_length=20, null=True),
        ),
    ]