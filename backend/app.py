from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# Load the dataset using an absolute path
data_path = os.path.join(os.path.dirname(__file__), 'popular.pkl')
data = pd.read_pickle(data_path)

@app.route('/api/books', methods=['GET'])
def get_books():
    books = data.to_dict(orient='records')
    return jsonify(books)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
