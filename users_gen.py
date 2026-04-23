import pandas as pd
import json
import random
import os

NUM_USERS = 20

# Usamos rutas absolutas para no tener problemas de directorios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(BASE_DIR, 'users.json')
MOVIES_FILE = os.path.join(BASE_DIR, 'movies_dataset.csv')

random.seed(42)  # Seed fijado para reproducibilidad

# 1. Definimos "Arquetipos" para curar la base de datos
ARCHETYPES = {
    "Nerd_SciFi_Action": {
        "genres": ["Action", "Sci-Fi", "Adventure"],
        "decades": [1980, 1990, 2010, 2020]
    },
    "Drama_Romance_Lover": {
        "genres": ["Drama", "Romance", "Biography"],
        "decades": [1990, 2000, 2010]
    },
    "Family_Animation_Parent": {
        "genres": ["Animation", "Family", "Comedy"],
        "decades": [1990, 2000, 2010, 2020]
    },
    "Horror_Thriller_Fan": {
        "genres": ["Horror", "Thriller", "Mystery", "Crime"],
        "decades": [1970, 1980, 1990, 2010]
    }
}

def get_movies_for_archetype(df, archetype):
    # Filtra películas que tengan al menos un género del arquetipo
    mask = df['genres'].apply(lambda x: any(g in x for g in archetype['genres']))
    return df[mask]['id'].tolist()

def generate_users():
    try:
        df_movies = pd.read_csv(MOVIES_FILE)
        all_movie_ids = df_movies['id'].tolist()
        
        # Pre-calcular las "bolsas" de películas para cada arquetipo
        archetype_movie_pools = {
            name: get_movies_for_archetype(df_movies, arch)
            for name, arch in ARCHETYPES.items()
        }

        users_db = []

        for i in range(1, NUM_USERS + 1):
            user_id = 100 + i
            username = f"user_{i}"
            
            # Asignar un arquetipo al azar al usuario
            arch_name = random.choice(list(ARCHETYPES.keys()))
            arch_data = ARCHETYPES[arch_name]
            
            # Setear preferencias (tomamos un par de su arquetipo)
            fav_genres = random.sample(arch_data["genres"], k=min(2, len(arch_data["genres"])))
            fav_decades = random.sample(arch_data["decades"], k=min(2, len(arch_data["decades"])))

            attributes = {
                "preferences": {
                    "genres": fav_genres,
                    "decades": fav_decades
                },
                "archetype": arch_name # Lo guardamos oculto acá para ver si el modelo funciona bien luego
            }

            # Historial sesgado (Cura de datos)
            num_purchases = random.randint(6, 12)
            pool_arch = archetype_movie_pools[arch_name]
            pool_others = list(set(all_movie_ids) - set(pool_arch))
            
            history = []
            purchased_ids = set()
            
            for _ in range(num_purchases):
                # 80% de chance de comprar algo de su estilo
                if random.random() < 0.8 and pool_arch:
                    movie_id = random.choice(pool_arch)
                    # Le gusta, así que le pone nota alta
                    rating = random.choices([4, 5], weights=[40, 60])[0]
                else:
                    # 20% de ruido/exploración
                    movie_id = random.choice(pool_others)
                    # No es su estilo favorito, nota más baja
                    rating = random.choices([1, 2, 3], weights=[30, 40, 30])[0]
                
                # Evitar duplicados
                if movie_id not in purchased_ids:
                    purchased_ids.add(movie_id)
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
            
        print(f"Generados {len(users_db)} usuarios CURADOS por arquetipos en '{OUTPUT_FILE}'.")

    except FileNotFoundError:
        print(f"Error: No se encontró '{MOVIES_FILE}'.")

if __name__ == "__main__":
    generate_users()