FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python -

# Copy poetry files
COPY pyproject.toml poetry.lock ./

# Configure poetry to not create virtual environment inside container
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-root --no-dev

# Copy application code
COPY . .

# Expose the port the app runs on
EXPOSE 8001

# Command to run the application
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]