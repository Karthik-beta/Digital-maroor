# Generated by Django 5.0.4 on 2024-05-08 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resource', '0005_remove_attendance_category_remove_attendance_company_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='attendance',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='employee',
            name='shift',
            field=models.CharField(choices=[('GS', 'General Shift'), ('Day Shift', 'Day Shift'), ('Night Shift', 'Night Shift'), ('Rotational Shift', 'Rotational Shift'), ('Split Shift', 'Split Shift'), ('Flexi Shift', 'Flexi Shift'), ('Other Shift', 'Other Shift')], default='GS', max_length=100),
        ),
    ]
