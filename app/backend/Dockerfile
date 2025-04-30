# # --- Python Backend (save_links.py)---
#     FROM python:3.10 AS python-backend-save-links

#     WORKDIR /app

#     COPY backend/requirements.txt .
    
#     RUN pip install --no-cache-dir -r requirements.txt

#     COPY backend/save_links.py ./

#     EXPOSE 5000

#     CMD ["python", "save_links.py"]

# # --- Python Backend (code_comment.py) ---
#     FROM python:3.10 AS python-backend-code-comment

#     WORKDIR /app
    
#     COPY backend/requirements.txt .
    
#     RUN pip install --no-cache-dir -r requirements.txt
    
#     COPY backend/code_comment.py ./
    
#     EXPOSE 5001
    
#     CMD ["python", "code_comment.py"]
    
# Use a Maven image with OpenJDK 17
FROM maven:3.8.1-openjdk-17 AS java-backend

WORKDIR /app

COPY . .

# Ensure Maven uses the GitHub token when building
ARG GITHUB_TOKEN
ENV GITHUB_TOKEN=${GITHUB_TOKEN}

RUN mvn clean install -DskipTests

EXPOSE 8080

CMD ["mvn", "spring-boot:run"]
