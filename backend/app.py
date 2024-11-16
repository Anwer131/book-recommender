from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
import pandas as pd
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow Cross-Origin requests

# Load the datasets
popular_df = pd.read_pickle('popular.pkl')
pt = pd.read_pickle('pt.pkl')
books = pd.read_pickle('books.pkl')
similarity_scores = pd.read_pickle('similarity_scores.pkl')

# API endpoint to fetch popular books
@app.route('/popular-books', methods=['GET'])
def get_best_books():
    """Returns a list of popular books"""
    try:
        print("Fetching popular books...")
        data = popular_df.to_dict(orient='records')
        return jsonify(data)
    except KeyError as e:
        print(f"KeyError: {e}")
        return jsonify({"error": f"Column {e} not found in DataFrame"}), 500
    except Exception as e:
        print(f"Error fetching books: {e}")
        return jsonify({"error": "Failed to fetch books"}), 500
@app.route('/search-books', methods=['GET'])
def search_books():
    """Search for books by title or author with pagination and filtering"""
    query = request.args.get('query', '').lower()
    limit = int(request.args.get('limit', 20))  # Number of results to return (default is 20)
    offset = int(request.args.get('offset', 0))  # Offset for pagination (default is 0)

    # Check if the query is provided
    if not query:
        return jsonify({"error": "Please provide a search query"}), 400

    # Filter books based on the query
    filtered_books = books[
        (books['Book-Title'].str.contains(query, case=False, na=False) |
         books['Book-Author'].str.contains(query, case=False, na=False))
        & (books['Num-Rating'] > 50)
    ]

    # Sort the filtered books by 'Avg-Rating' in descending order
    sorted_books = filtered_books.sort_values(by='Avg-Rating', ascending=False)

    # Paginate the results
    total_results = len(sorted_books)
    paginated_books = sorted_books.iloc[offset:offset + limit][['Book-Title', 'Book-Author', 'Image-URL-M', 'Avg-Rating', 'Num-Rating']]

    # Convert the filtered and paginated results to a list of dictionaries
    results = paginated_books.to_dict(orient='records')

    # Return the results as JSON, along with total results count
    return jsonify({
        "data": results,
        "total": total_results,
        "limit": limit,
        "offset": offset
    })

# API endpoint to get book recommendations
@app.route('/recommend-books',methods=['post'])
def recommend():
    """Get book recommendations based on user input"""
    try:
        data = request.json
        user_input = data.get('user_input')
        print(f"User input: {user_input}")

        # Check if the book exists in the pivot table
        if user_input not in pt.index:
            return jsonify({"message": "Book not found. Please try another title."}), 404

        index = np.where(pt.index == user_input)[0][0]
        similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:6]

        recommendations = []
        for i in similar_items:
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            book_info = {
                "Book-Title": list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values)[0],
                "Book-Author": list(temp_df.drop_duplicates('Book-Author')['Book-Author'].values)[0],
                "Image-URL-M": list(temp_df.drop_duplicates('Image-URL-M')['Image-URL-M'].values)[0],
            }
            recommendations.append(book_info)

        return jsonify({"data": recommendations})
    except Exception as e:
        print(f"Error during recommendation: {e}")
        return jsonify({"error": "Failed to get recommendations"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
