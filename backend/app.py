from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd

app = Flask(__name__, static_folder='../frontend/build', static_url_path='')
CORS(app)

# Load the dataset
data = pd.read_pickle('popular.pkl')

# API endpoint to get book data
@app.route('/api/books', methods=['GET'])
def get_books():
    books = data.to_dict(orient='records')
    return jsonify(books)

# Serve the React frontend
@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
