# Generated by Django 4.0.6 on 2022-08-02 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booksshelf', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='author_name',
            field=models.CharField(default='author', max_length=255),
            preserve_default=False,
        ),
    ]
