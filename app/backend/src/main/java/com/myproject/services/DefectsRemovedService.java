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

import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.temporal.WeekFields;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class DefectsRemovedService {

    private static final Logger logger = LoggerFactory.getLogger(DefectsRemovedService.class);

    @Value("${github.token}")
    private String githubToken;

    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    public DefectsRemovedService(RestTemplate restTemplate, ObjectMapper objectMapper) {
        this.restTemplate = restTemplate;
        this.objectMapper = objectMapper;
    }

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

        double percentageClosed = (totalOpenedBugs > 0)
                ? ((double) totalClosedBugs / totalOpenedBugs) * 100
                : 0;

        List<String> last90WeekStartDates = getLast90DaysWeekStartDates();

        LinkedHashMap<String, Integer> paddedOpened = padAndSortWeeklyMap(weeklyOpenedBugs, last90WeekStartDates);
        LinkedHashMap<String, Integer> paddedClosed = padAndSortWeeklyMap(weeklyClosedBugs, last90WeekStartDates);

        Map<String, Object> bugStatistics = new HashMap<>();
        bugStatistics.put("weeklyClosedBugs", paddedClosed);
        bugStatistics.put("weeklyOpenedBugs", paddedOpened);
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
            LocalDate ninetyDaysAgo = LocalDate.now().minusDays(90);
            WeekFields weekFields = WeekFields.of(Locale.getDefault());

            for (JsonNode issue : issues) {
                if (!issue.has("pull_request")) {
                    LocalDate createdDate = LocalDate.parse(issue.get("created_at").asText().substring(0, 10));
                    LocalDate createdWeekStart = createdDate.with(weekFields.dayOfWeek(), 1);
                    if (!createdWeekStart.isBefore(ninetyDaysAgo)) {
                        String week = createdWeekStart.toString();
                        weeklyOpenedBugs.put(week, weeklyOpenedBugs.getOrDefault(week, 0) + 1);
                        totalOpenedBugs++;
                    }

                    if (issue.has("closed_at") && !issue.get("closed_at").isNull()) {
                        LocalDate closedDate = LocalDate.parse(issue.get("closed_at").asText().substring(0, 10));
                        LocalDate closedWeekStart = closedDate.with(weekFields.dayOfWeek(), 1);
                        if (!closedWeekStart.isBefore(ninetyDaysAgo)) {
                            String week = closedWeekStart.toString();
                            weeklyClosedBugs.put(week, weeklyClosedBugs.getOrDefault(week, 0) + 1);
                            totalClosedBugs++;
                        }
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

    private LinkedHashMap<String, Integer> padAndSortWeeklyMap(Map<String, Integer> original, List<String> allWeeks) {
        LinkedHashMap<String, Integer> padded = new LinkedHashMap<>();
        for (String week : allWeeks) {
            padded.put(week, original.getOrDefault(week, 0));
        }
        return padded;
    }

    private List<String> getLast90DaysWeekStartDates() {
        LocalDate today = LocalDate.now();
        LocalDate ninetyDaysAgo = today.minusDays(90);
        WeekFields weekFields = WeekFields.of(Locale.getDefault());
        Set<String> weeks = new TreeSet<>();

        for (LocalDate date = ninetyDaysAgo; !date.isAfter(today); date = date.plusDays(1)) {
            LocalDate weekStart = date.with(weekFields.dayOfWeek(), 1);
            weeks.add(weekStart.toString());
        }

        return new ArrayList<>(weeks);
    }

    private void mergeBugStatistics(Map<String, Integer> target, Map<String, Integer> source) {
        source.forEach((key, value) -> target.merge(key, value, Integer::sum));
    }
}
