import pandas as pd
import httpx
import time

API_KEY = "85db02ebd090d9177d6cc59b84e013e7"
BASE_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

# Step 1: Load your original movie dataset
movies = pd.read_pickle("movies_list.pkl")

# Step 2: Prepare filtered list
filtered_movies = []

# Step 3: Loop through movies
for index, row in movies.iterrows():
    movie_id = row["id"]
    title = row["title"]

    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        res = httpx.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()

        poster_path = data.get("poster_path")

        if poster_path:
            print(f"✅ Poster found for: {title}")
            filtered_movies.append(row)
        else:
            print(f"❌ No poster for: {title}")

    except Exception as e:
        print(f"❌ ERROR for {title} (ID: {movie_id}): {e}")

    time.sleep(0.8)  # avoid rate limits

# Step 4: Save new filtered list
filtered_df = pd.DataFrame(filtered_movies)
filtered_df.to_pickle("movies_list_with_posters.pkl")
print("✅ Done! Saved filtered dataset with posters.")
