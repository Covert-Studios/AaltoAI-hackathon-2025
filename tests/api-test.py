import unittest
from api import app  # Import the Flask app from api.py

class TestAPI(unittest.TestCase):
    def setUp(self):
        # Set up the test client
        self.app = app.test_client()
        self.app.testing = True
        self.api_key = "prohackerschmacker6969"  # Correct API key
        self.headers = {"x-api-key": self.api_key}

    def test_date_endpoint_with_key(self):
        response = self.app.get('/date', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('date', response.json)

    def test_date_endpoint_without_key(self):
        response = self.app.get('/date')
        self.assertEqual(response.status_code, 401)
        self.assertIn('Unauthorized', response.json['message'])

    def test_cal_endpoint_with_key(self):
        response = self.app.get('/cal', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('calendar', response.json)

    def test_cal_endpoint_without_key(self):
        response = self.app.get('/cal')
        self.assertEqual(response.status_code, 401)
        self.assertIn('Unauthorized', response.json['message'])

    def test_docker_endpoint_with_key(self):
        response = self.app.get('/docker', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn('docker', response.json)

    def test_docker_endpoint_without_key(self):
        response = self.app.get('/docker')
        self.assertEqual(response.status_code, 401)
        self.assertIn('Unauthorized', response.json['message'])

    def test_cls_endpoint_with_key(self):
        response = self.app.get('/cls', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        # Since 'cls' is not a valid command on macOS/Linux, this might fail.
        # Adjust the test based on the expected behavior of the /cls endpoint.

    def test_cls_endpoint_without_key(self):
        response = self.app.get('/cls')
        self.assertEqual(response.status_code, 401)
        self.assertIn('Unauthorized', response.json['message'])

if __name__ == '__main__':
    unittest.main()