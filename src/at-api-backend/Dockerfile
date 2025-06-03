# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the root directory for the Lambda function
ENV LAMBDA_TASK_ROOT=/var/task

# Copy function code
COPY requirements.txt handler.py automated_taskmaster/ ${LAMBDA_TASK_ROOT}/

# Install dependencies from requirements.txt
RUN pip install -r requirements.txt -t ${LAMBDA_TASK_ROOT}/

# Set the CMD to your handler
CMD [ "handler.lambda_handler" ]
