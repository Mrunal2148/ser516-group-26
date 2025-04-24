FROM maven:3.9.4-eclipse-temurin-17

# Install Python and dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy app code and dependencies
COPY requirements.txt ./
COPY templates ./templates
COPY . .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./src /app

EXPOSE 8004
CMD ["python3", "main.py"]
