import unittest
from unittest.mock import patch
import flask_app.app as app_module


class FakeModel:
    def predict(self, features):
        return [1]


class FakeFeatures:
    shape = (1, 1)

    def toarray(self):
        return [[0]]


class FakeVectorizer:
    def transform(self, texts):
        return FakeFeatures()


class FlaskAppTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app_module.app.test_client()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<title>Sentiment Analysis</title>', response.data)

    def test_predict_page(self):
        with (
            patch.object(app_module, "load_registered_model", return_value=FakeModel()),
            patch.object(app_module, "load_vectorizer", return_value=FakeVectorizer()),
            patch.object(app_module, "normalize_text", side_effect=lambda text: text),
        ):
            response = self.client.post('/predict', data=dict(text="I loved this movie, this was amazing!"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            b'Positive' in response.data or b'Negative' in response.data,
            "Response should contain either 'Positive' or 'Negative'"
        )

if __name__ == '__main__':
    unittest.main()
