# Generated by Django 5.0.4 on 2024-05-22 07:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resource', '0009_alter_employee_shift'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='early_exit',
            field=models.DurationField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='late_entry',
            field=models.DurationField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='overtime',
            field=models.DurationField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='attendance',
            name='total_time',
            field=models.DurationField(blank=True, null=True),
        ),
    ]