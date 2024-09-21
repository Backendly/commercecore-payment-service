FROM python:3.9-slim

WORKDIR /app

# Copy the Pipfile and Pipfile.lock first to cache dependencies
COPY Pipfile Pipfile.lock /app/

# Install pipenv
RUN pip install pipenv

RUN pipenv install --deploy --ignore-pipfile

# Copy the rest of the application files
COPY . /app

EXPOSE 8000

# Run FastAPI using Uvicorn
CMD ["pipenv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
