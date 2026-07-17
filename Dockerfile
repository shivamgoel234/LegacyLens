# Stage 1: Builder - Install dependencies
FROM python:3.13-alpine AS builder

# Set environment variables to prevent caching and ensure output is sent directly
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies required for building psycopg2 and potentially others
# Using --no-cache with apk is standard practice
RUN apk add --no-cache \
    build-base \
    postgresql-dev

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Copy all requirements files
COPY requirements/*.txt /app/requirements/

# Install Python dependencies into a wheelhouse for faster installation in the final stage
# Install all requirements for testing and development
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements/test.txt


# Stage 2: Final - Build the final application image
FROM python:3.13-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Accept build argument for settings module with a default
ARG DJANGO_SETTINGS_MODULE=konveyor.settings.test
ENV DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}

# Set working directory
WORKDIR /app

# Install system dependencies needed only at runtime (e.g., postgresql-libs for psycopg2)
RUN apk add --no-cache \
    postgresql-libs \
    dos2unix

# Copy installed dependencies from the builder stage's wheelhouse
COPY --from=builder /wheels /wheels
# Copy all requirements files
COPY --from=builder /app/requirements/*.txt /app/requirements/
# Install wheels from the wheelhouse
RUN pip install --no-cache /wheels/*

# Create a non-root user and group for security
RUN addgroup -S app && adduser -S -G app app

# Copy the application code into the container
# This respects the .dockerignore file
COPY . /app/

# Set ownership of the app directory to the non-root user
RUN chown -R app:app /app
# Ensure startup.sh has correct line endings and is executable
RUN dos2unix /app/startup.sh && \
    chmod +x /app/startup.sh

# Create logs, static, and test results directories to prevent FileNotFoundError during startup
RUN mkdir -p /app/logs /app/static /app/staticfiles /app/tests/results && \
    chown -R app:app /app/logs /app/static /app/staticfiles /app/tests/results && \
    chmod -R 777 /app/tests/results

# Switch to the non-root user
USER app

# Expose the port Gunicorn will run on (default is 8000)
EXPOSE 8000

# Set the entrypoint to our script that handles migrations, collectstatic, etc.
ENTRYPOINT ["/app/startup.sh"]

# Default command runs gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "konveyor.wsgi:application"]
