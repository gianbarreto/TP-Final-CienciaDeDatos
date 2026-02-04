import pandas as pd
import json
import random

NUM_USERS = 20
OUTPUT_FILE = 'users.json'
MOVIES_FILE = 'movies_dataset.csv'

random.seed(42)  # Seed fijado

def generate_users():
    try:
        df_movies = pd.read_csv(MOVIES_FILE)
        
        all_movie_ids = df_movies['id'].tolist()
        
        all_genres = set()
        for g_str in df_movies['genres']:
            for g in g_str.split('|'):
                all_genres.add(g)
        all_genres = list(all_genres)
        
        all_decades = sorted(df_movies['decade'].unique().tolist())

        users_db = []

        for i in range(1, NUM_USERS + 1):
            user_id = 100 + i # IDs de usuario arrancan en 101
            username = f"user_{i}"
            
            fav_genres = random.sample(all_genres, k=random.randint(1, 3))
            fav_decades = random.sample(all_decades, k=random.randint(1, 2))
            fav_decades = [int(d) for d in fav_decades] 

            attributes = {
                "preferences": {
                    "genres": fav_genres,
                    "decades": fav_decades
                }
            }

            num_purchases = random.randint(5, 10)
            
            purchased_ids = random.sample(all_movie_ids, k=num_purchases)
            
            history = []
            for movie_id in purchased_ids:
                rating = random.choices([1, 2, 3, 4, 5], weights=[5, 10, 20, 35, 30])[0]
                
                history.append({
                    "item_id": int(movie_id),
                    "rating": rating
                })

            user_obj = {
                "id": user_id,
                "username": username,
                "attributes": attributes,
                "history": history
            }
            
            users_db.append(user_obj)

        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_db, f, indent=4)
            
        print(f"Generados {len(users_db)} usuarios en '{OUTPUT_FILE}'.")

    except FileNotFoundError:
        print(f"Error: No se encontró '{MOVIES_FILE}'. Ejecuta primero data_gen.py")

if __name__ == "__main__":
    generate_users()