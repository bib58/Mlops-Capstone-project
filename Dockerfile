FROM python:3.10-slim

WORKDIR /app

COPY flask_app/requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY flask_app/ /app/

RUN python -m nltk.downloader stopwords wordnet

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "app:app"]