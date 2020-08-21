# Generated by Django 2.0.13 on 2020-08-21 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AboutPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(help_text='The content of the about page')),
            ],
            options={
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='HomepageBanner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(help_text='The text for the banner', max_length=255)),
                ('is_visible', models.BooleanField(default=False)),
            ],
            options={
                'managed': True,
            },
        ),
    ]
