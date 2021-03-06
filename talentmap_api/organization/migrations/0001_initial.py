# Generated by Django 2.0.13 on 2020-09-25 15:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Obc',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_string_representation', models.CharField(blank=True, help_text='The string representation of this object', max_length=255, null=True)),
                ('code', models.CharField(db_index=True, help_text='The unique location code', max_length=255, unique=True)),
                ('short_name', models.TextField(help_text='The short name of the location', null=True)),
                ('obc_id', models.TextField(help_text='The OBC ID for this location', null=True)),
            ],
            options={
                'ordering': ['code'],
                'managed': True,
            },
        ),
    ]
