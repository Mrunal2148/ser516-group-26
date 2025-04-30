package com.example;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.stereotype.Service;

import com.example.utils.FetchRepo;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;

@Service
public class FogIndexCalculator {

    private final ObjectMapper objectMapper = new ObjectMapper();

    private static final List<String> TEXT_FILE_EXTENSIONS = Arrays.asList(
            ".java", ".txt", ".md", ".xml", ".json", ".html", ".csv");

    public String calculateFromGitHub(String githubRepoUrl) throws Exception {
        System.out.println("Fetching repository from shared volume: " + githubRepoUrl);

        Object fetchResult = FetchRepo.fetchRepo(githubRepoUrl);
        if (fetchResult instanceof Error) {
            throw new IOException(((Error) fetchResult).getMessage());
        }

        Object[] repoDetails = (Object[]) fetchResult;
        String repoDirPath = (String) repoDetails[1];
        File repoDir = new File(repoDirPath);

        List<File> textFiles = getTextFiles(repoDir);

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

    Map<String, Double> calculateMetrics(String text) {
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

    List<File> getTextFiles(File dir) {
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


    int countWords(String text) {
        if (text == null || text.trim().isEmpty()) {
            return 0;
        }
        return text.trim().split("\\s+").length;
    }

    int countSentences(String text) {
        if (text == null || text.trim().isEmpty()) {
            return 0;
        }
        return text.split("[.!?]+").length;
    }

    int countComplexWords(String text) {
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

    int countSyllables(String word) {
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

    boolean isTextFile(String fileName) {
        return TEXT_FILE_EXTENSIONS.stream().anyMatch(fileName::endsWith);
    }

    String readFile(File file) throws IOException {
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
