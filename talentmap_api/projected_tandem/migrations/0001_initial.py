# Generated by Django 2.0.13 on 2020-08-21 12:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user_profile', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectedFavoriteTandem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fv_seq_num', models.CharField(max_length=255)),
                ('archived', models.BooleanField(default=False)),
                ('user', models.ForeignKey(help_text='The user to which this favorite belongs', on_delete=django.db.models.deletion.DO_NOTHING, to='user_profile.UserProfile')),
            ],
            options={
                'ordering': ['fv_seq_num'],
                'managed': True,
            },
        ),
        migrations.AlterUniqueTogether(
            name='projectedfavoritetandem',
            unique_together={('fv_seq_num', 'user')},
        ),
    ]
