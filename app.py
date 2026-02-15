from flask import Flask, render_template, request
import pickle
import requests
import pandas as pd

app = Flask(__name__)

API_KEY = "268a784867e227e32b824626b91c7bad"

movies, cosine_sim = pickle.load(open("movie_data.pkl", "rb"))

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {
        "api_key": API_KEY,
        "language": "en-US"
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        poster_path = data.get("poster_path")

        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
        else:
            return "https://via.placeholder.com/300x450?text=No+Image"

    except:
        return "https://via.placeholder.com/300x450?text=No+Image"


def recommend(movie):
    recommended_movies = []
    recommended_posters = []

    idx = movies[movies['title'] == movie].index[0]
    distances = cosine_sim[idx]
    movie_list = sorted(list(enumerate(distances)), key=lambda x: x[1], reverse=True)[1:11]

    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        title = movies.iloc[i[0]].title

        recommended_movies.append(title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_posters


@app.route('/', methods=['GET', 'POST'])
def index():
    movie_list = movies['title'].values

    if request.method == 'POST':
        selected_movie = request.form.get('movie')
        names, posters = recommend(selected_movie)

        return render_template(
            'index.html',
            movies=movie_list,
            selected_movie=selected_movie,
            names=names,
            posters=posters
        )

    return render_template(
        'index.html',
        movies=movie_list,
        selected_movie=None,
        names=None,
        posters=None
    )


if __name__ == '__main__':
    app.run(debug=True)