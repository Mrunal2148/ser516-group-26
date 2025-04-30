package com.example.controller;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.Test;
import org.springframework.http.ResponseEntity;

import com.example.FogIndexResponse;

public class FogIndexControllerTest {

    private final FogIndexController controller = new FogIndexController();

    @Test
    public void testCalculateFogIndexWithInvalidUrl() {
        Map<String, String> requestBody = Map.of("repo_url", "invalid-url");
        FogIndexResponse response = controller.calculateFogIndex(requestBody);

        assertNotNull(response);
        assertEquals(1, response.getData().size());
        assertTrue(response.getData().get(0).containsKey("error"));
    }

    @Test
    public void testHandlePreflight() {
        ResponseEntity<?> response = controller.handlePreflight();
        assertEquals(200, response.getStatusCodeValue());
    }
}
