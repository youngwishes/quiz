# Generated by Django 5.0.3 on 2024-04-02 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='next_question_id',
            field=models.IntegerField(null=True),
        ),
    ]
