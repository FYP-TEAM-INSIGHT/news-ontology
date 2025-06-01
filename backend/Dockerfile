# Choose an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION=2.1.2
ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry'

# Install Poetry
RUN apt-get update && apt-get install -y curl \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get remove -y curl && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*
ENV PATH="$POETRY_HOME/bin:$PATH"

# Set the working directory in the container
WORKDIR /app

# Copy only the dependency definition files first to leverage Docker cache
COPY poetry.lock pyproject.toml ./

# Install project dependencies using Poetry
# --no-root: Do not install the project itself as a package, only dependencies
RUN poetry install --no-interaction --no-ansi --no-root 

# Copy the rest of your application code into the container
COPY ./app ./app
# If you have other directories like 'core' or 'models' at the same level as 'app', copy them too
# COPY ./core ./core
# COPY ./models ./models

# Expose the port your app runs on (e.g., 8000 for FastAPI/Uvicorn by default)
EXPOSE 8000

# Define the command to run your application
# This assumes your FastAPI app instance is named 'app' in 'app/main.py'
# Adjust host and port as needed. 0.0.0.0 makes it accessible from outside the container.
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]