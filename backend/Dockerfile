# Use an official Python runtime as a parent image
FROM python:3.11.7

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1 

# Set the working directory in the container
WORKDIR /app

# Install ODBC driver for SQL Server
RUN apt-get update && apt-get install -y gnupg2
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Copy the requirements file and crontab into the container
COPY requirements.txt /app/
COPY crontab /etc/cron.d/cronjob

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Expose port 8000 to the outside world
EXPOSE 8000

# Install cron
RUN apt-get update && apt-get install -y cron

# Create the log file and set permissions
RUN touch /var/log/cron.log && chmod 0644 /var/log/cron.log
RUN chmod 0644 /etc/cron.d/cronjob

# Apply cron job
RUN crontab /etc/cron.d/cronjob

# Run migrations
# RUN python manage.py migrate

# Start cron, tail the log file, and run your application
CMD cron && tail -f /var/log/cron.log & python manage.py runserver 0.0.0.0:8000
