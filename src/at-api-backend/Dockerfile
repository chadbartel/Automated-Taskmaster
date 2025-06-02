# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Create a non-root user and group for security
# Running applications as a non-root user is a good security practice.
RUN groupadd --system appuser && useradd --system --gid appuser appuser

# Copy the dependencies file first to leverage Docker cache
# This means if requirements.txt doesn't change, this layer won't be rebuilt.
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# --no-cache-dir reduces image size
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application source code from the build context
# (which is src/automated-taskmaster/) into the WORKDIR (/app) in the container.
# This will copy handler.py and the automated_taskmaster/ sub-package, etc.
COPY . .

# Change ownership of the /app directory to the non-root user
RUN chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Expose port 8000 (standard for Uvicorn/FastAPI, though not directly used by Lambda when invoked via Mangum)
EXPOSE 8000

# Set the CMD to your handler
CMD [ "handler.lambda_handler" ]