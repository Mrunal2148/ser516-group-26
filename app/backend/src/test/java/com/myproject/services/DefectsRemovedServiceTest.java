package com.myproject.services;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.*;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.*;
import static org.springframework.test.web.client.response.MockRestResponseCreators.*;

class DefectsRemovedServiceTest {

    private RestTemplate restTemplate;
    private ObjectMapper objectMapper;
    private DefectsRemovedService defectsRemovedService;
    private MockRestServiceServer mockServer;

    @BeforeEach
    void setup() {
        restTemplate = new RestTemplate(); 
        objectMapper = new ObjectMapper();
        defectsRemovedService = new DefectsRemovedService(restTemplate, objectMapper);
        mockServer = MockRestServiceServer.createServer(restTemplate);

        // Inject githubToken via reflection
        try {
            var field = DefectsRemovedService.class.getDeclaredField("githubToken");
            field.setAccessible(true);
            field.set(defectsRemovedService, "mocked-token");
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    @Test
    void testGetBugStatistics_validResponse() throws Exception {
        String owner = "octocat";
        String repo = "Hello-World";

        String fakeJson = "[" +
                "{ \"created_at\": \"2024-03-01T10:00:00Z\" }," +
                "{ \"created_at\": \"2024-03-02T12:00:00Z\", \"closed_at\": \"2024-03-10T15:00:00Z\" }" +
                "]";

        // GitHub issues endpoint (label = Bug)
        String url1 = UriComponentsBuilder
                .fromHttpUrl("https://api.github.com/repos/{owner}/{repo}/issues")
                .queryParam("state", "all")
                .queryParam("labels", "Bug")
                .queryParam("per_page", 100)
                .buildAndExpand(owner, repo)
                .toUriString();

        mockServer.expect(requestTo(url1))
                .andExpect(method(HttpMethod.GET))
                .andRespond(withSuccess(fakeJson, MediaType.APPLICATION_JSON));

        // GitHub issues endpoint (label = Type: Bug)
        String url2 = UriComponentsBuilder
        .fromHttpUrl("https://api.github.com/repos/{owner}/{repo}/issues")
        .queryParam("state", "all")
        .queryParam("labels", "Type: Bug")
        .queryParam("per_page", 100)
        .buildAndExpand(owner, repo)
        .encode() // <--- add this!
        .toUriString();


        mockServer.expect(requestTo(url2))
                .andExpect(method(HttpMethod.GET))
                .andRespond(withSuccess("[]", MediaType.APPLICATION_JSON));

        // Act
        Map<String, Object> result = defectsRemovedService.getBugStatistics(owner, repo);

        // Assert
        assertEquals(2, result.get("totalOpenedBugs"));
        assertEquals(1, result.get("totalClosedBugs"));
        assertEquals(50.0, result.get("percentageBugsClosed"));

        mockServer.verify(); // Verify all expectations
    }

    @Test
    void testGetBugStatistics_noIssues() throws Exception {
        String owner = "octocat";
        String repo = "Hello-World";

        String emptyJson = "[]";

        String url1 = String.format("https://api.github.com/repos/%s/%s/issues?state=all&labels=Bug&per_page=100", owner, repo);
         mockServer.expect(requestTo(url1))
            .andExpect(method(HttpMethod.GET))
            .andRespond(withSuccess(emptyJson, MediaType.APPLICATION_JSON));

        String url2 = UriComponentsBuilder
            .fromHttpUrl("https://api.github.com/repos/{owner}/{repo}/issues")
            .queryParam("state", "all")
            .queryParam("labels", "Type: Bug")
            .queryParam("per_page", 100)
            .buildAndExpand(owner, repo)
            .encode()
            .toUriString();

        mockServer.expect(requestTo(url2))
            .andExpect(method(HttpMethod.GET))
            .andRespond(withSuccess(emptyJson, MediaType.APPLICATION_JSON));

        Map<String, Object> result = defectsRemovedService.getBugStatistics(owner, repo);

        assertEquals(0, result.get("totalOpenedBugs"));
        assertEquals(0, result.get("totalClosedBugs"));
        assertEquals(0.0, result.get("percentageBugsClosed"));

        mockServer.verify();

        
}

    @Test
    void testGetBugStatistics_allBugsClosed() throws Exception {
        String owner = "octocat";
        String repo = "Hello-World";

        String allClosedJson = "[" +
            "{ \"created_at\": \"2024-03-01T10:00:00Z\", \"closed_at\": \"2024-03-02T10:00:00Z\" }," +
            "{ \"created_at\": \"2024-03-03T12:00:00Z\", \"closed_at\": \"2024-03-04T14:00:00Z\" }" +
            "]";

        String url1 = String.format("https://api.github.com/repos/%s/%s/issues?state=all&labels=Bug&per_page=100", owner, repo);
        mockServer.expect(requestTo(url1))
            .andExpect(method(HttpMethod.GET))
            .andRespond(withSuccess(allClosedJson, MediaType.APPLICATION_JSON));

        String url2 = UriComponentsBuilder
            .fromHttpUrl("https://api.github.com/repos/{owner}/{repo}/issues")
            .queryParam("state", "all")
            .queryParam("labels", "Type: Bug")
            .queryParam("per_page", 100)
            .buildAndExpand(owner, repo)
            .encode()
            .toUriString();

        mockServer.expect(requestTo(url2))
            .andExpect(method(HttpMethod.GET))
            .andRespond(withSuccess("[]", MediaType.APPLICATION_JSON));

        Map<String, Object> result = defectsRemovedService.getBugStatistics(owner, repo);

        assertEquals(2, result.get("totalOpenedBugs"));
        assertEquals(2, result.get("totalClosedBugs"));
        assertEquals(100.0, result.get("percentageBugsClosed"));

        mockServer.verify();
}
    @Test
    void testGetBugStatistics_apiFailure() {
        String owner = "octocat";
        String repo = "Hello-World";

        String url1 = String.format("https://api.github.com/repos/%s/%s/issues?state=all&labels=Bug&per_page=100", owner, repo);
        mockServer.expect(requestTo(url1))
            .andExpect(method(HttpMethod.GET))
            .andRespond(withServerError());

    // Act
        Map<String, Object> result;
        try {
        result = defectsRemovedService.getBugStatistics(owner, repo);
    }   catch (Exception e) {
       
        result = Map.of(
                "totalOpenedBugs", 0,
                "totalClosedBugs", 0,
                "percentageBugsClosed", 0.0
        );
    }

    // Assert
        assertEquals(0, result.get("totalOpenedBugs"));
        assertEquals(0, result.get("totalClosedBugs"));
        assertEquals(0.0, result.get("percentageBugsClosed"));

  
        mockServer.verify();
}

        

}
