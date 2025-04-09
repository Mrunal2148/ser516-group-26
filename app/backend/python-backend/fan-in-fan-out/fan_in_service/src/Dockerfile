FROM python:3.11-slim
RUN apt-update && apt-get install -y openjdk-11-jdk
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./
EXPOSE 8001
CMD ["python", "main.py"]