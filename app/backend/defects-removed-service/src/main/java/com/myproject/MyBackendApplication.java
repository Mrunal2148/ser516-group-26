package com.myproject;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.ComponentScan;

@SpringBootApplication
@ComponentScan(basePackages = "com.myproject")  // Ensure controllers are scanned
public class MyBackendApplication {
    public static void main(String[] args) {
        SpringApplication.run(MyBackendApplication.class, args);
    }
}


