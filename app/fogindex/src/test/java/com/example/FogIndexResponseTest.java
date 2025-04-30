package com.example;

import java.util.Date;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import org.junit.jupiter.api.Test;

public class FogIndexResponseTest {

    @Test
    public void testFogIndexResponse() {
        Date timestamp = new Date();
        List<Map<String, Object>> data = List.of(Map.of("key", "value"));

        FogIndexResponse response = new FogIndexResponse(timestamp, data);

        assertEquals(timestamp, response.getTimestamp());
        assertEquals(data, response.getData());

        Date newTimestamp = new Date();
        response.setTimestamp(newTimestamp);
        assertEquals(newTimestamp, response.getTimestamp());

        List<Map<String, Object>> newData = List.of(Map.of("newKey", "newValue"));
        response.setData(newData);
        assertEquals(newData, response.getData());
    }
}
