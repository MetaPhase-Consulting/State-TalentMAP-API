# Generated by Django 2.0.4 on 2019-07-29 02:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('integrations', '0007_auto_20190529_1910'),
    ]

    operations = [
        migrations.CreateModel(
            name='SynchronizationTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date_time', models.DateTimeField(help_text='Time the task started', null=True)),
                ('end_date_time', models.DateTimeField(help_text='Time the task ended', null=True)),
                ('running', models.BooleanField(default=False, help_text='Whether the synchronization task is currently running')),
                ('talentmap_model', models.TextField(help_text='The talentmap model as a string; e.g. position.Position')),
                ('priority', models.IntegerField(default=0, help_text='The job priority, higher numbers run later. Default 0')),
                ('use_last_date_updated', models.BooleanField(default=False, help_text='Denotes if the job should only pull newest records')),
                ('new_count', models.IntegerField(help_text='Number of new records', null=True)),
                ('updated_count', models.IntegerField(help_text='Number of updated records', null=True)),
                ('job', models.ForeignKey(help_text='The job for this task', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='job', to='integrations.SynchronizationJob')),
            ],
            options={
                'ordering': ['start_date_time'],
                'managed': True,
            },
        ),
    ]
