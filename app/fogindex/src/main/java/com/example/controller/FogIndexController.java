package com.example.controller;

import java.util.Collections;
import java.util.Date;
import java.util.Map;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;

import com.example.FogIndexCalculator;
import com.example.FogIndexResponse;
import com.fasterxml.jackson.databind.ObjectMapper;


@RestController
@CrossOrigin(origins = "*")
public class FogIndexController {

    private final ObjectMapper mapper = new ObjectMapper();
    private final FogIndexCalculator calculator = new FogIndexCalculator();  //  Use a single instance

    @RequestMapping("/fogindex")
    public FogIndexResponse calculateFogIndex(@RequestBody Map<String, String> body) {
    String githubUrl = body.get("repo_url");
        try {
            String jsonResult = calculator.calculateFromGitHub(githubUrl);
            Map<String, Object> result = mapper.readValue(jsonResult, Map.class);
            return new FogIndexResponse(new Date(), Collections.singletonList(result));

        } catch (Exception e) {
            System.err.println("Error calculating Fog Index: " + e.getMessage());
            return new FogIndexResponse(new Date(), Collections.singletonList(
                Map.of("error", "Failed to process the request", "details", e.getMessage())
            ));
        }
    }

    @RequestMapping(value = "/fogindex", method = RequestMethod.OPTIONS)
    public ResponseEntity<?> handlePreflight() {
        return ResponseEntity.ok().build();
    }
}
