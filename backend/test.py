from flask import Flask, jsonify, request
from flask_cors import CORS
import pickle
import numpy as np
import os
popular_df = pickle.load(open('D:/website/book-recommender/backend/books.pkl', 'rb'))
print(popular_df.columns)