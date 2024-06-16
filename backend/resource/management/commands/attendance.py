from django.core.management.base import BaseCommand
from resource.models import Logs, Employee, Attendance
from datetime import datetime, time, timedelta, date
from tqdm import tqdm

class Command(BaseCommand):
    help = 'Update AttendanceRecord based on Logs and EmployeeData'

    def calculate_overtime(self, first_logtime, last_logtime):
        # Implement your overtime calculation logic here
        if first_logtime is not None and first_logtime < time(7, 30):
            morning_overtime_cal = datetime.combine(date.min, time(8, 0)) - datetime.combine(date.min, first_logtime)
            morning_overtime_seconds = int(morning_overtime_cal.total_seconds())
            morning_overtime_minutes = morning_overtime_seconds // 60
        else:
            morning_overtime_minutes = 0

        if last_logtime is not None and last_logtime > time(16, 30):
            evening_overtime_cal = datetime.combine(date.min, last_logtime) - datetime.combine(date.min, time(16, 0))
            evening_overtime_seconds = int(evening_overtime_cal.total_seconds())
            evening_overtime_minutes = evening_overtime_seconds // 60
        else:
            evening_overtime_minutes = 0

        total_overtime_minutes = morning_overtime_minutes + evening_overtime_minutes

        if total_overtime_minutes > 0:
            total_hours, total_minutes = divmod(total_overtime_minutes, 60)
            formatted_overtime = f"{total_hours:02d}:{total_minutes:02d}"
        else:
            formatted_overtime = "00:00"

        return formatted_overtime
    

    def calculate_overtime_OS(self, first_logtime, last_logtime):
        # Implement your overtime calculation logic here
        if first_logtime is not None and first_logtime < time(7, 30):
            morning_overtime_cal = datetime.combine(date.min, time(8, 0)) - datetime.combine(date.min, first_logtime)
            morning_overtime_seconds = int(morning_overtime_cal.total_seconds())
            morning_overtime_minutes = morning_overtime_seconds // 60
        else:
            morning_overtime_minutes = 0

        if last_logtime is not None and last_logtime > time(17, 0):
            evening_overtime_cal = datetime.combine(date.min, last_logtime) - datetime.combine(date.min, time(16, 30))
            evening_overtime_seconds = int(evening_overtime_cal.total_seconds())
            evening_overtime_minutes = evening_overtime_seconds // 60
        else:
            evening_overtime_minutes = 0

        total_overtime_minutes = morning_overtime_minutes + evening_overtime_minutes

        if total_overtime_minutes > 0:
            total_hours, total_minutes = divmod(total_overtime_minutes, 60)
            formatted_overtime = f"{total_hours:02d}:{total_minutes:02d}"
        else:
            formatted_overtime = "00:00"

        return formatted_overtime
    
    def calculate_overtime_HK(self, first_logtime, last_logtime):
        # Implement your overtime calculation logic here
        if first_logtime is not None and first_logtime < time(6, 30):
            morning_overtime_cal = datetime.combine(date.min, time(7, 0)) - datetime.combine(date.min, first_logtime)
            morning_overtime_seconds = int(morning_overtime_cal.total_seconds())
            morning_overtime_minutes = morning_overtime_seconds // 60
        else:
            morning_overtime_minutes = 0

        if last_logtime is not None and last_logtime > time(17, 30):
            evening_overtime_cal = datetime.combine(date.min, last_logtime) - datetime.combine(date.min, time(17, 0))
            evening_overtime_seconds = int(evening_overtime_cal.total_seconds())
            evening_overtime_minutes = evening_overtime_seconds // 60
        else:
            evening_overtime_minutes = 0

        total_overtime_minutes = morning_overtime_minutes + evening_overtime_minutes

        if total_overtime_minutes > 0:
            total_hours, total_minutes = divmod(total_overtime_minutes, 60)
            formatted_overtime = f"{total_hours:02d}:{total_minutes:02d}"
        else:
            formatted_overtime = "00:00"

        return formatted_overtime
    

    def handle(self, *args, **options):
        employee_data_instances = Employee.objects.all()
        all_log_dates = Logs.objects.values_list('logdate', flat=True).distinct()
         
        total_iterations = len(employee_data_instances) * len(all_log_dates)
        progress_bar = tqdm(total=total_iterations, desc="Processing")

        for employee_data in employee_data_instances:
            employee_id = employee_data.employee_id

            for log_date in all_log_dates:
                logs_for_date = Logs.objects.filter(employeeid=employee_id, logdate=log_date)

                if logs_for_date.exists():
                    first_logtime = logs_for_date.earliest('logtime').logtime
                    last_logtime = logs_for_date.latest('logtime').logtime
                    direction = logs_for_date.last().direction
                    shortname = logs_for_date.last().shortname
                    present = True
                else:
                    first_logtime = None
                    last_logtime = None
                    direction = None
                    shortname = None
                    present = False

                total_time = None
                if first_logtime and last_logtime:
                    time_difference = datetime.combine(datetime.min, last_logtime) - datetime.combine(datetime.min, first_logtime)
                    total_seconds = time_difference.total_seconds()
                    hours = int(total_seconds // 3600)
                    minutes = int((total_seconds % 3600) // 60)
                    total_time = f"{hours:02d}:{minutes:02d}"
                                                                       
                if first_logtime is not None:
                    if employee_data.shift == "HK" and first_logtime > time(7, 15):
                        late_difference = datetime.combine(date.min, first_logtime) - datetime.combine(date.min, time(7, 0))
                    elif employee_data.shift == "GS" and first_logtime > time(8, 15):
                        late_difference = datetime.combine(date.min, first_logtime) - datetime.combine(date.min, time(8, 0))
                    else:
                        late_difference = timedelta(0)

                    late_seconds = int(late_difference.total_seconds())
                    late_hours, late_remainder = divmod(late_seconds, 3600)
                    late_minutes, late_seconds = divmod(late_remainder, 60)
                    late_entry = f"{late_hours:02d}:{late_minutes:02d}:{late_seconds:02d}"  

                    if late_entry == "00:00:00":
                        late_entry = None

                else: 
                    late_entry = None


                early_exit = None
                if first_logtime is not None and last_logtime is not None and last_logtime > first_logtime:
                    if employee_data.shift == "OS" and last_logtime < time(16, 15):
                        early_difference = datetime.combine(date.min, time(16, 30)) - datetime.combine(date.min, last_logtime)
                    elif employee_data.shift == "GS" and last_logtime < time(16, 45):
                        early_difference = datetime.combine(date.min, time(17, 0)) - datetime.combine(date.min, last_logtime)
                    elif last_logtime < time(15, 45):
                        early_difference = datetime.combine(date.min, time(16, 0)) - datetime.combine(date.min, last_logtime)
                    else:
                        early_difference = timedelta(0)

                    early_seconds = int(early_difference.total_seconds())
                    early_hours, early_remainder = divmod(early_seconds, 3600)
                    early_minutes, early_seconds = divmod(early_remainder, 60)
                    early_exit = f"{early_hours:02d}:{early_minutes:02d}:{early_seconds:02d}"

                elif first_logtime is None and last_logtime is None:
                        early_exit = None

                overtime = None
                if employee_data.shift == "OS":
                    overtime = self.calculate_overtime_OS(first_logtime, last_logtime)
                elif employee_data.shift == "GS":
                    if first_logtime == last_logtime: 
                        overtime = None
                    else:
                        overtime = self.calculate_overtime_HK(first_logtime, last_logtime)
                    # elif employee_data.shift == "TS":
                    #     overtime = self.calculate_overtime(first_logtime, last_logtime)
                else:
                    overtime = None




                shift_status = None
                if first_logtime is not None and total_time is not None and total_time > "07:30:00":
                    shift_status = "P"
                elif total_time is not None and "04:00:00" < total_time <= "07:30:00":
                    if first_logtime and last_logtime and first_logtime < time(13, 0) and last_logtime < time(13, 0):
                        shift_status = "P/A"
                    elif first_logtime and last_logtime and first_logtime < time(13, 0) and last_logtime < time(16, 0):
                        shift_status = "P/A"
                    elif first_logtime and last_logtime and first_logtime > time(13, 0) and last_logtime > time(13, 0):
                        shift_status = "A/P"

                if first_logtime == last_logtime:
                    shift_status = "A"
                     
                      
                # Fetch the corresponding Employee instance based on the employee_id
                try:
                    employee_instance = Employee.objects.get(employee_id=employee_id)
                except Employee.DoesNotExist:
                    # Handle the case where the employee with the given ID does not exist
                    # You may want to log this or handle it differently based on your requirements
                    employee_instance = None

                Attendance.objects.update_or_create(
                    employeeid=employee_instance,
                    logdate=log_date,
                    defaults={
                        # 'employee_name': employee_data.employee_name,
                        # 'device_enroll_id': employee_data.device_enroll_id,
                        'first_logtime': first_logtime,
                        'last_logtime': last_logtime,
                        'direction': direction,
                        # 'department': employee_data.department,
                        'shortname': shortname,
                        # 'company': employee_data.company,
                        # 'location': employee_data.location,
                        'total_time': total_time,
                        'late_entry': None if late_entry is None or late_entry == timedelta(0) or late_entry.strip() == "00:00:00" else late_entry,
                        'early_exit': None if early_exit is None or early_exit == timedelta(0) or early_exit.strip() == "00:00:00" else early_exit,
                        'overtime': None if overtime is None or overtime == timedelta(0) or overtime.strip() == "00:00:00" else overtime,
                        'shift_status': shift_status,
                        # 'shift': employee_data.shift,
                        # 'job_type': employee_data.job_type,
                        # 'designation': employee_data.designation,
                        # 'category': employee_data.category,
                        # 'status': employee_data.status,
                        'date_of_joining': employee_data.date_of_joining,
                        'date_of_leaving': employee_data.date_of_leaving,
                        # 'gender': employee_data.gender,
                    }
                )

                # if present:
                #     self.stdout.write(self.style.SUCCESS(f'Employee {employee_id} marked present on {log_date}'))
                # else:
                #     self.stdout.write(self.style.SUCCESS(f'Employee {employee_id} marked absent on {log_date}'))
                 
                progress_bar.update(1)  # Update the progress bar
                             
        progress_bar.close()
        self.stdout.write(self.style.SUCCESS('Attendance records updated successfully'))
