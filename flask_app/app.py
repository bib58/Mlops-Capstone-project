from flask import Flask, render_template, request
import mlflow
from mlflow.exceptions import MlflowException
import pickle
import os
import pandas as pd
from prometheus_client import Counter, Histogram, generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST
import time
import numpy as np
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import string
import re
import dagshub
import warnings
warnings.simplefilter("ignore", UserWarning)
warnings.filterwarnings("ignore")

def lemmatization(text):
    lemmatizer = WordNetLemmatizer()
    text = text.split()
    text = [lemmatizer.lemmatize(word) for word in text]
    return " ".join(text)

def remove_stop_words(text):
    stop_words = set(stopwords.words("english"))
    text = [word for word in str(text).split() if word not in stop_words]
    return " ".join(text)

def removing_numbers(text):
    text = ''.join([char for char in text if not char.isdigit()])
    return text

def lower_case(text):
    text = text.split()
    text = [word.lower() for word in text]
    return " ".join(text)

def removing_punctuations(text):
    text = re.sub('[%s]' % re.escape(string.punctuation), ' ', text)
    text = text.replace('؛', "")
    text = re.sub('\s+', ' ', text).strip()
    return text

def removing_urls(text):
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    return url_pattern.sub(r'', text)

def remove_small_sentences(df):
    for i in range(len(df)):
        if len(df.text.iloc[i].split()) < 3:
            df.text.iloc[i] = np.nan

def normalize_text(text):
    text = lower_case(text)
    text = remove_stop_words(text)
    text = removing_numbers(text)
    text = removing_punctuations(text)
    text = removing_urls(text)
    text = lemmatization(text)

    return text

mlflow.set_tracking_uri('https://dagshub.com/bibhukumarsingh355/Mlops-Capstone-project.mlflow')

app = Flask(__name__)
registry = CollectorRegistry()

REQUEST_COUNT = Counter("app_request_count", "Total number of requests to the app", ["method", "endpoint"], registry=registry)
REQUEST_LATENCY = Histogram("app_request_latency_seconds", "Latency of requests in seconds", ["endpoint"], registry=registry)
PREDICTION_COUNT = Counter("model_prediction_count", "Count of predictions for each class", ["prediction"], registry=registry)


model_name = "my_model"

# model serving
def get_latest_model_version(model_name):
    client = mlflow.MlflowClient()
    try:
        return client.get_model_version_by_alias(model_name, "production").version
    except MlflowException:
        pass

    try:
        return client.get_model_version_by_alias(model_name, "staging").version
    except MlflowException:
        pass

    latest_version = client.get_latest_versions(model_name, stages=["Production"])
    if not latest_version:
        latest_version = client.get_latest_versions(model_name, stages=["Staging"])
    if not latest_version:
        latest_version = client.get_latest_versions(model_name, stages=["None"])
    return latest_version[0].version if latest_version else None

model = None
vectorizer = None


def load_registered_model():
    dagshub.init(repo_owner='bibhukumarsingh355', repo_name='Mlops-Capstone-project', mlflow=True)
    model_version = get_latest_model_version(model_name)
    if model_version is None:
        raise RuntimeError(
            f"No registered version found for '{model_name}'. Run model registration first."
        )
    model_uri = f'models:/{model_name}/{model_version}'
    print(f"Fetching model from: {model_uri}")
    return mlflow.pyfunc.load_model(model_uri)


def get_model():
    global model
    if model is None:
        model = load_registered_model()
    return model


def load_vectorizer():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    vectorizer_path = os.path.join(project_root, 'models', 'vectorizer.pkl')
    with open(vectorizer_path, 'rb') as vectorizer_file:
        return pickle.load(vectorizer_file)


def get_vectorizer():
    global vectorizer
    if vectorizer is None:
        vectorizer = load_vectorizer()
    return vectorizer


@app.route("/")
def home():
    REQUEST_COUNT.labels(method="GET", endpoint="/").inc()
    start_time = time.time()
    response = render_template("index.html", result=None)
    REQUEST_LATENCY.labels(endpoint="/").observe(time.time() - start_time)
    return response

@app.route("/predict", methods=["POST"])
def predict():
    REQUEST_COUNT.labels(method="POST", endpoint="/predict").inc()
    start_time = time.time()

    text = request.form["text"]
    text = normalize_text(text)
    features = get_vectorizer().transform([text])
    features_df = pd.DataFrame(features.toarray(), columns=[str(i) for i in range(features.shape[1])])

    result = get_model().predict(features_df)
    prediction = result[0]

    PREDICTION_COUNT.labels(prediction=str(prediction)).inc()
    REQUEST_LATENCY.labels(endpoint="/predict").observe(time.time() - start_time)

    return render_template("index.html", result=prediction)

@app.route("/metrics", methods=["GET"])
def metrics():
    return generate_latest(registry), 200, {"Content-Type": CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
