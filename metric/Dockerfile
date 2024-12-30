FROM python:3.9-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./
RUN mkdir -p logs
CMD ["python", "metric.py"]