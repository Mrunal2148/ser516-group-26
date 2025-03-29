package com.myproject.controllers;

import java.io.File;
import java.io.IOException;
import java.nio.file.Paths;
import java.time.Instant;
import java.util.*;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.myproject.utils.FogIndexCalculator;

@RestController
@RequestMapping("/api/fog-index")
@CrossOrigin(origins = "http://localhost:3000", allowCredentials = "true")
public class FogIndexController {

    private static final String DATA_FILE = "fog_index_data.json";
    private final ObjectMapper mapper = new ObjectMapper();
    private final FogIndexCalculator calculator = new FogIndexCalculator();  //  Use a single instance

    @GetMapping("/calculate")
    public ResponseEntity<Map<String, Object>> calculateFogIndex(@RequestParam String githubZipUrl) {
        try {
            System.out.println("Received request for: " + githubZipUrl);
            String defaultBranch = calculator.getDefaultBranch(githubZipUrl);
            System.out.println("default branch : "+defaultBranch);
            if (defaultBranch == null) {
                return ResponseEntity.status(500).body(Collections.singletonMap("error", "Failed to determine default branch"));
            }

            String correctedZipUrl = githubZipUrl.replace("/archive/main.zip", "/archive/refs/heads/" + defaultBranch + ".zip");
            System.out.println("Using ZIP URL: " + correctedZipUrl);
            String jsonResult = calculator.calculateFromGitHub(correctedZipUrl);
            Map<String, Object> result = mapper.readValue(jsonResult, Map.class);



     String truncatedRepoName = correctedZipUrl.replace("/archive/refs/heads/" + defaultBranch + ".zip", "");
            List<Map<String, Object>> repoList = loadExistingData();
            Map<String, Object> existingRepo = repoList.stream()
                .filter(repo -> repo.get("repo").equals(truncatedRepoName))
                .findFirst()
                .orElse(null);

            Map<String, Object> historyEntry = new HashMap<>();
            historyEntry.put("fogIndex", result.get("fogIndex"));
            historyEntry.put("generatedTime", Instant.now().toString());
            historyEntry.put("metric", "fog-index");

            if (existingRepo == null) {
                Map<String, Object> newRepoEntry = new HashMap<>();
                newRepoEntry.put("repo", truncatedRepoName);
                newRepoEntry.put("history", new ArrayList<>(Collections.singletonList(historyEntry)));
                repoList.add(newRepoEntry);
            } else {
                List<Map<String, Object>> history = (List<Map<String, Object>>) existingRepo.get("history");
                history.add(historyEntry);
            }
            
            saveData(repoList);
            System.out.println(" Saved Data for: " + truncatedRepoName);
            result.put("message", "Calculation successful");
            return ResponseEntity.ok(result);

        } catch (Exception e) {
            System.err.println("Error calculating Fog Index: " + e.getMessage());
            Map<String, Object> errorResponse = new HashMap<>();
            errorResponse.put("error", "Failed to process the request");
            errorResponse.put("details", e.getMessage());
            return ResponseEntity.status(500).body(errorResponse);
        }
    }

    @GetMapping("/history")
    public ResponseEntity<List<Map<String, Object>>> getFogIndexHistory(@RequestParam String repoUrl) {
        try {
            System.out.println("Fetching history for: " + repoUrl);

          
            String defaultBranch = calculator.getDefaultBranch(repoUrl);
            String truncatedRepoName = repoUrl.replace("/archive/refs/heads/" + defaultBranch + ".zip", "");

            System.out.println("truncated url for history"+truncatedRepoName);
            List<Map<String, Object>> repoList = loadExistingData();
            Map<String, Object> repoEntry = repoList.stream()
                .filter(repo -> repo.get("repo").equals(truncatedRepoName))
                .findFirst()
                .orElse(null);

            if (repoEntry == null) {
                return ResponseEntity.ok(Collections.emptyList());
            }

            List<Map<String, Object>> history = (List<Map<String, Object>>) repoEntry.get("history");
            System.out.println(" Retrieved History Data: " + history);
            return ResponseEntity.ok(history);

        } catch (Exception e) {
            System.err.println(" Error fetching history: " + e.getMessage());
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
            System.err.println(" Error reading history file: " + e.getMessage());
            return new ArrayList<>();
        }
    }

    private void saveData(List<Map<String, Object>> data) {
        try {
            mapper.writeValue(Paths.get(DATA_FILE).toFile(), data);
        } catch (IOException e) {
            System.err.println("Error saving history file: " + e.getMessage());
        }
    }

    @RequestMapping(value = "/calculate", method = RequestMethod.OPTIONS)
    public ResponseEntity<?> handlePreflight() {
        return ResponseEntity.ok().build();
    }
}
