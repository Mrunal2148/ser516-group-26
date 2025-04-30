# Stage 1: Build with Maven
FROM maven:3.8.1-openjdk-17 AS builder

WORKDIR /app

# Pass GitHub token to use private repositories (if applicable)
ARG GITHUB_TOKEN
ENV GITHUB_TOKEN=${GITHUB_TOKEN}

COPY . .


RUN mvn clean package -DskipTests

# Stage 2: Create minimal runtime image
FROM eclipse-temurin:17-jdk-alpine

WORKDIR /app


COPY --from=builder /app/target/*.jar app.jar

ENV SERVER_PORT=5000
ENV GITHUB_TOKEN=${GITHUB_TOKEN}


EXPOSE 5000

ENTRYPOINT ["java", "-jar", "app.jar"]
