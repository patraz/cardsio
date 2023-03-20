# Generated by Django 3.2.18 on 2023-03-20 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flashcards', '0007_alter_deck_anki'),
    ]

    operations = [
        migrations.CreateModel(
            name='Flashcard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField()),
                ('answer', models.TextField()),
            ],
        ),
        migrations.RenameField(
            model_name='deck',
            old_name='flashcards',
            new_name='list',
        ),
        migrations.AlterField(
            model_name='deck',
            name='csv',
            field=models.FileField(blank=True, null=True, upload_to='csv_files/'),
        ),
    ]
