# Use the official AWS Lambda Python base image for Python 3.12
FROM public.ecr.aws/lambda/python:3.12

# Set the root directory for the Lambda function
ENV LAMBDA_TASK_ROOT=/var/task

# Copy function code
COPY handler.py ${LAMBDA_TASK_ROOT}/

# Copy submodules
COPY automated_taskmaster/ ${LAMBDA_TASK_ROOT}/automated_taskmaster/

# Install dependencies from requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install -r requirements.txt -t ${LAMBDA_TASK_ROOT}/

# Set the CMD to your handler
CMD [ "handler.lambda_handler" ]