from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import os

app = Flask(__name__)
CORS(app)

# Load the datasets
popular_data_path = os.path.join(os.path.dirname(__file__), 'popular.pkl')
popular_df = pd.read_pickle(popular_data_path)

books_data_path = os.path.join(os.path.dirname(__file__), 'books.pkl')
pt_data_path = os.path.join(os.path.dirname(__file__), 'pt.pkl')
similarity_data_path = os.path.join(os.path.dirname(__file__), 'similarity_scores.pkl')

books = pd.read_pickle(books_data_path)
pt = pd.read_pickle(pt_data_path)
similarity_scores = pd.read_pickle(similarity_data_path)

# API endpoint to get popular books
@app.route('/api/books', methods=['GET'])
def get_books():
    books = popular_df.to_dict(orient='records')
    return jsonify(books)

# API endpoint for book recommendations
@app.route('/api/recommend_books', methods=['POST'])
def recommend_books():
    data = request.json
    user_input = data.get('user_input')

    # Check if the book exists in the pivot table index
    if user_input not in pt.index:
        return jsonify({"message": "Book not found. Please try another title.", "data": []}), 404

    index = np.where(pt.index == user_input)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:6]

    recommendations = []
    for i in similar_items:
        item = {}
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item['title'] = list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values)[0]
        item['author'] = list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values)[0]
        item['image'] = list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values)[0]
        recommendations.append(item)

    return jsonify({"data": recommendations})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
