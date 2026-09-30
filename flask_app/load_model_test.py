import pickle
import os

pkl_file_path = '../models/vectorizer.pkl'

if os.path.exists(pkl_file_path):
    print(f"File found: {pkl_file_path}")
    try:
        vectorizer = pickle.load(open(pkl_file_path, 'rb'))
        print("File loaded successfully.")
    except Exception as e:
        print(f"Error loading the .pkl file: {e}")
else:
    print(f"File not found: {pkl_file_path}. Please check the path and try again.")
