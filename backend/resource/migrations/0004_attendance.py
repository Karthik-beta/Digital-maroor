# Generated by Django 5.0.4 on 2024-04-29 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resource', '0003_logs_logs_idno_e2aca0_idx_alter_logs_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employeeid', models.IntegerField()),
                ('employee_name', models.CharField(max_length=100)),
                ('device_enroll_id', models.CharField(max_length=100)),
                ('logdate', models.DateField()),
                ('first_logtime', models.TimeField(blank=True, null=True)),
                ('last_logtime', models.TimeField(blank=True, null=True)),
                ('direction', models.CharField(blank=True, max_length=50, null=True)),
                ('department', models.CharField(max_length=100)),
                ('shortname', models.CharField(blank=True, max_length=50, null=True)),
                ('company', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=100)),
                ('total_time', models.TimeField(blank=True, null=True)),
                ('late_entry', models.TimeField(blank=True, null=True)),
                ('early_exit', models.TimeField(blank=True, null=True)),
                ('overtime', models.TimeField(blank=True, null=True)),
                ('shift_status', models.CharField(blank=True, max_length=50, null=True)),
                ('shift', models.CharField(max_length=100)),
                ('job_type', models.CharField(max_length=100)),
                ('designation', models.CharField(max_length=100)),
                ('category', models.CharField(blank=True, max_length=100, null=True)),
                ('status', models.CharField(max_length=100)),
                ('date_of_joining', models.DateField(blank=True, null=True)),
                ('date_of_leaving', models.DateField(blank=True, null=True)),
                ('gender', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'attendance',
                'unique_together': {('employeeid', 'logdate')},
            },
        ),
    ]