package com.myproject.controllers;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Map;

import org.junit.jupiter.api.AfterEach;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.http.ResponseEntity;

import com.myproject.models.FogIndexResponse;

public class FogIndexControllerTest {

    private static final Path DATA_FILE_PATH = Paths.get("fog_index_data.json");
    private static final Path BACKUP_FILE_PATH = Paths.get("fog_index_data_backup.json");

    @BeforeEach
    void backupJsonFile() throws Exception {
        if (Files.exists(DATA_FILE_PATH)) {
            Files.copy(DATA_FILE_PATH, BACKUP_FILE_PATH, java.nio.file.StandardCopyOption.REPLACE_EXISTING);
        }
    }

    @AfterEach
    void restoreJsonFile() throws Exception {
        Files.deleteIfExists(DATA_FILE_PATH);
        if (Files.exists(BACKUP_FILE_PATH)) {
            Files.copy(BACKUP_FILE_PATH, DATA_FILE_PATH, java.nio.file.StandardCopyOption.REPLACE_EXISTING);
            Files.deleteIfExists(BACKUP_FILE_PATH);
        }
    }

    @Test
    void testHandlePreflight_returnsOk() {
        FogIndexController controller = new FogIndexController();
        ResponseEntity<?> response = controller.handlePreflight();
        assertNotNull(response);
        assertEquals(200, response.getStatusCodeValue(), "Expected 200 OK from preflight handler");
    }

    @Test
    void testCalculateFogIndex_withDummyUrl_returnsError() {
        FogIndexController controller = new FogIndexController();
        // URL that doesn’t point to a Git repo
        String dummyUrl = "https://example.com/archive/main.zip";
    
        FogIndexResponse response = controller.calculateFogIndex(dummyUrl);
    
        assertNotNull(response, "Response should not be null");
        assertNotNull(response.getData(), "Response data should not be null");
        assertTrue(response.getData().get(0).containsKey("error"), 
            "Response data should contain an error key");
    }

    @Test
    void testGetFogIndexHistory_withDummyUrl_returnsEmptyList() {
        FogIndexController controller = new FogIndexController();
        String dummyUrl = "https://example.com/archive/refs/heads/main.zip";

        ResponseEntity<?> response = controller.getFogIndexHistory(dummyUrl);

        // Expect an OK with an empty list because it won't find anything
        assertNotNull(response);
        assertEquals(200, response.getStatusCodeValue(),
            "Expected an HTTP 200 when fetching history");
        assertTrue(response.getBody() instanceof java.util.List,
            "Expected the response body to be a List");
        assertTrue(((java.util.List<?>)response.getBody()).isEmpty(),
            "Expected an empty list for the dummy URL’s history");
    }

    @Test
    void testCalculateFogIndex_SuccessWithRealRepo() {
        FogIndexController controller = new FogIndexController();
        String realRepoUrl = "https://github.com/Mrunal2148/ser516-group-java-2/archive/refs/heads/Period-2.zip";
    
        FogIndexResponse response = controller.calculateFogIndex(realRepoUrl);
    
        assertNotNull(response, "Response should not be null");
        assertNotNull(response.getData(), "Response data should not be null");
    
        Map<String, Object> body = response.getData().get(0);
        assertNotNull(body, "Response body should not be null");
        assertTrue(body.containsKey("fogIndex"), "Body should contain a ‘fogIndex’ key");
        assertTrue(body.containsKey("message"), "Body should contain a ‘message’ key");
        assertEquals("Calculation successful", body.get("message"),
                "Expected a ‘Calculation successful’ message in the response");
    }

    @Test
    void testLoadExistingData_withCorruptedJson_returnsEmptyList() throws Exception {
        java.nio.file.Files.writeString(
            java.nio.file.Paths.get("fog_index_data.json"),
            "INVALID_JSON");

        FogIndexController controller = new FogIndexController();
        ResponseEntity<?> response = controller.getFogIndexHistory("https://some/repo/archive/refs/heads/main.zip");

        assertNotNull(response);
        assertTrue(response.getBody() instanceof java.util.List);
        assertTrue(((java.util.List<?>)response.getBody()).isEmpty(), "Expected empty list on corrupted JSON");
    }

    @Test
    void testCalculateFogIndex_withNonExistentBranch_returnsError() {
        FogIndexController controller = new FogIndexController();
        String bogusBranchUrl = "https://github.com/Mrunal2148/ser516-group-java-2/archive/refs/heads/bogus-branch.zip";
    
        FogIndexResponse response = controller.calculateFogIndex(bogusBranchUrl);
    
        assertNotNull(response, "Response should not be null");
        assertNotNull(response.getData(), "Response data should not be null");
        assertTrue(response.getData().get(0).containsKey("error"), "Response data should contain an error key");
    }

    @Test
    void testCalculateFogIndex_AppendsHistoryForSameRepo() {
        FogIndexController controller = new FogIndexController();
        String repoUrl = "https://github.com/Mrunal2148/ser516-group-java-2/archive/refs/heads/Period-2.zip";

        controller.calculateFogIndex(repoUrl);
        controller.calculateFogIndex(repoUrl);

        ResponseEntity<?> response = controller.getFogIndexHistory(repoUrl);
        assertNotNull(response);
        assertTrue(response.getBody() instanceof java.util.List);

        java.util.List<?> history = (java.util.List<?>) response.getBody();
        assertTrue(history.size() >= 2, "History should have at least 2 entries for repeated analysis");
    }

}