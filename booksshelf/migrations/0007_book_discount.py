# Generated by Django 4.0.6 on 2022-08-09 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booksshelf', '0006_alter_userbookrelation_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='discount',
            field=models.PositiveIntegerField(max_length=2, null=True),
        ),
    ]