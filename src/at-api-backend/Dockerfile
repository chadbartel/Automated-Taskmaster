FROM python:3.12-slim

WORKDIR /app

RUN groupadd --system appuser && useradd --system --gid appuser appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application source code from src/automated-taskmaster into the container's /app
ADD handler.py automated_taskmaster/ app/

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
# For Lambda with Mangum, the handler is specified in Lambda config (e.g., handler.lambda_handler_asgi)
# This CMD is for local 'docker run' testing.
CMD ["uvicorn", "handler:app", "--host", "0.0.0.0", "--port", "8000"]
