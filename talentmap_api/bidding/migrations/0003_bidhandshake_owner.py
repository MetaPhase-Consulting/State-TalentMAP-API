# Generated by Django 2.2.18 on 2021-04-16 18:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0002_savedsearch_is_bureau'),
        ('bidding', '0002_bidhandshake'),
    ]

    operations = [
        migrations.AddField(
            model_name='bidhandshake',
            name='owner',
            field=models.ForeignKey(default=1, help_text='The first to initiate the HS', on_delete=django.db.models.deletion.DO_NOTHING, related_name='owner', to='user_profile.UserProfile'),
            preserve_default=False,
        ),
    ]
