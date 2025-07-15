import streamlit as st
import pickle
import httpx
import time

API_KEY = "85db02ebd090d9177d6cc59b84e013e7"
BASE_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

# ---- Fetch poster with retry and logs ----
def fetch_poster(movie_id, title=""):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    for attempt in range(3):  # Retry 3 times
        try:
            print(f"➡️ [Attempt {attempt+1}] Fetching poster for: {title} (ID: {movie_id})")
            response = httpx.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            poster_path = data.get("poster_path")
            if poster_path:
                poster_url = BASE_IMAGE_URL + poster_path
                print(f"✅ Poster: {poster_url}")
                return poster_url
            else:
                print(f"⚠️ No poster found for: {title} (ID: {movie_id})")
                return "https://via.placeholder.com/300x450?text=No+Poster"
        except Exception as e:
            print(f"❌ ERROR for {title} (ID: {movie_id}): {e}")
            time.sleep(1.5)  # Wait before retry
    return "https://via.placeholder.com/300x450?text=Error"

# ---- Load data ----
movies = pickle.load(open("movies_list.pkl", "rb"))
  # Requires 'title' and 'id'
similarity = pickle.load(open("similarity.pkl", "rb"))
movie_titles = movies["title"].values

# ---- Streamlit UI ----
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title("🎬 Movie Recommender System")

selected_movie = st.selectbox("Select a movie you like:", movie_titles)

# ---- Recommendation logic ----
def recommend(movie_title):
    index = movies[movies["title"] == movie_title].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended = []
    for i in distances[1:4]:  # Limit to 3 posters to avoid overload
        movie_id = movies.iloc[i[0]].id
        title = str(movies.iloc[i[0]].title)
        time.sleep(1.2)  # Respect TMDb rate limit
        poster = fetch_poster(movie_id, title)
        recommended.append((title, poster))

    return recommended

# ---- Show recommendations ----
if st.button("Show Recommendations"):
    results = recommend(selected_movie)
    st.subheader("Recommended for you:")

    cols = st.columns(len(results))
    for i, (title, poster_url) in enumerate(results):
        with cols[i]:
            st.image(poster_url, use_container_width=True)
            st.caption(title if title else "Unknown Title")  