FROM gradle:8.7-jdk21 as build
COPY . /home/app
WORKDIR /home/app
RUN gradle bootJar

FROM openjdk:21-jdk-slim
WORKDIR /app
COPY --from=build /home/app/build/libs/*.jar app.jar
EXPOSE 5050
ENTRYPOINT ["java", "-jar", "app.jar"]

