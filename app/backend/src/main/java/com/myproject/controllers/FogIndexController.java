package com.myproject.controllers;

import java.io.Console;
import java.io.File;
import java.io.IOException;
import java.nio.file.Paths;
import java.time.Instant;
import java.util.*;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import com.fasterxml.jackson.core.type.TypeReference;

import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.myproject.utils.FogIndexCalculator;

@RestController
@RequestMapping("/api/fog-index")
@CrossOrigin(origins = "http://localhost:3000", allowCredentials = "true")
public class FogIndexController {

    private static final String DATA_FILE = "fog_index_data.json";
    private final ObjectMapper mapper = new ObjectMapper();

    @GetMapping("/calculate")
    public ResponseEntity<Map<String, Object>> calculateFogIndex(@RequestParam String githubZipUrl) {
        try {
            FogIndexCalculator calculator = new FogIndexCalculator();
            String jsonResult = calculator.calculateFromGitHub(githubZipUrl);

            // Truncate /archive/refs/heads/main.zip or /archive/main.zip from the URL before saving
            String truncatedRepoName = githubZipUrl.replace("/archive/refs/heads/main.zip", "").replace("/archive/main.zip", "");
            System.out.println("Truncated Repo Name: " + truncatedRepoName); // Add logging

            // Convert JSON string to Map
            Map<String, Object> result = mapper.readValue(jsonResult, Map.class);

            // Load existing history
            List<Map<String, Object>> repoList = loadExistingData();

            // Check if repo exists
            Map<String, Object> existingRepo = repoList.stream()
                .filter(repo -> repo.get("repo").equals(truncatedRepoName))
                .findFirst()
                .orElse(null);

            // Create history entry
            Map<String, Object> historyEntry = new HashMap<>();
            historyEntry.put("fogIndex", result.get("fogIndex"));
            historyEntry.put("generatedTime", Instant.now().toString());
            historyEntry.put("metric", "fog-index");

            if (existingRepo == null) {
                // Create new repo entry
                Map<String, Object> newRepoEntry = new HashMap<>();
                newRepoEntry.put("repo", truncatedRepoName);
                newRepoEntry.put("history", new ArrayList<>(Collections.singletonList(historyEntry)));
                repoList.add(newRepoEntry);
            } else {
                // Append to existing history
                List<Map<String, Object>> history = (List<Map<String, Object>>) existingRepo.get("history");
                history.add(historyEntry);
            }

            // Save back to file
            saveData(repoList);

            System.out.println("Saved data: " + repoList); // Add logging

            result.put("repo", truncatedRepoName);
            result.put("message", "Calculation successful");
            return ResponseEntity.ok(result);

        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("error", "Failed to process the request");
            errorResponse.put("details", e.getMessage());

            return ResponseEntity.status(500).body(errorResponse);
        }
    }

    @GetMapping("/history")
    public ResponseEntity<List<Map<String, Object>>> getFogIndexHistory(@RequestParam String repoUrl) {
        String truncatedRepoName = repoUrl.replace("/archive/refs/heads/main.zip", "").replace("/archive/main.zip", "");
        try {
            List<Map<String, Object>> repoList = loadExistingData();

            Map<String, Object> repoEntry = repoList.stream()
                .filter(repo -> repo.get("repo").equals(truncatedRepoName))
                .findFirst()
                .orElse(null);

            if (repoEntry == null) {
                return ResponseEntity.ok(Collections.emptyList());
            }

            List<Map<String, Object>> history = (List<Map<String, Object>>) repoEntry.get("history");
            System.out.println("Fetched history data: " + history); // Add logging
            return ResponseEntity.ok(history);
        } catch (Exception e) {
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("error", "Failed to fetch the history");
            errorResponse.put("details", e.getMessage());

            return ResponseEntity.status(500).body(Collections.singletonList(errorResponse));
        }
    }

    private List<Map<String, Object>> loadExistingData() {
        try {
            File file = new File(DATA_FILE);
            if (!file.exists()) return new ArrayList<>();
            return mapper.readValue(file, new TypeReference<List<Map<String, Object>>>() {});
        } catch (IOException e) {
            return new ArrayList<>();
        }
    }

    private void saveData(List<Map<String, Object>> data) {
        try {
            mapper.writeValue(Paths.get(DATA_FILE).toFile(), data);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    @RequestMapping(value = "/calculate", method = RequestMethod.OPTIONS)
    public ResponseEntity<?> handlePreflight() {
        return ResponseEntity.ok().build();
    }
}
