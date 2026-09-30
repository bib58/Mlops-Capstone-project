import unittest
from types import SimpleNamespace
from unittest.mock import patch


class FakeModel:
    def predict(self, features):
        return [1]

class FlaskAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch("dagshub.init"), patch("mlflow.MlflowClient") as mlflow_client, patch(
            "mlflow.pyfunc.load_model", return_value=FakeModel()
        ):
            mlflow_client.return_value.get_model_version_by_alias.return_value = (
                SimpleNamespace(version="test")
            )
            from flask_app.app import app

        cls.app = app
        cls.client = app.test_client()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<title>Sentiment Analysis</title>', response.data)

    def test_predict_page(self):
        with patch("flask_app.app.normalize_text", side_effect=lambda text: text):
            response = self.client.post('/predict', data=dict(text="I loved this movie, this was amazing!"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            b'Positive' in response.data or b'Negative' in response.data,
            "Response should contain either 'Positive' or 'Negative'"
        )

if __name__ == '__main__':
    unittest.main()
