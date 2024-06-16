# resource/management/commands/calculate_attendance.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from datetime import timedelta, datetime, date
from tqdm import tqdm
import asyncio

from resource.models import Employee, Logs, Attendance
from asgiref.sync import sync_to_async

from asyncpg import create_pool

class Command(BaseCommand):
    help = "Calculate and update attendance records from employee logs"

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=2,
            help='Number of days back to process (default: 1)',
        )

    def handle(self, *args, **options):
        self.stdout.write("Starting attendance calculation...")

        today = timezone.now().date()
        timezone.activate(timezone.get_default_timezone())
        processing_days = options['days']

        self.stdout.write(f"Processing attendance for {processing_days} days.")

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.process_attendance(today, processing_days))

        self.stdout.write(self.style.SUCCESS('Attendance calculation completed!'))

    async def process_attendance(self, today, processing_days):
        # Construct the DSN from Django settings
        db_settings = settings.DATABASES['default']
        dsn = f"postgres://{db_settings['USER']}:{db_settings['PASSWORD']}@{db_settings['HOST']}:{db_settings['PORT']}/{db_settings['NAME']}"

        # Async pool for database connections
        pool = await create_pool(dsn=dsn)

        try:
            for days_back in tqdm(range(processing_days)):
                target_date = today - timedelta(days=days_back)
                await self.process_attendance_for_date(target_date, pool)
        finally:
            await pool.close()

    async def process_attendance_for_date(self, target_date, pool):
        employees = await sync_to_async(list)(Employee.objects.select_related('shift').all())

        async def process_employee(employee):
            async with pool.acquire() as conn:
                async with conn.transaction():
                    row = await conn.fetchrow(
                        """
                        SELECT 
                            MIN(logtime), 
                            MAX(logtime), 
                            (
                                SELECT direction 
                                FROM public.logs 
                                WHERE employeeid = $1::int AND logdate = $2 
                                ORDER BY logtime DESC 
                                LIMIT 1
                            ) as last_direction,
                            (
                                SELECT shortname 
                                FROM public.logs 
                                WHERE employeeid = $1::int AND logdate = $2 
                                ORDER BY logtime DESC 
                                LIMIT 1
                            ) as last_shortname
                        FROM public.logs 
                        WHERE employeeid = $1::int AND logdate = $2;
                        """,
                        int(employee.employee_id), target_date  # Ensure employee_id is cast to int
                    )

                if row:
                    first_logtime, last_logtime, direction, shortname = row
                else:
                    first_logtime = last_logtime = direction = shortname = None

                if first_logtime and last_logtime:
                    shift_status = 'P'
                    late_entry = self.calculate_late_entry(employee, first_logtime)
                    early_exit = self.calculate_early_exit(employee, last_logtime)
                    total_time = self.calculate_total_time(first_logtime, last_logtime)
                    overtime = self.calculate_overtime(employee, first_logtime, last_logtime)
                else:
                    shift_status = 'A'
                    late_entry = early_exit = total_time = overtime = None

                await sync_to_async(Attendance.objects.update_or_create)(
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

        await asyncio.gather(*[process_employee(employee) for employee in employees])

    def calculate_late_entry(self, employee, first_logtime):
        if employee.shift:
            start_datetime = datetime.combine(date.today(), employee.shift.start_time)
            grace_datetime = start_datetime + employee.shift.grace_period
            if first_logtime > grace_datetime.time():
                return datetime.combine(date.today(), first_logtime) - grace_datetime
        return None

    def calculate_early_exit(self, employee, last_logtime):
        if employee.shift:
            end_datetime = datetime.combine(date.today(), employee.shift.end_time)
            grace_datetime = end_datetime - employee.shift.grace_period
            if last_logtime < grace_datetime.time():
                return grace_datetime - datetime.combine(date.today(), last_logtime)
        return None

    def calculate_total_time(self, first_logtime, last_logtime):
        if first_logtime and last_logtime:
            first_datetime = datetime.combine(date.today(), first_logtime)
            last_datetime = datetime.combine(date.today(), last_logtime)
            return last_datetime - first_datetime
        return None

    def calculate_overtime(self, employee, first_logtime, last_logtime):
        overtime = timedelta()
        if employee.shift:
            start_datetime = datetime.combine(date.today(), employee.shift.start_time)
            end_datetime = datetime.combine(date.today(), employee.shift.end_time)
            if first_logtime < (start_datetime - employee.shift.overtime_threshold).time():
                overtime += start_datetime - datetime.combine(date.today(), first_logtime)
            if last_logtime > (end_datetime + employee.shift.overtime_threshold).time():
                overtime += datetime.combine(date.today(), last_logtime) - end_datetime
        return overtime if overtime.total_seconds() > 0 else None
