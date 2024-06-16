# resource/management/commands/calculate_attendance.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction, connections
from django.db.models import F, ExpressionWrapper, DateTimeField, TimeField
from datetime import timedelta, datetime, date
from tqdm import tqdm  # For progress bar

from resource.models import Employee, Logs, Attendance
from config.models import Shift

class Command(BaseCommand):
    help = "Calculate and update attendance records from employee logs"

    def handle(self, *args, **options):
        """
        Calculates and updates attendance records for all employees based on their log entries
        using a combination of Django ORM and raw SQL for optimized performance.
        """

        self.stdout.write("Starting attendance calculation...")

        # Step 1: Get current date and timezone
        today = timezone.now().date()
        timezone.activate(timezone.get_default_timezone())

        # Step 2: Define processing duration
        processing_days = 1000  # Define how many days back to process

        self.stdout.write(f"Processing attendance for {processing_days} days.")

        for days_back in tqdm(range(processing_days)):
            target_date = today - timedelta(days=days_back)
            self.process_attendance_for_date(target_date)

        self.stdout.write(self.style.SUCCESS('Attendance calculation completed!'))

    def process_attendance_for_date(self, target_date):
        """
        Processes attendance for all employees on a specific date.

        Args:
            target_date (date): Date for which to process attendance.
        """
        # Use a single transaction for each date to improve performance
        with transaction.atomic():
            # Step 1: Fetch employees with prefetched shifts for optimization
            employees = Employee.objects.select_related('shift').all()

            for employee in employees:
                # Step 2 & 3: Efficiently retrieve first and last logs using raw SQL
                with connections['default'].cursor() as cursor:
                    cursor.execute(
                        """
                        SELECT 
                            MIN(logtime), 
                            MAX(logtime), 
                            (
                                SELECT direction 
                                FROM public.logs 
                                WHERE employeeid = %s AND logdate = %s 
                                ORDER BY logtime DESC 
                                LIMIT 1
                            ) as last_direction,
                            (
                                SELECT shortname 
                                FROM public.logs 
                                WHERE employeeid = %s AND logdate = %s 
                                ORDER BY logtime DESC 
                                LIMIT 1
                            ) as last_shortname
                        FROM public.logs 
                        WHERE employeeid = %s AND logdate = %s;
                        """,
                        [employee.employee_id, target_date, 
                         employee.employee_id, target_date, 
                         employee.employee_id, target_date]
                    )
                    row = cursor.fetchone()

                first_logtime, last_logtime, direction, shortname = row

                # Step 4: Calculate attendance fields if logs exist
                if first_logtime and last_logtime:
                    shift_status = 'P'
                    # Directly use first_logtime and last_logtime here
                    late_entry = self.calculate_late_entry(employee, first_logtime)  
                    early_exit = self.calculate_early_exit(employee, last_logtime)
                    total_time = self.calculate_total_time(first_logtime, last_logtime)
                    overtime = self.calculate_overtime(employee, first_logtime, last_logtime)
                else:
                    first_logtime = None
                    last_logtime = None
                    direction = None
                    shortname = None
                    shift_status = 'A'  
                    late_entry = None
                    early_exit = None
                    total_time = None
                    overtime = None

                # Step 5: Update or create attendance using Django ORM
                Attendance.objects.update_or_create(
                    employeeid=employee,
                    logdate=target_date,
                    defaults={
                        'first_logtime': first_logtime,
                        'last_logtime': last_logtime,
                        'direction': direction,
                        'shortname': shortname,
                        'total_time': total_time,
                        'late_entry': late_entry,
                        'early_exit': early_exit,
                        'overtime': overtime,
                        'shift_status': shift_status,
                    },
                )

    def calculate_late_entry(self, employee, first_logtime):
        """Calculates late entry duration based on shift start time and grace period."""
        if employee.shift:
            # Convert start_time to datetime (using current date)
            start_datetime = datetime.combine(date.today(), employee.shift.start_time) 

            grace_datetime = start_datetime + employee.shift.grace_period
            grace_time = grace_datetime.time() # Get time portion 

            if first_logtime > grace_time:
                return datetime.combine(date.today(), first_logtime) - datetime.combine(date.today(), grace_time) 
        return None

    def calculate_early_exit(self, employee, last_logtime):
        """Calculates early exit duration based on shift end time and grace period."""
        if employee.shift:
            # Convert end_time to datetime (using current date)
            end_datetime = datetime.combine(date.today(), employee.shift.end_time) 

            grace_datetime = end_datetime - employee.shift.grace_period
            grace_time = grace_datetime.time()  # Get time portion

            if last_logtime < grace_time:
                return datetime.combine(date.today(), grace_time) - datetime.combine(date.today(), last_logtime)
        return None

    def calculate_total_time(self, first_logtime, last_logtime):
        """Calculates total time worked based on first and last log times."""
        if first_logtime is not None and last_logtime is not None:
            # Ensure consistent date for calculation (using current date)
            first_datetime = datetime.combine(date.today(), first_logtime) 
            last_datetime = datetime.combine(date.today(), last_logtime)
            return last_datetime - first_datetime 
        return None

    def calculate_overtime(self, employee, first_logtime, last_logtime):
        """Calculates overtime based on shift start/end times and overtime threshold."""
        overtime = timedelta()
        if employee.shift:
            # Convert start_time and end_time to datetime objects (using current date)
            start_datetime = datetime.combine(date.today(), employee.shift.start_time)
            end_datetime = datetime.combine(date.today(), employee.shift.end_time)

            if first_logtime < (start_datetime - employee.shift.overtime_threshold).time():
                overtime += start_datetime - datetime.combine(date.today(), first_logtime)
            if last_logtime > (end_datetime + employee.shift.overtime_threshold).time():
                overtime += datetime.combine(date.today(), last_logtime) - end_datetime 
        return overtime if overtime.total_seconds() > 0 else None