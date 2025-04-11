import os
import json
import pytest
from app import app, links_file

@pytest.fixture
def client():
    # Setup
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
    # Teardown
    if os.path.exists('benchmarks.json'):
        os.remove('benchmarks.json')
    if os.path.exists(links_file):
        os.remove(links_file)

def test_get_links_empty(client):
    response = client.get('/links.json')
    assert response.status_code == 200
    assert response.is_json
    assert response.json == []

def test_save_links_invalid_format(client):
    response = client.post('/save-links', json={"url": "https://example.com"})
    assert response.status_code == 400
    assert response.json['error'] == "Invalid data format, expected a list"

def test_save_and_get_links(client):
    test_data = [{"url": "https://example.com"}]
    post_response = client.post('/save-links', json=test_data)
    assert post_response.status_code == 200
    assert post_response.json['message'] == "Links saved successfully!"

    get_response = client.get('/links.json')
    assert get_response.status_code == 200
    assert get_response.json == test_data

# def test_save_benchmark_invalid_data(client):
#     response = client.post('/save-benchmark', json={})
#     assert response.status_code == 400
#     assert response.json['error'] == "Invalid data"

def test_save_and_get_benchmarks(client):
    test_entry = {
        "repoUrl": "https://github.com/mrunal2148/rca-app",
        "metric": "Code Coverage",
        "history": [{"date": "2024-01-01", "value": 85}]
    }

    post_response = client.post('/save-benchmark', json=test_entry)
    assert post_response.status_code == 200
    assert post_response.json['message'] == "Benchmark saved successfully!"

    get_response = client.get('/benchmarks.json')
    assert get_response.status_code == 200
    benchmarks = get_response.json
    assert isinstance(benchmarks, list)
    assert benchmarks[0]["repoUrl"] == test_entry["repoUrl"]
    assert benchmarks[0]["metric"] == test_entry["metric"]
    assert benchmarks[0]["history"][0] == test_entry["history"][0]

def test_append_benchmark_history(client):
    entry1 = {
        "repoUrl": "https://github.com/mrunal2148/rca-app",
        "metric": "Code Coverage",
        "history": [{"date": "2024-01-01", "value": 85}]
    }
    entry2 = {
        "repoUrl": "https://github.com/mrunal2148/rca-app",
        "metric": "Code Coverage",
        "history": [{"date": "2024-02-01", "value": 90}]
    }

    client.post('/save-benchmark', json=entry1)
    client.post('/save-benchmark', json=entry2)

    response = client.get('/benchmarks.json')
    assert response.status_code == 200
    history = response.json[0]["history"]
    assert len(history) == 2
    assert history[1] == entry2["history"][0]
