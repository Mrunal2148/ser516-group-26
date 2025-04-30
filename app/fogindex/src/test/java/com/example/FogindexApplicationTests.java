package com.example;

import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;

@SpringBootTest
class FogindexApplicationTests {

    @MockBean
    private FogIndexCalculator fogIndexCalculator; // Replace with your actual service

    @Test
    void contextLoads() {
        // Test if the application context loads successfully
    }
}
