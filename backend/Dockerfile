
FROM python:3.12-slim

WORKDIR /app

# Python configuration
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask application
COPY app.py .

# Create a non-root user and assign ownership
RUN useradd --create-home appuser \
    && chown -R appuser:appuser /app

# Run the application as a non-root user
USER appuser

# Expose the application port
EXPOSE 5000

# Initialize the database and start Gunicorn
CMD ["sh", "-c", "python -c 'from app import initialize_database; initialize_database()' && exec gunicorn --bind 0.0.0.0:5000 --workers 2 --access-logfile - --error-logfile - app:app"]
```
