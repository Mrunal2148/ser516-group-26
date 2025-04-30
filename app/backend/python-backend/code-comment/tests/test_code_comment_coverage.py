import unittest
import os
import shutil
import json
from flask import json
from code_comment_app import app, save_to_json, get_code_files, process_file, calculate_comment_coverage
import tempfile
import sys

# Add utilities to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))


class TestApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_repo_url = "https://github.com/Mrunal2148/rca-app"
        cls.test_repo_path = tempfile.mkdtemp()
        cls.coverage_data_file = "coverage_data.json"
        
        # Create a test client
        app.config['TESTING'] = True
        cls.client = app.test_client()
        
        # Backup existing coverage data if it exists
        if os.path.exists(cls.coverage_data_file):
            shutil.copy(cls.coverage_data_file, cls.coverage_data_file + ".bak")

    @classmethod
    def tearDownClass(cls):
        # Restore original coverage data
        if os.path.exists(cls.coverage_data_file + ".bak"):
            shutil.move(cls.coverage_data_file + ".bak", cls.coverage_data_file)
        
        # Clean up test repo directory
        if os.path.exists(cls.test_repo_path):
            shutil.rmtree(cls.test_repo_path)

    def setUp(self):
        # Clear coverage data before each test
        if os.path.exists(self.coverage_data_file):
            os.remove(self.coverage_data_file)

    def test_analyze_no_repo_url(self):
        """Test /analyze endpoint with no repository URL."""
        response = self.client.post('/analyze', json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn('GitHub repository URL is required', response.json['error'])

    def test_analyze_valid_repo(self):
        """Test /analyze endpoint with valid GitHub repository URL."""
        data = {"repo_url": self.test_repo_url}
        response = self.client.post('/analyze', json=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('coverage', response.json)
        self.assertIsInstance(response.json['coverage'], (float, int))

    def test_analyze_invalid_repo(self):
        """Test /analyze endpoint with invalid repository URL."""
        data = {"repo_url": "https://github.com/invalid/repo"}
        response = self.client.post('/analyze', json=data)
        self.assertEqual(response.status_code, 500)

    def test_get_coverage_data_empty(self):
        """Test /get_coverage_data endpoint with no coverage data."""
        response = self.client.get('/get_coverage_data')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertEqual(len(response.json), 0)

    def test_get_coverage_data_with_data(self):
        """Test /get_coverage_data endpoint with existing coverage data."""
        # First add some test data
        test_data = {
            "repo_url": self.test_repo_url,
            "total_lines": 1000,
            "comment_lines": 500,
            "coverage": 50.0
        }
        save_to_json(**test_data)
        
        # Then test the endpoint
        response = self.client.get('/get_coverage_data')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        self.assertGreater(len(response.json), 0)
        self.assertEqual(response.json[0]["repo_url"], self.test_repo_url)

    def test_get_code_files(self):
        """Test the get_code_files function."""
        # Create a temporary directory with some test files
        test_dir = tempfile.mkdtemp()
        try:
            # Create some test files
            with open(os.path.join(test_dir, "test.py"), "w") as f:
                f.write("# Test file\nprint('Hello')")
            with open(os.path.join(test_dir, "README.md"), "w") as f:
                f.write("# Readme")
                
            # Test the function
            files = get_code_files(test_dir)
            self.assertIsInstance(files, list)
            self.assertEqual(len(files), 1)  # Should only return .py file
            self.assertTrue(files[0].endswith(".py"))
        finally:
            shutil.rmtree(test_dir)

    def test_process_file(self):
        """Test the process_file function."""
        # Create a temporary test file
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as f:
            file_path = f.name
            f.write("# This is a comment\nprint('Hello')\n# Another comment\n")
        
        try:
            total_lines, comment_lines = process_file(file_path)
            self.assertIsInstance(total_lines, int)
            self.assertIsInstance(comment_lines, int)
            self.assertEqual(total_lines, 3)
            self.assertEqual(comment_lines, 2)
        finally:
            os.unlink(file_path)

    def test_calculate_comment_coverage(self):
        """Test the calculate_comment_coverage function."""
        # Create temporary test files
        files = []
        try:
            for i in range(2):
                fd, path = tempfile.mkstemp(suffix='.py')
                with os.fdopen(fd, 'w') as f:
                    f.write("# Comment\n" * (i+1) + "print('Hello')\n" * (i+1))
                files.append(path)
            
            total_lines, comment_lines, coverage = calculate_comment_coverage(files)
            
            self.assertIsInstance(total_lines, int)
            self.assertIsInstance(comment_lines, int)
            self.assertIsInstance(coverage, float)
            self.assertGreaterEqual(coverage, 0)
            self.assertLessEqual(coverage, 100)
        finally:
            for path in files:
                os.unlink(path)


if __name__ == "__main__":
    unittest.main()
