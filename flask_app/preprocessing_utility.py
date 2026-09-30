import numpy as np
import pandas as pd
import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
nltk.download('stopwords')
nltk.download('wordnet')

STOP_WORDS = set(stopwords.words("english"))
LEMMATIZER = WordNetLemmatizer()

def preprocess_text(text):
    if not isinstance(text, str):
        return ""

    words = text.lower().split()
    words = [
        LEMMATIZER.lemmatize(re.sub(r'\d+', '', word))
        for word in words if word not in STOP_WORDS
    ]

    cleaned_text = ' '.join(words)
    cleaned_text = re.sub(f"[{re.escape(string.punctuation)}]", " ", cleaned_text)
    cleaned_text = re.sub(r"https?://\S+|www\.\S+", "", cleaned_text)
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()

    return cleaned_text

def remove_small_sentences(df, column='text', min_words=3):
    return df[df[column].apply(lambda x: len(str(x).split()) >= min_words)].reset_index(drop=True)
