package com.example.utils;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.Test;

public class FetchRepoTest {

    @Test
    public void testFetchRepoWithEmptyUrl() {
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            FetchRepo.fetchRepo("");
        });
        assertEquals("No repository URL provided. Please enter a valid GitHub repository URL.", exception.getMessage());
    }

    @Test
    public void testFetchRepoWithMalformedUrl() {
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            FetchRepo.fetchRepo("https://github.com/invalid/repo/malformed-url");
        });
        assertTrue(exception.getMessage().contains("Malformed repository URL"));
    }
}
