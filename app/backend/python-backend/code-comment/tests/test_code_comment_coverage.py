import unittest
import os
import shutil
from flask import json
from code_comment_app import app, save_to_json, clone_repo, get_code_files, process_file, calculate_comment_coverage


class TestApp(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_analyze_no_repo_url(self):
        print('Test - 1 : Test the /analyze endpoint with no repository URL.')
        response = self.client.post('/analyze', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn('GitHub repository URL is required', response.json['error'])

    def test_analyze_valid_repo(self):
        print('Test - 2 :Test the /analyze endpoint with a valid GitHub repository URL.')
        data = {"repo_url": "https://github.com/Mrunal2148/rca-app"}
        response = self.client.post('/analyze', json=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('coverage', response.json)

    def test_analyze_invalid_repo(self):
        print('Test - 3 : Test the /analyze endpoint with an invalid repository URL.')
        data = {"repo_url": "https://github.com/invalid/repo"}
        response = self.client.post('/analyze', json=data)
        self.assertEqual(response.status_code, 500)

    def test_get_coverage_data_empty(self):
        print('Test - 4 : Test the /get_coverage_data endpoint with no coverage data.')
        response = self.client.get('/get_coverage_data')
        
        #print(f"Response Data: {response.json}")  

        self.assertTrue(isinstance(response.json, list))

        self.assertGreater(len(response.json), 0)  

    def test_get_coverage_data_with_data(self):
        print('Test - 5 : Test the /get_coverage_data endpoint with existing coverage data.')
        save_to_json("https://github.com/Mrunal2148/rca-app", 1000, 500, 50.0)
        response = self.client.get('/get_coverage_data')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json) > 0)

    def test_clone_repo(self):
        print('Test - 6 : Test the clone_repo function.')
        repo_url = "https://github.com/Mrunal2148/rca-app"
        repo_path = "/tmp/test_repo"
        try:
            clone_repo(repo_url, repo_path)
            self.assertTrue(os.path.exists(repo_path))
        finally:
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path)

    def test_get_code_files(self):
        print('Test - 7 : Test the get_code_files function.')
        repo_path = "/tmp/test_repo"
        files = get_code_files(repo_path)
        self.assertTrue(isinstance(files, list))

    def test_process_file(self):
        print('Test - 8 : Test the process_file function.')
        file_path = "../code_comment_app.py"
        total_lines, comment_lines = process_file(file_path)
        self.assertTrue(isinstance(total_lines, int))
        self.assertTrue(isinstance(comment_lines, int))


    def test_calculate_comment_coverage(self):
        print('Test - 9 : Test the calculate_comment_coverage function.')
        files = ["../code_comment_app.py"]
        total_lines, comment_lines, coverage = calculate_comment_coverage(files)

        self.assertTrue(isinstance(total_lines, int))
        self.assertTrue(isinstance(comment_lines, int))
        self.assertTrue(isinstance(coverage, (float, int)))

        coverage = float(coverage)  

        self.assertTrue(isinstance(coverage, float))



    def test_save_to_json(self):
        print('Test - 10 : Test the save_to_json function.')
        save_to_json("https://github.com/Mrunal2148/rca-app", 1000, 500, 50.0)
        with open("coverage_data.json", "r") as file:
            data = json.load(file)
            self.assertTrue(len(data) > 0)

if __name__ == "__main__":
    unittest.main()
