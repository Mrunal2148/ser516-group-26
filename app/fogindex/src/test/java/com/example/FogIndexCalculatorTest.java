package com.example;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.Test;

public class FogIndexCalculatorTest {

    FogIndexCalculator calculator = new FogIndexCalculator();

    @Test
    public void testCalculateMetrics_basicText() {
        String text = "This is a test. It has two sentences.";
        Map<String, Double> metrics = calculator.calculateMetrics(text);

        assertEquals(2, metrics.get("totalSentences").intValue());
        assertEquals(8, metrics.get("totalWords").intValue());
        assertEquals(1, metrics.get("complexWords").intValue());
    }

    @Test
    public void testCountWords_withWhitespace() {
        assertEquals(5, calculator.countWords("  One two   three\nfour five "));
    }

    @Test
    public void testCountSentences_withPunctuation() {
        assertEquals(3, calculator.countSentences("First sentence. Second! Third?"));
    }

    @Test
    public void testCountComplexWords() {
        String text = "Complicated arrangements usually intensify difficulty.";
        int complexCount = calculator.countComplexWords(text);
        assertEquals(5, complexCount); 
    }


    @Test
    public void testIsTextFile_validExtensions() {
        assertTrue(calculator.isTextFile("file.java"));
        assertTrue(calculator.isTextFile("notes.txt"));
        assertTrue(calculator.isTextFile("index.html"));
        assertFalse(calculator.isTextFile("image.png"));
    }
}
