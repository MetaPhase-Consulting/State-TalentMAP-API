# Generated by Django 2.0.4 on 2019-05-29 19:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0006_importmodel'),
    ]

    operations = [
        migrations.AlterField(
            model_name='importmodel',
            name='source_endpoint',
            field=models.TextField(help_text='The endpoint from which the data originated'),
        ),
    ]
