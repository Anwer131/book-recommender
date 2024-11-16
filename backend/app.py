from flask import Flask, jsonify, request
from flask_cors import CORS
import pickle
import numpy as np
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow Cross-Origin requests

# Load the datasets
popular_df = pickle.load(open('popular.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(open('books.pkl', 'rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl', 'rb'))

# API endpoint to fetch popular books
@app.route('/api/books', methods=['GET'])
def get_books():
    """Returns a list of popular books"""
    data = {
        "book_name": list(popular_df['Book-Title'].values),
        "author": list(popular_df['Book-Author'].values),
        "image": list(popular_df['Image-URL-M'].values),
        "votes": list(popular_df['num_ratings'].values),
        "rating": list(popular_df['avg_rating'].values)
    }
    return jsonify(data)

# API endpoint to get book recommendations
@app.route('/api/recommend_books', methods=['POST'])
def recommend_books():
    """Returns book recommendations based on user input"""
    data = request.json
    user_input = data.get('user_input')

    # Check if the book exists in the pivot table index
    if user_input not in pt.index:
        return jsonify({"message": "Book not found. Please try another title.", "data": []}), 404

    # Get the index of the input book
    index = np.where(pt.index == user_input)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:6]

    # Prepare recommendation data
    recommendations = []
    for i in similar_items:
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        book_info = {
            "title": list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values)[0],
            "author": list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values)[0],
            "image": list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values)[0]
        }
        recommendations.append(book_info)

    return jsonify({"data": recommendations})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
