FROM python:3.9-slim

WORKDIR /app

# Copy the requirements.txt file
COPY requirements.txt /app/

# Install the dependencies
RUN pip install -r requirements.txt

# Copy the rest of the application files
COPY . /app

EXPOSE 8000

# Execute the execute_jobs.py script
CMD ["python", "execute_jobs.py"]
