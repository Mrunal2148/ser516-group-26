package com.myproject.services;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;
import org.springframework.http.*;

import java.io.File;
import java.io.IOException;
import java.time.LocalDate;
import java.time.temporal.WeekFields;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class DefectsRemovedService {

    private static final Logger logger = LoggerFactory.getLogger(DefectsRemovedService.class);
    private static final String JSON_FILE_PATH = "defects_data.json";

    @Value("${github.token}")
    private String githubToken;

    private final RestTemplate restTemplate = new RestTemplate();
    private final ObjectMapper objectMapper = new ObjectMapper();

    public Map<String, Object> getBugStatistics(String owner, String repo) {
        Map<String, Integer> weeklyClosedBugs = new HashMap<>();
        Map<String, Integer> weeklyOpenedBugs = new HashMap<>();
        int totalOpenedBugs = 0;
        int totalClosedBugs = 0;

        Map<String, Object> bugStats1 = fetchBugData(owner, repo, "Bug");
        Map<String, Object> bugStats2 = fetchBugData(owner, repo, "Type: Bug");

        mergeBugStatistics(weeklyClosedBugs, (Map<String, Integer>) bugStats1.get("weeklyClosedBugs"));
        mergeBugStatistics(weeklyClosedBugs, (Map<String, Integer>) bugStats2.get("weeklyClosedBugs"));
        mergeBugStatistics(weeklyOpenedBugs, (Map<String, Integer>) bugStats1.get("weeklyOpenedBugs"));
        mergeBugStatistics(weeklyOpenedBugs, (Map<String, Integer>) bugStats2.get("weeklyOpenedBugs"));

        totalOpenedBugs = (int) bugStats1.get("totalOpenedBugs") + (int) bugStats2.get("totalOpenedBugs");
        totalClosedBugs = (int) bugStats1.get("totalClosedBugs") + (int) bugStats2.get("totalClosedBugs");

        double percentageClosed = (totalOpenedBugs > 0) ? ((double) totalClosedBugs / totalOpenedBugs) * 100 : 0;

        LinkedHashMap<String, Integer> sortedOpened = sortWeeklyMap(weeklyOpenedBugs);
        LinkedHashMap<String, Integer> sortedClosed = sortWeeklyMap(weeklyClosedBugs);

        saveDefectsDataToJson(repo, totalOpenedBugs, totalClosedBugs, percentageClosed);

        Map<String, Object> bugStatistics = new HashMap<>();
        bugStatistics.put("weeklyClosedBugs", sortedClosed);
        bugStatistics.put("weeklyOpenedBugs", sortedOpened);
        bugStatistics.put("totalOpenedBugs", totalOpenedBugs);
        bugStatistics.put("totalClosedBugs", totalClosedBugs);
        bugStatistics.put("percentageBugsClosed", percentageClosed);

        return bugStatistics;
    }

    private Map<String, Object> fetchBugData(String owner, String repo, String label) {
        String url = UriComponentsBuilder.fromHttpUrl("https://api.github.com/repos/{owner}/{repo}/issues")
                .queryParam("state", "all")
                .queryParam("labels", label)
                .queryParam("per_page", 100)
                .buildAndExpand(owner, repo)
                .toUriString();

        HttpHeaders headers = new HttpHeaders();
        headers.set("Authorization", "token " + githubToken);
        headers.set("Accept", "application/vnd.github.v3+json");

        HttpEntity<String> entity = new HttpEntity<>(headers);
        ResponseEntity<String> response = restTemplate.exchange(url, HttpMethod.GET, entity, String.class);

        return parseIssues(response.getBody());
    }

    private Map<String, Object> parseIssues(String responseBody) {
        Map<String, Integer> weeklyClosedBugs = new HashMap<>();
        Map<String, Integer> weeklyOpenedBugs = new HashMap<>();
        int totalOpenedBugs = 0;
        int totalClosedBugs = 0;

        try {
            JsonNode issues = objectMapper.readTree(responseBody);
            WeekFields weekFields = WeekFields.of(Locale.getDefault());

            for (JsonNode issue : issues) {
                if (!issue.has("pull_request")) {
                    LocalDate createdDate = LocalDate.parse(issue.get("created_at").asText().substring(0, 10));
                    String createdWeek = createdDate.getYear() + "-W" + createdDate.get(weekFields.weekOfWeekBasedYear());
                    weeklyOpenedBugs.put(createdWeek, weeklyOpenedBugs.getOrDefault(createdWeek, 0) + 1);
                    totalOpenedBugs++;

                    if (issue.has("closed_at") && !issue.get("closed_at").isNull()) {
                        LocalDate closedDate = LocalDate.parse(issue.get("closed_at").asText().substring(0, 10));
                        String closedWeek = closedDate.getYear() + "-W" + closedDate.get(weekFields.weekOfWeekBasedYear());
                        weeklyClosedBugs.put(closedWeek, weeklyClosedBugs.getOrDefault(closedWeek, 0) + 1);
                        totalClosedBugs++;
                    }
                }
            }
        } catch (Exception e) {
            logger.error("Error parsing GitHub API response", e);
        }

        Map<String, Object> result = new HashMap<>();
        result.put("weeklyClosedBugs", weeklyClosedBugs);
        result.put("weeklyOpenedBugs", weeklyOpenedBugs);
        result.put("totalOpenedBugs", totalOpenedBugs);
        result.put("totalClosedBugs", totalClosedBugs);

        return result;
    }

    public List<Map<String, Object>> getDefectsHistory() {
        File file = new File(JSON_FILE_PATH);
        List<Map<String, Object>> jsonData = new ArrayList<>();

        try {
            if (file.exists()) {
                jsonData = objectMapper.readValue(file, List.class);
            }
        } catch (IOException e) {
            logger.error("Error reading defects history JSON", e);
        }

        return jsonData;
    }

    private void mergeBugStatistics(Map<String, Integer> target, Map<String, Integer> source) {
        source.forEach((key, value) -> target.merge(key, value, Integer::sum));
    }

    private LinkedHashMap<String, Integer> sortWeeklyMap(Map<String, Integer> unsortedMap) {
        return unsortedMap.entrySet().stream()
                .sorted(Comparator.comparing(entry -> {
                    String[] parts = entry.getKey().split("-W");
                    return Integer.parseInt(parts[0]) * 100 + Integer.parseInt(parts[1]);
                }))
                .collect(Collectors.toMap(
                        Map.Entry::getKey,
                        Map.Entry::getValue,
                        (oldValue, newValue) -> oldValue,
                        LinkedHashMap::new
                ));
    }

    private void saveDefectsDataToJson(String repoUrl, int totalOpenedBugs, int totalClosedBugs, double percentageClosed) {
        Map<String, Object> data = new HashMap<>();
        data.put("repo_url", repoUrl);
        data.put("total_bugs_opened", totalOpenedBugs);
        data.put("total_bugs_closed", totalClosedBugs);
        data.put("percentage_bugs_closed", percentageClosed);
        data.put("timestamp", new Date().toString());

        File file = new File(JSON_FILE_PATH);
        List<Map<String, Object>> jsonData = new ArrayList<>();

        try {
            if (file.exists()) {
                jsonData = objectMapper.readValue(file, List.class);
            }
            jsonData.add(data);
            objectMapper.writeValue(file, jsonData);
            logger.info("Defects data saved to JSON file.");
        } catch (IOException e) {
            logger.error("Error saving defects data to JSON", e);
        }
    }
}
