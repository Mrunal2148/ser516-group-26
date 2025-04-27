package com.myproject.controllers;

import com.myproject.services.DefectsRemovedService;
import com.myproject.models.BugStatsResponse;
import org.springframework.web.bind.annotation.*;
import java.util.Collections;
import java.util.Date;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/github")
public class DefectsRemovedController {

    private final DefectsRemovedService defectsRemovedService;

    public DefectsRemovedController(DefectsRemovedService defectsRemovedService) {
        this.defectsRemovedService = defectsRemovedService;
    }

    @GetMapping("/defects-stats")
public BugStatsResponse getBugStatistics(@RequestParam String owner, @RequestParam String repo) {
    Map<String, Object> statsMap = defectsRemovedService.getBugStatistics(owner, repo);

    // Wrap the map into a list
    List<Map<String, Object>> wrappedList = Collections.singletonList(statsMap);

    return new BugStatsResponse(new Date(), wrappedList);
}

    @GetMapping("/defects-history")
    public BugStatsResponse getDefectsHistory() {
        List<Map<String, Object>> historyData = defectsRemovedService.getDefectsHistory();
        return new BugStatsResponse(new Date(), historyData);
    }
}
