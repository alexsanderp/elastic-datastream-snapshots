FROM python:3.9-slim

WORKDIR /app
COPY src/ .
RUN pip install --no-cache-dir -r requirements.txt
ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "main.py"]
