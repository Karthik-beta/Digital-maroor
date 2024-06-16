import pyodbc

# Define the connection parameters
server = 'HRSERVER'
database = 'eBioServerNew' 
username = 'essl'       
password = 'essl'       # Replace with your password
table_name = 'GISLOGS'   # Replace with your table name

# Define the connection string
connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

def test_connection():
    try:
        # Establish the connection
        with pyodbc.connect(connection_string) as conn:
            print("Connection established successfully.")

            # Create a cursor from the connection
            cursor = conn.cursor()

            # Check if the table exists
            cursor.execute(f"SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table_name}'")
            if cursor.fetchone():
                print(f"Table '{table_name}' exists.")
            else:
                print(f"Table '{table_name}' does not exist.")
    except Exception as e:
        print("An error occurred while connecting to the database:", e)

if __name__ == "__main__":
    test_connection()
