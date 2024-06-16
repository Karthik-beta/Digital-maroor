import pyodbc
import psycopg2
from datetime import datetime
import schedule
import time
import subprocess

# MSSQL database connection details
mssql_conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=HRSERVER;"
    "DATABASE=eBioServerNew;"
    "UID=essl;"
    "PWD=essl"
)

# PostgreSQL database connection details
pg_conn_str = {
    'dbname': 'digital',
    'user': 'postgres',
    'password': 'password123',
    'host': '192.168.2.183',
    'port': '5432'
}

def get_latest_mssql_data():
    conn = pyodbc.connect(mssql_conn_str)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT [ID], [EMPLOYEECODE], [LOGDATETIME], [DEVICENAME], [SERIALNUMBER], [DIRECTION]
        FROM [dbo].[GISLOGS]
        ORDER BY LOGDATETIME DESC
    """)
    
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_last_logdatetime_from_postgres():
    conn = psycopg2.connect(**pg_conn_str)
    cursor = conn.cursor()
    
    cursor.execute("SELECT MAX(logdate || ' ' || logtime) FROM public.logs")
    last_logdatetime = cursor.fetchone()[0]
    
    conn.close()
    if last_logdatetime:
        return datetime.strptime(last_logdatetime, '%Y-%m-%d %H:%M:%S')
    else:
        return None

def insert_into_postgres(data):
    conn = psycopg2.connect(**pg_conn_str)
    cursor = conn.cursor()
    
    insert_query = """
        INSERT INTO public.logs (id, idno, employeeid, logdate, logtime, direction, shortname, serialno)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    for row in data:
        logdate = row.LOGDATETIME.date()
        logtime = row.LOGDATETIME.time()
        cursor.execute(insert_query, (
            row.ID, row.ID, row.EMPLOYEECODE, logdate, logtime, row.DIRECTION, row.DEVICENAME, row.SERIALNUMBER
        ))
    
    conn.commit()
    conn.close()

def execute_post_copy_command():
    # subprocess.run(["docker", "exec", "backend", "python", "manage.py", "at7"])
    subprocess.run(
        ["docker", "exec", "backend", "python", "manage.py", "at7"],
        creationflags=subprocess.CREATE_NO_WINDOW  
    )

def sync_databases():
    last_logdatetime = get_last_logdatetime_from_postgres()
    
    new_data = []
    for row in get_latest_mssql_data():
        if last_logdatetime is None or row.LOGDATETIME > last_logdatetime:
            new_data.append(row)
    
    if new_data:
        insert_into_postgres(new_data)
        execute_post_copy_command()

# Schedule the sync to run every minute
schedule.every(1).minutes.do(sync_databases)

# Run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)
