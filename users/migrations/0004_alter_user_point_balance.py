# Generated by Django 3.2.18 on 2023-07-20 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_pointproducts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='point_balance',
            field=models.IntegerField(default=5000),
        ),
    ]