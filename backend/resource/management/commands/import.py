import pyodbc
from django.core.management.base import BaseCommand
from django.db import transaction
from resource.models import Logs
from datetime import datetime
from django.core.management import execute_from_command_line

class Command(BaseCommand):
    """
    Sync logs from MS SQL Server to PostgreSQL.
    """

    def handle(self, *args, **kwargs):
        """
        Handles the command execution.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.
        """
        # MS SQL Server connection details for MS SQL Server 11.0.2100.60 Version
        mssql_conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=HRSERVER;"
            "DATABASE=eBioServerNew;"
            "UID=essl;"
            "PWD=essl;"
        )

        # Connect to MS SQL Server
        mssql_conn = pyodbc.connect(mssql_conn_str)
        cursor = mssql_conn.cursor()

        # Query to fetch data from MS SQL Server
        query = """
        SELECT [ID], [EMPLOYEECODE], [LOGDATETIME], [DEVICENAME],
               [SERIALNUMBER], [DIRECTION]
        FROM [dbo].[GISLOGS]
        ORDER BY LOGDATETIME DESC
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        # Sync data to PostgreSQL
        with transaction.atomic():
            for row in rows:
                idno, employeeid, logdatetime, shortname, serialno, direction = row
                logdate = logdatetime.date()
                logtime = logdatetime.time()

                # Check if the record exists in PostgreSQL
                log_exists = Logs.objects.filter(
                    idno=idno,
                    employeeid=employeeid,
                    logdate=logdate,
                    logtime=logtime,
                    direction=direction,
                    shortname=shortname,
                    serialno=serialno
                ).exists()

                if not log_exists:
                    # Create or update the log
                    Logs.objects.update_or_create(
                        idno=idno,
                        employeeid=employeeid,
                        defaults={
                            'logdate': logdate,
                            'logtime': logtime,
                            'direction': direction,
                            'shortname': shortname,
                            'serialno': serialno
                        }
                    )

        self.stdout.write(self.style.SUCCESS('Successfully synced logs'))

        # Call the other management command 'at7'
        # This is how you call another management command
        execute_from_command_line(['manage.py', 'at7'])
        self.stdout.write(self.style.SUCCESS('Successfully called at7 command'))

        # Close the MS SQL Server connection
        cursor.close()
        mssql_conn.close()