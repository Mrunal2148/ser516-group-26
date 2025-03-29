package com.myproject.controllers;

import com.myproject.services.DefectsRemovedService;
import org.springframework.web.bind.annotation.*;
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
    public Map<String, Object> getBugStatistics(@RequestParam String owner, @RequestParam String repo) {
        return defectsRemovedService.getBugStatistics(owner, repo);
    }

    @GetMapping("/defects-history")
    public List<Map<String, Object>> getDefectsHistory() {
        return defectsRemovedService.getDefectsHistory();
    }
}
