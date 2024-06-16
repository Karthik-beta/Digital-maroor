from django.core.management.base import BaseCommand
from django.utils import timezone
from resource.models import Employee, Logs, Attendance
from config.models import AutoShift
from django.db import transaction
from tqdm import tqdm
from datetime import datetime, date, timedelta

class Command(BaseCommand):
    help = "Calculate and update attendance records"

    def handle(self, *args, **kwargs):
        # Step 1: Get current date and timezone
        today = timezone.now().date()
        timezone.activate('Asia/Kolkata')  # Set your desired timezone

        # Step 2: Fetch employee IDs from Employee model
        employee_ids = Employee.objects.values_list('employee_id', flat=True)
        days_to_process = 1  # Define how many days back to process
        total_iterations = len(employee_ids) * days_to_process

        with tqdm(total=total_iterations, desc="Processing Attendance") as pbar:
            for employee_id in employee_ids:
                for day_offset in range(days_to_process):
                    processing_date = today - timedelta(days=day_offset)

                    # Step 3: Check if there are any log entries for the employee
                    logs = Logs.objects.filter(
                        employeeid=employee_id,
                        logdate=processing_date,
                    ).order_by('logdate', 'logtime')

                    if not logs:
                        pbar.update(1)
                        continue

                    # Step 4 & 5: Handle shift logic 
                    employee = Employee.objects.get(employee_id=employee_id)
                    # print(f"Processing attendance for Employee ID: {employee_id}")  # Debugging

                    # ***CORRECTED CONDITION:***
                    if employee.shift:  # Only skip if employee has a fixed Shift
                        pbar.update(1)
                        continue 

                    last_attendance = Attendance.objects.filter(
                        employeeid=employee,
                        logdate=processing_date - timedelta(days=1)
                    ).first()

                    previous_day_last_logtime = last_attendance.last_logtime if last_attendance else None
                    
                    # Step 6 & 7: Determine shift and calculate times
                    first_logtime = None
                    last_logtime = None
                    shift_name = None
                    total_time = timedelta()
                    late_entry = timedelta()
                    early_exit = timedelta()
                    overtime = timedelta()
                    
                    for i, log in enumerate(logs):
                        if previous_day_last_logtime and previous_day_last_logtime.time() > log.logtime:
                            # Log entry is from previous day's incomplete shift, continue to next log
                            continue
                        else:
                            # Reset previous day's last log time 
                            previous_day_last_logtime = None
                        
                        log_time = datetime.combine(processing_date, log.logtime).time()  

                        for shift in AutoShift.objects.all():
                            start_time_with_grace_before = (datetime.combine(processing_date, shift.start_time) - shift.grace_period_before_start_time).time()
                            start_time_with_grace_after = (datetime.combine(processing_date, shift.start_time) + shift.grace_period_after_start_time).time()
                            end_time_with_grace_before = (datetime.combine(processing_date, shift.end_time) - shift.grace_period_before_end_time).time()
                            end_time_with_grace_after = (datetime.combine(processing_date, shift.end_time) + shift.grace_period_after_end_time).time()

                            if start_time_with_grace_before <= log_time <= start_time_with_grace_after and not first_logtime:
                                first_logtime = log.logtime
                                shift_name = shift.name

                            if end_time_with_grace_before <= log_time <= end_time_with_grace_after:
                                last_logtime = log.logtime
                                if first_logtime: 
                                    # Convert time objects to datetime objects for the current day
                                    first_log_datetime = datetime.combine(processing_date, first_logtime)
                                    last_log_datetime = datetime.combine(processing_date, last_logtime)

                                    total_time = last_log_datetime - first_log_datetime

                                    # Calculate shift duration using timedelta
                                    shift_duration = timedelta(hours=shift.end_time.hour, minutes=shift.end_time.minute) - \
                                                    timedelta(hours=shift.start_time.hour, minutes=shift.start_time.minute)
                                    
                                    # Example logic for overtime (using timedelta for comparison)
                                    if total_time > shift_duration + shift.overtime_threshold:
                                        overtime = total_time - shift_duration 

                    # Step 8: Update or create attendance record
                    with transaction.atomic():
                        attendance, created = Attendance.objects.update_or_create(
                            employeeid=employee,
                            logdate=processing_date,
                            defaults={
                                'first_logtime': first_logtime,
                                'last_logtime': last_logtime,
                                'direction': log.direction if logs else None, 
                                'shortname': log.shortname if logs else None,
                                'total_time': total_time,
                                'late_entry': late_entry,
                                'early_exit': early_exit,
                                'overtime': overtime,
                                'shift_status': shift_name, 
                            }
                        )

                        # Example usage of attendance and created variables
                        if created:
                            print(f"Created new attendance record: {attendance}")
                        else:
                            print(f"Updated attendance record: {attendance}")

                    pbar.update(1)

        self.stdout.write(self.style.SUCCESS('Attendance records updated successfully!'))