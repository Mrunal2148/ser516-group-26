package com.example;

import java.util.Date;
import java.util.List;
import java.util.Map;

public class FogIndexResponse {
    private Date timestamp;
    private List<Map<String, Object>> data;

    public FogIndexResponse() {}

    public FogIndexResponse(Date timestamp, List<Map<String, Object>> data) {
        this.timestamp = timestamp;
        this.data = data;
    }

    public Date getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(Date timestamp) {
        this.timestamp = timestamp;
    }

    public List<Map<String, Object>> getData() {
        return data;
    }

    public void setData(List<Map<String, Object>> data) {
        this.data = data;
    }
}