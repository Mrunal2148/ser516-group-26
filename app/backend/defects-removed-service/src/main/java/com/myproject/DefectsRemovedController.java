package com.myproject;

import com.myproject.DefectsRemovedService;
import com.myproject.BugStatsResponse;
import org.springframework.web.bind.annotation.*;

import java.util.Collections;
import java.util.Date;
import java.util.List;
import java.util.Map;

@RestController
public class DefectsRemovedController {

    private final DefectsRemovedService defectsRemovedService;

    public DefectsRemovedController(DefectsRemovedService defectsRemovedService) {
        this.defectsRemovedService = defectsRemovedService;
    }

    @PostMapping("/defects-stats")
    public BugStatsResponse getBugStatistics(@RequestBody Map<String, String> body) {
        String repoUrl = body.get("repo_url");
        if (repoUrl == null || !repoUrl.startsWith("https://github.com/")) {
            throw new IllegalArgumentException("Invalid or missing 'repo_url'");
        }

        String[] parts = extractOwnerAndRepo(repoUrl);
        String owner = parts[0];
        String repo = parts[1];

        Map<String, Object> statsMap = defectsRemovedService.getBugStatistics(owner, repo);
        List<Map<String, Object>> wrappedList = Collections.singletonList(statsMap);
        return new BugStatsResponse(new Date(), wrappedList);
    }

    private String[] extractOwnerAndRepo(String repoUrl) {
        String[] segments = repoUrl.replace("https://github.com/", "").split("/");
        return new String[]{segments[0], segments[1]};
    }
}
