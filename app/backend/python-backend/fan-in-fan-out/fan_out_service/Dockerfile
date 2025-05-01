FROM eclipse-temurin:11-jdk-focal

RUN apt-get update && apt-get install -y python3 python3-pip git

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

EXPOSE 5000
CMD ["python3", "main.py"]
