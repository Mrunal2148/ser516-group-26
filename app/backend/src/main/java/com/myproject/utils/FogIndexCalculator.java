package com.myproject.utils;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.*;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;
import org.springframework.http.*;
import org.springframework.web.client.RestTemplate;

@Service
public class FogIndexCalculator {

    @Value("${github.token}")
    private String GITHUB_TOKEN; // Inject GitHub token from application.properties

    private final ObjectMapper objectMapper = new ObjectMapper();

    private static final List<String> TEXT_FILE_EXTENSIONS = Arrays.asList(
            ".java", ".txt", ".md", ".xml", ".json", ".html", ".csv");

    public String calculateFromGitHub(String githubZipUrl) throws IOException {
                
        System.out.println("Downloading ZIP from: " + githubZipUrl);

        String outputDir = "github_project";
        downloadAndExtractZip(githubZipUrl, outputDir);
        List<File> textFiles = getTextFiles(new File(outputDir));

        int totalFiles = textFiles.size();
        int totalWords = 0, totalSentences = 0, totalComplexWords = 0;

        for (File file : textFiles) {
            String content = readFile(file);
            Map<String, Double> fileMetrics = calculateMetrics(content);
            totalWords += fileMetrics.get("totalWords").intValue();
            totalSentences += fileMetrics.get("totalSentences").intValue();
            totalComplexWords += fileMetrics.get("complexWords").intValue();
        }

        double averageSentenceLength = totalSentences == 0 ? 0 : (double) totalWords / totalSentences;
        double percentageComplexWords = totalWords == 0 ? 0 : ((double) totalComplexWords / totalWords) * 100;
        double finalFogIndex = 0.4 * (averageSentenceLength + percentageComplexWords);

        Map<String, Object> finalMetrics = new HashMap<>();
        finalMetrics.put("fogIndex", finalFogIndex);
        finalMetrics.put("totalWords", totalWords);
        finalMetrics.put("totalSentences", totalSentences);
        finalMetrics.put("complexWords", totalComplexWords);
        finalMetrics.put("averageSentenceLength", averageSentenceLength);
        finalMetrics.put("percentageComplexWords", percentageComplexWords);
        finalMetrics.put("totalFiles", totalFiles);

        objectMapper.enable(SerializationFeature.INDENT_OUTPUT);
        return objectMapper.writeValueAsString(finalMetrics);
    }

    private void downloadAndExtractZip(String fileUrl, String outputDir) throws IOException {
        System.out.println("Downloading ZIP from: " + fileUrl);

        File dir = new File(outputDir);
        if (dir.exists()) {
            deleteFolder(dir);
        }
        dir.mkdirs();

        URL url = new URL(fileUrl);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");

        if (GITHUB_TOKEN != null && !GITHUB_TOKEN.isEmpty()) {
            conn.setRequestProperty("Authorization", "token " + GITHUB_TOKEN);
        }

        conn.setRequestProperty("Accept", "application/vnd.github.v3.raw");

        int responseCode = conn.getResponseCode();
        if (responseCode != 200) {
            throw new IOException("GitHub API error: " + responseCode);
        }

        try (InputStream inputStream = conn.getInputStream();
             ZipInputStream zipIn = new ZipInputStream(inputStream)) {

            ZipEntry entry;
            byte[] buffer = new byte[1024];

            while ((entry = zipIn.getNextEntry()) != null) {
                File newFile = new File(outputDir, entry.getName());
                if (entry.isDirectory()) {
                    newFile.mkdirs();
                } else {
                    new File(newFile.getParent()).mkdirs();
                    try (FileOutputStream fos = new FileOutputStream(newFile)) {
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

    public String getDefaultBranch(String githubRepoUrl) {
        try {

            String[] parts = githubRepoUrl.replaceAll("(\\.zip|/refs/heads/.*)", "")
                                     .replace("https://github.com/", "")
                                     .split("/");
        if (parts.length < 2) return "main";

        String owner = parts[0];
        String repo = parts[1];
        System.out.println(owner+"........owner");
        System.out.println(repo+"........repo");
        String apiUrl = "https://api.github.com/repos/" + owner + "/" + repo;
    
            HttpHeaders headers = new HttpHeaders();
            headers.set("Authorization", "token" + GITHUB_TOKEN);
    
            HttpEntity<String> entity = new HttpEntity<>(headers);
            RestTemplate restTemplate = new RestTemplate();
            ResponseEntity<String> response = restTemplate.exchange(apiUrl, HttpMethod.GET, entity, String.class);
    
            if (response.getStatusCode() == HttpStatus.OK) {
                ObjectMapper objectMapper = new ObjectMapper();
                JsonNode json = objectMapper.readTree(response.getBody());
                return json.get("default_branch").asText();
            } else {
                System.err.println("GitHub API Error: " + response.getStatusCodeValue());
                return "main";
            }
        } catch (Exception e) {
            System.err.println("Error fetching default branch: " + e.getMessage());
            return "main";
        }
    }
    

    private void deleteFolder(File folder) {
        if (folder.isDirectory()) {
            for (File file : Objects.requireNonNull(folder.listFiles())) {
                deleteFolder(file);
            }
        }
        folder.delete();
    }

    private Map<String, Double> calculateMetrics(String text) {
        int wordCount = countWords(text);
        int sentenceCount = countSentences(text);
        int complexWordCount = countComplexWords(text);

        double averageSentenceLength = (sentenceCount == 0) ? 0 : (double) wordCount / sentenceCount;
        double complexWordPercentage = (wordCount == 0) ? 0 : ((double) complexWordCount / wordCount) * 100;
        double fogIndex = 0.4 * (averageSentenceLength + complexWordPercentage);

        Map<String, Double> metrics = new HashMap<>();
        metrics.put("fogIndex", fogIndex);
        metrics.put("totalWords", (double) wordCount);
        metrics.put("totalSentences", (double) sentenceCount);
        metrics.put("complexWords", (double) complexWordCount);
        metrics.put("averageSentenceLength", averageSentenceLength);
        metrics.put("percentageComplexWords", complexWordPercentage);
        return metrics;
    }

    private List<File> getTextFiles(File dir) {
        List<File> textFiles = new ArrayList<>();
        File[] files = dir.listFiles();
        if (files != null) {
            for (File file : files) {
                if (file.isDirectory()) {
                    textFiles.addAll(getTextFiles(file));
                } else if (isTextFile(file.getName())) {
                    textFiles.add(file);
                }
            }
        }
        return textFiles;
    }


    private int countWords(String text) {
        if (text == null || text.trim().isEmpty()) {
            return 0;
        }
        return text.trim().split("\\s+").length;
    }

    private int countSentences(String text) {
        if (text == null || text.trim().isEmpty()) {
            return 0;
        }
        return text.split("[.!?]+").length;
    }

    private int countComplexWords(String text) {
        if (text == null || text.trim().isEmpty()) {
            return 0;
        }
        String[] words = text.trim().split("\\s+");
        int count = 0;
        for (String word : words) {
            if (countSyllables(word) >= 3) {
                count++;
            }
        }
        return count;
    }

    private int countSyllables(String word) {
        word = word.toLowerCase().replaceAll("[^a-z]", "");
        int count = 0;
        boolean vowelFound = false;
        for (int i = 0; i < word.length(); i++) {
            char c = word.charAt(i);
            if ("aeiouy".indexOf(c) != -1) {
                if (!vowelFound) {
                    count++;
                    vowelFound = true;
                }
            } else {
                vowelFound = false;
            }
        }
        if (word.endsWith("e") && count > 1) {
            count--;
        }
        return count > 0 ? count : 1;
    }

    private boolean isTextFile(String fileName) {
        return TEXT_FILE_EXTENSIONS.stream().anyMatch(fileName::endsWith);
    }

    private String readFile(File file) throws IOException {
        StringBuilder content = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(new FileReader(file))) {
            String line;
            while ((line = reader.readLine()) != null) {
                content.append(line).append(" ");
            }
        }
        return content.toString();
    }
}
