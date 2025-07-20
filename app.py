import streamlit as st
import pickle
import pandas as pd
import aiohttp
import asyncio
from dotenv import load_dotenv
import os


load_dotenv()
api_key = os.getenv("TMDB_API_KEY")

movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))



async def fetch_single_poster(session, movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}'
    try:
        async with session.get(url) as response:
            data = await response.json()
            poster_path = data.get('poster_path')
            if poster_path:
                return "https://image.tmdb.org/t/p/w500/" + poster_path
            else:
                return "https://via.placeholder.com/500x750.png?text=No+Poster"
    except:
        return "https://via.placeholder.com/500x750.png?text=Error"

async def fetch_all_posters(movie_ids):
    async with aiohttp.ClientSession(headers={"User-Agent": "Mozilla/5.0"}) as session:
        tasks = [fetch_single_poster(session, mid) for mid in movie_ids]
        return await asyncio.gather(*tasks)

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = [movies.iloc[i[0]].title for i in movies_list]
    movie_ids = [movies.iloc[i[0]].id for i in movies_list]

    # Run the async poster fetch
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    recommended_movies_poster = loop.run_until_complete(fetch_all_posters(movie_ids))

    return recommended_movies, recommended_movies_poster


st.title('Movie Recommender System')

selected_movie_name = st.selectbox(
    'Select a movie',
    movies['title'].values
)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.text(names[0])
        st.image(posters[0])

    with col2:
        st.text(names[1])
        st.image(posters[1])

    with col3:
        st.text(names[2])
        st.image(posters[2])

    with col4:
        st.text(names[3])
        st.image(posters[3])

    with col5:
        st.text(names[4])
        st.image(posters[4])