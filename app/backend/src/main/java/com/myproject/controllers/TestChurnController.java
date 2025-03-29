package com.myproject.controllers;

import com.myproject.services.TestChurnService;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Map;

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
        Map<String, Object> testChurn = testChurnService.calculateTestChurn(owner, repo, startDate, endDate);

        // If a report is generated, add the download link
        if (testChurn.containsKey("report_path")) {
            String reportPath = (String) testChurn.get("report_path");
            File reportFile = new File(reportPath);

            if (reportFile.exists()) {
                testChurn.put("report_download_url", "/api/test-churn/download-report");
            } else {
                testChurn.put("report_download_url", "Report not found");
            }
        }

        return ResponseEntity.ok(testChurn);
    }

    @GetMapping("/download-report")
    public ResponseEntity<byte[]> downloadReport() {
        try {
            Path reportPath = Paths.get("test_churn_report.md");
            File reportFile = reportPath.toFile();

            if (!reportFile.exists()) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(("Report file not found!").getBytes());
            }

            byte[] reportBytes = Files.readAllBytes(reportPath);

            HttpHeaders headers = new HttpHeaders();
            headers.add(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=test_churn_report.md");
            headers.add(HttpHeaders.CONTENT_TYPE, "text/markdown");

            return ResponseEntity.ok()
                    .headers(headers)
                    .body(reportBytes);

        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(("Error downloading the report: " + e.getMessage()).getBytes());
        }
    }
}
