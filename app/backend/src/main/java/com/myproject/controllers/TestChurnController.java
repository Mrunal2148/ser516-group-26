package com.myproject.controllers;

import com.myproject.services.TestChurnService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/api/test-churn")
@CrossOrigin(origins = "http://localhost:3000", allowCredentials = "true")
public class TestChurnController {

    private final TestChurnService testChurnService;

    public TestChurnController(TestChurnService testChurnService) {
        this.testChurnService = testChurnService;
    }

    @GetMapping("/calculate")
    public ResponseEntity<Map<String, Object>> calculateTestChurn(
            @RequestParam String owner,
            @RequestParam String repo,
            @RequestParam String startDate,
            @RequestParam String endDate
    ) {
        // 1. Invoke the service
        Map<String, Object> raw = testChurnService.calculateTestChurn(owner, repo, startDate, endDate);

        // 2. Use the endDate parameter as the timestamp at midnight UTC
        String timestamp = endDate + "T00:00:00Z";

        // 3. Build the 'data' array from the three churn metrics
        List<LinkedHashMap<String, Object>> data = new ArrayList<>();
        for (String key : List.of("added_tests", "deleted_tests", "modified_tests")) {
            Object val = raw.get(key);
            int score = (val instanceof Number) ? ((Number) val).intValue() : 0;

            LinkedHashMap<String, Object> entry = new LinkedHashMap<>();
            entry.put("class_name", key);
            entry.put("score",       score);
            data.add(entry);
        }

        // 4. Assemble final JSON
        LinkedHashMap<String, Object> response = new LinkedHashMap<>();
        response.put("timestamp", timestamp);
        response.put("data",      data);

        return ResponseEntity.ok(response);
    }

    @GetMapping("/download-report")
    public ResponseEntity<byte[]> downloadReport() {
        // unchanged
        try {
            java.nio.file.Path reportPath = java.nio.file.Paths.get("test_churn_report.md");
            java.io.File reportFile = reportPath.toFile();

            if (!reportFile.exists()) {
                return ResponseEntity.status(org.springframework.http.HttpStatus.NOT_FOUND)
                        .body("Report file not found!".getBytes());
            }

            byte[] bytes = java.nio.file.Files.readAllBytes(reportPath);
            org.springframework.http.HttpHeaders headers = new org.springframework.http.HttpHeaders();
            headers.add(org.springframework.http.HttpHeaders.CONTENT_DISPOSITION,
                    "attachment; filename=test_churn_report.md");
            headers.add(org.springframework.http.HttpHeaders.CONTENT_TYPE, "text/markdown");

            return ResponseEntity.ok().headers(headers).body(bytes);

        } catch (Exception e) {
            return ResponseEntity.status(org.springframework.http.HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(("Error downloading the report: " + e.getMessage()).getBytes());
        }
    }
}
