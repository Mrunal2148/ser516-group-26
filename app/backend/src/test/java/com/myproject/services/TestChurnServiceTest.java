package com.myproject.services;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.*;
import static org.springframework.test.web.client.response.MockRestResponseCreators.*;

class TestChurnServiceTest {

    private TestChurnService testChurnService;
    private RestTemplate restTemplate;
    private ObjectMapper objectMapper;
    private MockRestServiceServer mockServer;

    @BeforeEach
    void setup() {
        restTemplate = new RestTemplate();
        objectMapper = new ObjectMapper();
        testChurnService = new TestChurnService();
        mockServer = MockRestServiceServer.createServer(restTemplate);

        // Inject githubToken via reflection
        try {
            var field = TestChurnService.class.getDeclaredField("githubToken");
            field.setAccessible(true);
            field.set(testChurnService, "mocked-token");
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }

    @Test
    void testDateDifferenceInDays() {
        long days = testChurnService.dateDifferenceInDays("2024-04-01", "2024-04-10");
        assertEquals(9, days);
    }

    @Test
    void testNormalizeFilePaths() {
        Map<String, String> input = Map.of("/react-a12b34c/TestFile.java", "dummy");
        Map<String, String> result = testChurnService.normalizeFilePaths(input);
        assertTrue(result.containsKey("/react/TestFile.java"));
    }

    @Test
    void testExtractTestCases_javaTestCase() {
        String content = "@Test\npublic void shouldPass() {}";
        var result = testChurnService.extractTestCases(content);
        assertTrue(result.contains("shouldPass"));
    }

    @Test
    void testExtractTestCases_jsTestCase() {
        String content = "test('works', () => { expect(true).toBe(true); });";
        var result = testChurnService.extractTestCases(content);
        assertFalse(result.isEmpty());
    }

    @Test
    void testExtractTestMethodBody() {
        String content = "public class A {\n@Test\npublic void demo() {\nSystem.out.println(\"ok\");\n}\n}";
        String body = testChurnService.extractTestMethodBody(content, "demo");
        assertTrue(body.contains("System.out.println"));
    }

    @Test
    void testIsTestFile_withKnownExtensions() {
        assertTrue(testChurnService.isTestFile("/test/exampleTest.java"));
        assertTrue(testChurnService.isTestFile("/unit/sample.test.js"));
    }

    @Test
    void testIsTestFile_withUnknownExtensions() {
        assertFalse(testChurnService.isTestFile("/src/main/App.java"));
    }
} 
