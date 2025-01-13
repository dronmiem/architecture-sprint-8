FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r dependencies.txt
COPY logging_config.yaml /app/
RUN pip install pyyaml
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "/app/logging_config.yaml"]