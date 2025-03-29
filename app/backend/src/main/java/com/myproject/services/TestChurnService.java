package com.myproject.services;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;
import java.io.*;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.*;
import java.util.concurrent.TimeUnit;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;


@Service
public class TestChurnService {

    private static final Logger logger = LoggerFactory.getLogger(TestChurnService.class);
    private static final String GITHUB_API_URL = "https://api.github.com/repos/";
    private static final List<String> TEST_FILE_EXTENSIONS = Arrays.asList(".test.js", ".spec.js", ".test.ts", ".test.py", "Test.java", "test.go");

    @Value("${github.token}")
    private String githubToken;

    private final ObjectMapper objectMapper = new ObjectMapper();

    public Map<String, Object> calculateTestChurn(String owner, String repo, String startDate, String endDate) {
        try {
            // Get first and last commit in the range
            String firstCommitSha = getFirstCommitSha(owner, repo, startDate);
            String lastCommitSha = getLastCommitSha(owner, repo, endDate);

            if (firstCommitSha == null || lastCommitSha == null) {
                logger.error("Could not determine commit range.");
                return Collections.emptyMap();
            }

            // logger.info("First commit: " + firstCommitSha+"start date"+startDate);
            // logger.info("Last commit: " + lastCommitSha+"end date"+endDate);

            // Download and extract test files from both commits
            Map<String, String> oldTestFiles = downloadAndExtractTests(owner, repo, firstCommitSha, "old_commit");
            Map<String, String> newTestFiles = downloadAndExtractTests(owner, repo, lastCommitSha, "new_commit");

            return analyzeTestChurn(oldTestFiles, newTestFiles);
        } catch (Exception e) {
            logger.error("Error calculating test churn", e);
            return Collections.emptyMap();
        }
        finally {
            // **Ensure Cleanup Happens After Response is Calculated**
           cleanupDownloadedFiles("old_commit_extracted","old_commit.zip");
           cleanupDownloadedFiles("new_commit_extracted","new_commit.zip");
            
        }
    }
    private String getFirstCommitSha(String owner, String repo, String startDate) throws IOException {
        String closestCommitSha = null;
        String closestCommitDate = null;
        long minDateDifference = Long.MAX_VALUE; // Track the closest commit
    
        int page = 1;
        boolean commitsFound = false;
    
        while (true) {
            // Fetch commits sorted from latest to oldest
            String url = UriComponentsBuilder.fromHttpUrl(GITHUB_API_URL + owner + "/" + repo + "/commits")
                    .queryParam("per_page", 100) // Larger batch size
                    .queryParam("page", page) // Handle pagination
                    .toUriString();
    
            String response = makeGitHubRequest(url);
            JsonNode commitsArray = objectMapper.readTree(response);
    
            if (commitsArray.isEmpty()) break; // No more commits, stop searching
    
            for (JsonNode commitNode : commitsArray) {
                String commitSha = commitNode.get("sha").asText();
                String commitDate = commitNode.get("commit").get("committer").get("date").asText().substring(0, 10); // Extract YYYY-MM-DD
    
                // Calculate the date difference
                long dateDiff = Math.abs(dateDifferenceInDays(startDate, commitDate));
    
                // Find the commit closest to the given date
                if (dateDiff < minDateDifference) {
                    minDateDifference = dateDiff;
                    closestCommitSha = commitSha;
                    closestCommitDate = commitDate;
                    commitsFound = true;
                }
            }
    
            page++; // Fetch next page of commits
            if (page > 10) break; // Prevent infinite loops
        }
    
        if (!commitsFound) {
            logger.error("No commit found near " + startDate);
        } else {
            logger.info("Closest commit found for " + startDate + " → " + closestCommitDate + " (SHA: " + closestCommitSha + ")");
        }
    
        return closestCommitSha;
    }

    private long dateDifferenceInDays(String date1, String date2) {
    try {
        SimpleDateFormat format = new SimpleDateFormat("yyyy-MM-dd");
        Date d1 = format.parse(date1);
        Date d2 = format.parse(date2);
        long diff = Math.abs(d1.getTime() - d2.getTime());
        return TimeUnit.DAYS.convert(diff, TimeUnit.MILLISECONDS);
    } catch (Exception e) {
        logger.error(" Error parsing dates: " + date1 + " and " + date2, e);
        return Long.MAX_VALUE; // Return large value to ignore this commit
    }
}

    
    
    

    private String getLastCommitSha(String owner, String repo, String endDate) throws IOException {
        String url = UriComponentsBuilder.fromHttpUrl(GITHUB_API_URL + owner + "/" + repo + "/commits")
                .queryParam("until", endDate + "T23:59:59Z")
                .queryParam("per_page", 1000)
                .queryParam("order", "desc")
                .toUriString();

        return extractCommitSha(makeGitHubRequest(url));
    }

    private String extractCommitSha(String response) throws IOException {
        JsonNode commitsArray = objectMapper.readTree(response);
        if (!commitsArray.isEmpty() && commitsArray.isArray()) {
            return commitsArray.get(0).get("sha").asText();
        }
        return null;
    }

    private String makeGitHubRequest(String url) throws IOException {
        org.springframework.http.HttpHeaders headers = new org.springframework.http.HttpHeaders();
        headers.set("Authorization", "token " + githubToken);
        headers.set("Accept", "application/vnd.github.v3+json");

        org.springframework.http.HttpEntity<String> entity = new org.springframework.http.HttpEntity<>(headers);
        return new RestTemplate().exchange(url, org.springframework.http.HttpMethod.GET, entity, String.class).getBody();
    }

    private Map<String, String> downloadAndExtractTests(String owner, String repo, String commitSha, String folderName) throws IOException {
        String zipUrl = "https://github.com/" + owner + "/" + repo + "/archive/" + commitSha + ".zip";
        String zipFilePath = folderName + ".zip";
        String extractFolder = folderName + "_extracted";

        logger.info("Downloading ZIP: " + zipUrl);
        downloadFile(zipUrl, zipFilePath);
        extractZip(zipFilePath, extractFolder);

        return getTestFilesFromFolder(new File(extractFolder));
    }

    private void downloadFile(String fileUrl, String destination) throws IOException {
        try (BufferedInputStream in = new BufferedInputStream(new URL(fileUrl).openStream());
             FileOutputStream fileOutputStream = new FileOutputStream(destination)) {
            byte[] buffer = new byte[1024];
            int count;
            while ((count = in.read(buffer, 0, 1024)) != -1) {
                fileOutputStream.write(buffer, 0, count);
            }
        }
    }

    private void extractZip(String zipFilePath, String destinationFolder) throws IOException {
        File destDir = new File(destinationFolder);
        if (!destDir.exists()) destDir.mkdirs();

        try (ZipInputStream zipIn = new ZipInputStream(new FileInputStream(zipFilePath))) {
            ZipEntry entry;
            while ((entry = zipIn.getNextEntry()) != null) {
                File file = new File(destinationFolder, entry.getName());
                if (entry.isDirectory()) {
                    file.mkdirs();
                } else {
                    new File(file.getParent()).mkdirs();
                    try (FileOutputStream fos = new FileOutputStream(file)) {
                        byte[] buffer = new byte[1024];
                        int len;
                        while ((len = zipIn.read(buffer)) > 0) {
                            fos.write(buffer, 0, len);
                        }
                    }
                }
                zipIn.closeEntry();
            }
        }
    }

    private Map<String, String> getTestFilesFromFolder(File folder) throws IOException {
        Map<String, String> testFiles = new HashMap<>();
    
        // Recursive search
        Collection<File> allFiles = FileUtils.listFiles(folder, null, true);
        for (File file : allFiles) {
            String relativePath = file.getAbsolutePath().replace(folder.getAbsolutePath(), "");
    
            // Check if the file is a test file (either by path or extension)
            if (isTestFile(relativePath)) {
                testFiles.put(relativePath, FileUtils.readFileToString(file, "UTF-8"));
            }
        }
        return testFiles;
    }
    
    private Map<String, Object> analyzeTestChurn(Map<String, String> oldTestFiles, Map<String, String> newTestFiles) {
        int addedTests = 0, deletedTests = 0, modifiedTests = 0;
        Set<String> allFiles = new HashSet<>();
    
        // Normalize file paths (remove commit SHA from the path)
        Map<String, String> normalizedOldTestFiles = normalizeFilePaths(oldTestFiles);
        Map<String, String> normalizedNewTestFiles = normalizeFilePaths(newTestFiles);
    
        allFiles.addAll(normalizedOldTestFiles.keySet());
        allFiles.addAll(normalizedNewTestFiles.keySet());
    
        // Report file
        File reportFile = new File("test_churn_report.md");
    
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(reportFile))) {
            writer.write("# Test Churn Report\n");
            writer.write("Generated on: " + new Date() + "\n\n");
    
            for (String filePath : allFiles) {
                String oldContent = normalizedOldTestFiles.getOrDefault(filePath, "");
                String newContent = normalizedNewTestFiles.getOrDefault(filePath, "");
    
                Set<String> oldTests = extractTestCases(oldContent);
                Set<String> newTests = extractTestCases(newContent);
    
                // Finding added tests
                for (String newTest : newTests) {
                    if (!oldTests.contains(newTest)) {
                        addedTests++;
                        writer.write("### ➕ ADDED: `" + newTest + "` (File: `" + filePath + "`)\n\n");
                    }
                }
    
                // Finding deleted tests
                for (String oldTest : oldTests) {
                    if (!newTests.contains(oldTest)) {
                        deletedTests++;
                        writer.write("### ❌ DELETED: `" + oldTest + "` (File: `" + filePath + "`)\n\n");
                    }
                }
    
                // Finding modified tests
                for (String test : oldTests) {
                    if (newTests.contains(test)) {
                        String oldBody = extractTestMethodBody(oldContent, test);
                        String newBody = extractTestMethodBody(newContent, test);
                        if (!oldBody.equals(newBody)) {
                            modifiedTests++;
                            writer.write("### ✏️ MODIFIED: `" + test + "` (File: `" + filePath + "`)\n");
                            writer.write("#### 🟡 Old Version:\n```\n" + oldBody + "\n```\n");
                            writer.write("#### 🟢 New Version:\n```\n" + newBody + "\n```\n\n");
                        }
                    }
                }
            }
    
            writer.write("## Summary\n");
            writer.write("- **Added Tests:** " + addedTests + "\n");
            writer.write("- **Deleted Tests:** " + deletedTests + "\n");
            writer.write("- **Modified Tests:** " + modifiedTests + "\n");
    
        } catch (Exception e) {
            logger.error("Error writing test churn report", e);
        }
    
        Map<String, Object> testChurnMetrics = new HashMap<>();
        testChurnMetrics.put("added_tests", addedTests);
        testChurnMetrics.put("deleted_tests", deletedTests);
        testChurnMetrics.put("modified_tests", modifiedTests);
        testChurnMetrics.put("timestamp", new Date().toString());
        testChurnMetrics.put("report_path", reportFile.getAbsolutePath());
    
        return testChurnMetrics;
    }
    

    // private Map<String, Object> analyzeTestChurn(Map<String, String> oldTestFiles, Map<String, String> newTestFiles) {
    //     int addedTests = 0, deletedTests = 0, modifiedTests = 0;
    //     Set<String> allFiles = new HashSet<>();
    
    //     // Normalize file paths (remove commit SHA from the path)
    //     Map<String, String> normalizedOldTestFiles = normalizeFilePaths(oldTestFiles);
    //     Map<String, String> normalizedNewTestFiles = normalizeFilePaths(newTestFiles);
    
    //     allFiles.addAll(normalizedOldTestFiles.keySet());
    //     allFiles.addAll(normalizedNewTestFiles.keySet());
    
    //    //File logFile = new File("test_churn_log4.txt");
        
    //     // try (BufferedWriter writer = new BufferedWriter(new FileWriter(logFile, true))) {
    //     //     writer.write("==== Test Churn Analysis Log ====\n");
    //     //     writer.write("Timestamp: " + new Date() + "\n");
    //      try{
    //         for (String filePath : allFiles) {
    //             String oldContent = normalizedOldTestFiles.getOrDefault(filePath, "");
    //             String newContent = normalizedNewTestFiles.getOrDefault(filePath, "");
            
    //             Set<String> oldTests = extractTestCases(oldContent);
    //             Set<String> newTests = extractTestCases(newContent);
            
    //             // Finding added tests
    //             for (String newTest : newTests) {
    //                 if (!oldTests.contains(newTest)) {
    //                     addedTests++;
    //                 // writer.write(" ➕ ADDED: " + newTest + " (in file: " + filePath + ")\n");
    //                 //     logger.info("➕ ADDED: " + newTest + " (in file: " + filePath + ")");
    //                 }
    //             }
            
    //             // Finding deleted tests
    //             for (String oldTest : oldTests) {
    //                 if (!newTests.contains(oldTest)) {
    //                     deletedTests++;
    //                     // writer.write(" ❌Deleted: " + oldTest + " (in file: " + filePath + ")\n");
    //                     // logger.info("❌ DELETED: " + oldTest + " (from file: " + filePath + ")");
    //                 }
    //             }
            
    //             // Finding modified tests
    //             for (String test : oldTests) {
    //                 if (newTests.contains(test)) {
    //                     String oldBody = extractTestMethodBody(oldContent, test);
    //                     String newBody = extractTestMethodBody(newContent, test);
    //                     if (!oldBody.equals(newBody)) {
    //                         modifiedTests++;
    //                         // writer.write(" - MODIFIED: " + test + " (in file: " + filePath + ")\n");
    //                         // logger.info("✏️ MODIFIED: " + test + " (in file: " + filePath + ")");
    //                     }
    //                 }
    //             }
    //         }
            
    
    //         //writer.write("==== End of Log ====\n\n");
    //     } catch (Exception e) {
    //         logger.error("Error writing to log file", e);
    //     }
    
    //     Map<String, Object> testChurnMetrics = new HashMap<>();
    //     testChurnMetrics.put("added_tests", addedTests);
    //     testChurnMetrics.put("deleted_tests", deletedTests);
    //     testChurnMetrics.put("modified_tests", modifiedTests);
    //     testChurnMetrics.put("timestamp", new Date().toString());
    
    //     return testChurnMetrics;
    // }
    
    private Map<String, String> normalizeFilePaths(Map<String, String> testFiles) {
        Map<String, String> normalizedFiles = new HashMap<>();
    
        for (Map.Entry<String, String> entry : testFiles.entrySet()) {
            String normalizedPath = entry.getKey().replaceAll("/react-[a-f0-9]+/", "/react/");
            normalizedFiles.put(normalizedPath, entry.getValue());
        }
    
        return normalizedFiles;
    }
    
    private String extractTestMethodBody(String content, String methodName) {
        StringBuilder methodBody = new StringBuilder();
        String[] lines = content.split("\n");
    
        boolean insideMethod = false;
        int braceCount = 0;
    
        for (String line : lines) {
            if (line.contains("void " + methodName + "(")) {
                insideMethod = true;
            }
            if (insideMethod) {
                methodBody.append(line).append("\n");
                if (line.contains("{")) braceCount++;
                if (line.contains("}")) braceCount--;
                if (braceCount == 0 && insideMethod) {
                    break; // End of method body
                }
            }
        }
        return methodBody.toString();
    }
    
    private Set<String> extractTestCases(String content) {
        Set<String> testCases = new HashSet<>();
        String[] lines = content.split("\n");
        boolean insideTestMethod = false;
        StringBuilder currentMethod = new StringBuilder();
    
        for (String line : lines) {
            line = line.trim();
    
            // Java @Test methods
            if (line.matches(".*@Test.*")) {
                insideTestMethod = true;
                currentMethod = new StringBuilder();
            }
    
            if (insideTestMethod) {
                currentMethod.append(line).append("\n");
            }
    
            // Java method signature (assumes @Test is followed by a method)
            if (line.matches(".*public\\s+void\\s+\\w+\\s*\\(.*\\).*") && insideTestMethod) {
                String methodName = line.replaceAll(".*public\\s+void\\s+(\\w+)\\s*\\(.*", "$1");
                testCases.add(methodName);
                insideTestMethod = false; // End method tracking
            }
    
            // Detect test cases for JS, Python, etc.
            if (line.matches(".*test\\s*\\(.*") ||  
                line.matches(".*it\\s*\\(.*") ||    
                line.matches(".*describe\\s*\\(.*") || 
                line.matches(".*def test_.*") ||    
                line.matches(".*expect\\s*\\(.*") || 
                line.matches(".*render\\s*\\(.*") || 
                line.matches(".*QUnit\\.test\\s*\\(.*") || 
                line.matches(".*QUnit\\.module\\s*\\(.*")) { 
    
                testCases.add(line);
            }
        }
        return testCases;
    }
    
    

    private boolean isTestFile(String filePath) {
        String lowerCasePath = filePath.toLowerCase();
    
        if (lowerCasePath.contains("/test/") || lowerCasePath.contains("/tests/") ||
            lowerCasePath.contains("/__tests__/") || lowerCasePath.contains("/cypress/") ||
            lowerCasePath.contains("/unit/") || lowerCasePath.contains("/integration/") ||
            lowerCasePath.contains("/tests/unit/") || lowerCasePath.contains("/tests/integration/")) {
            return true;
        }
    
        return TEST_FILE_EXTENSIONS.stream().anyMatch(lowerCasePath::endsWith);
    }


    private void cleanupDownloadedFiles(String folderName, String zipFileName) {
        if (folderName == null || zipFileName == null) return; // Skip if null
        File folder = new File(folderName);
        File zipFile = new File(zipFileName);
    
        try {

            // Delete extracted folder
            if (folder.exists()) {
                FileUtils.deleteDirectory(folder);
                logger.info("Successfully deleted folder: " + folder.getAbsolutePath());
            } else {
                logger.warn("Folder not found: " + folder.getAbsolutePath());
            }
    
            // Delete ZIP file
            if (zipFile.exists()) {
                zipFile.delete();
                logger.info("Successfully deleted ZIP file: " + zipFile.getAbsolutePath());
            } else {
                logger.warn("ZIP file not found: " + zipFile.getAbsolutePath());
            }
        } catch (IOException e) {
            logger.error("Error deleting files: " + folder.getAbsolutePath() + " or " + zipFile.getAbsolutePath(), e);
        }
    }
}


