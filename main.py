import json
import pandas as pd
import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# --- MODELOS DE DATOS (ESTRICTOS) ---

class UserPreferences(BaseModel):
    # Obligamos a que la lista exista y tenga al menos 1 elemento
    genres: List[str] = Field(..., min_length=1, description="Debe ingresar al menos un género")
    decades: List[int] = Field(..., min_length=1, description="Debe ingresar al menos una década")

class UserAttributes(BaseModel):
    preferences: UserPreferences 
    extra: Dict[str, Any] = {} 

class User(BaseModel):
    id: Optional[int] = None # Opcional para que el backend lo asigne
    username: str
    attributes: UserAttributes

class Item(BaseModel):
    id: int
    name: str
    attributes: Dict[str, Any]

class ItemArray(BaseModel):
    items: List[Item]

class RatingCreate(BaseModel):
    item_id: int
    rating: float = Field(..., ge=1, le=5, description="El rating debe estar entre 1 y 5")


# --- CONFIGURACIÓN DE LA API ---

app = FastAPI(
    title="Sistema Recomendador - PeliMovies",
    description="API para recomendación de películas.",
    version="1.0.0"
)

movies_df = None
users_db = []
item_similarity_df = pd.DataFrame()

# Rutas de archivos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MOVIES_FILE = os.path.join(BASE_DIR, 'movies_dataset.csv')
USERS_FILE = os.path.join(BASE_DIR, 'users.json')

# Variables de optimización
new_interactions_count = 0
TRAIN_THRESHOLD = 5  # Parametro, luego de 5 iteraciones, recalcula


# --- LÓGICA DEL RECOMENDADOR ---

def train_model():
    global item_similarity_df
    print("Iniciando reentrenamiento de la matriz de similitud...")
    
    interactions = []
    for user in users_db:
        if 'history' in user:
            for record in user['history']:
                interactions.append({
                    'user_id': user['id'],
                    'item_id': record['item_id'],
                    'rating': record['rating']
                })
    
    if not interactions:
        print("No hay interacciones suficientes.")
        return

    df_interactions = pd.DataFrame(interactions)
    
    user_item_matrix = df_interactions.pivot_table(
        index='user_id', 
        columns='item_id', 
        values='rating'
    ).fillna(0)
    
    item_user_matrix = user_item_matrix.T 
    
    similarity_matrix = cosine_similarity(item_user_matrix)
    
    item_similarity_df = pd.DataFrame(
        similarity_matrix, 
        index=item_user_matrix.index, 
        columns=item_user_matrix.index
    )
    
    print(f"Matriz de similitud actualizada: {item_similarity_df.shape}")

def recommend_cold_start(user_prefs: dict, n: int) -> pd.DataFrame:
    candidates = movies_df.copy()
    candidates['score'] = candidates['vote_average']
    
    fav_genres = user_prefs.get('genres', [])
    fav_decades = user_prefs.get('decades', [])
    
    if fav_genres:
        def check_genre_match(movie_genres_list):
            return not set(movie_genres_list).isdisjoint(fav_genres)
        mask_genre = candidates['genres_list'].apply(check_genre_match)
        candidates.loc[mask_genre, 'score'] += 10

    if fav_decades:
        mask_decade = candidates['decade'].isin(fav_decades)
        candidates.loc[mask_decade, 'score'] += 5

    return candidates.sort_values(by='score', ascending=False).head(n)

def recommend_collaborative(history: List[dict], n: int) -> pd.DataFrame:
    global item_similarity_df
    
    if item_similarity_df.empty:
        return movies_df.sort_values(by='vote_average', ascending=False).head(n)

    user_ratings = {item['item_id']: item['rating'] for item in history}
    watched_ids = list(user_ratings.keys())
    
    valid_items = [i for i in item_similarity_df.index if i not in watched_ids]
    
    scores = {}
    
    for candidate_id in valid_items:
        relevant_watched = [wid for wid in watched_ids if wid in item_similarity_df.index]
        
        if not relevant_watched:
            continue
            
        similarities = item_similarity_df.loc[candidate_id, relevant_watched]
        ratings = [user_ratings[wid] for wid in relevant_watched]
        
        numerator = np.dot(similarities, ratings)
        denominator = similarities.sum()
        
        if denominator > 0:
            predicted_score = numerator / denominator
        else:
            predicted_score = 0
            
        scores[candidate_id] = predicted_score
        
    if not scores:
         return movies_df[~movies_df['id'].isin(watched_ids)].sort_values(by='vote_average', ascending=False).head(n)

    recommendations = pd.DataFrame(list(scores.items()), columns=['id', 'score'])
    recommendations = recommendations.merge(movies_df, on='id')
    
    return recommendations.sort_values(by='score', ascending=False).head(n)


# --- EVENTOS Y ENDPOINTS ---

@app.on_event("startup")
def startup_event():
    global movies_df, users_db
    try:
        movies_df = pd.read_csv(MOVIES_FILE)
        movies_df['genres_list'] = movies_df['genres'].apply(lambda x: x.split('|'))
        print(f"Catálogo cargado: {len(movies_df)} películas.")
    except Exception as e:
        print(f"Error cargando películas: {e}")

    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            users_db = json.load(f)
        print(f"Base de usuarios cargada: {len(users_db)} usuarios.")
    except Exception as e:
        print(f"No se encontró {USERS_FILE}, iniciando base vacía.")
        users_db = []
        
    train_model()

@app.get("/")
def read_root():
    return {"status": "API Online", "model_strategy": "Hybrid (Content + Collaborative)"}

@app.post("/user", response_model=User, tags=["Sistema recomendador"])
def create_user(user: User):
    global users_db
    if user.id is not None:
        if any(u['id'] == user.id for u in users_db):
            raise HTTPException(status_code=400, detail="ID duplicado")
    else:
        user.id = (max([u['id'] for u in users_db]) if users_db else 0) + 1

    new_user = user.model_dump() if hasattr(user, 'model_dump') else user.dict()
    new_user['history'] = []
    users_db.append(new_user)
    
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_db, f, indent=4)
        
    return new_user

@app.get("/user/{user_id}", tags=["Sistema recomendador"])
def get_user(user_id: int):
    user = next((u for u in users_db if u['id'] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/user/{user_id}/rating", tags=["Sistema recomendador"])
def add_rating(user_id: int, rating_data: RatingCreate, background_tasks: BackgroundTasks):
    global users_db, new_interactions_count

    user = next((u for u in users_db if u['id'] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if rating_data.item_id not in movies_df['id'].values:
        raise HTTPException(status_code=404, detail="La película no existe en el catálogo")

    history = user.get('history', [])
    existing_rating = next((item for item in history if item['item_id'] == rating_data.item_id), None)
    
    if existing_rating:
        existing_rating['rating'] = rating_data.rating
    else:
        history.append({"item_id": rating_data.item_id, "rating": rating_data.rating})
        user['history'] = history

    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_db, f, indent=4)

    new_interactions_count += 1
    if new_interactions_count >= TRAIN_THRESHOLD:
        background_tasks.add_task(train_model)
        new_interactions_count = 0  

    return {"message": "Rating guardado exitosamente", "current_interactions_pending": new_interactions_count}

@app.get("/user/{user_id}/recommend", response_model=ItemArray, tags=["Sistema recomendador"])
def recommend(user_id: int, n: int = 5):
    user = next((u for u in users_db if u['id'] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    history = user.get('history', [])
    
    n_model = n - 1 if n > 1 else n

    if not history:
        user_attrs = user.get('attributes', {})
        prefs = {}
        if user_attrs and 'preferences' in user_attrs:
            prefs = user_attrs['preferences']
        elif user_attrs and isinstance(user_attrs, dict):
             prefs = user_attrs.get('preferences', {})
        
        result_df = recommend_cold_start(prefs, n_model)
    else:
        result_df = recommend_collaborative(history, n_model)

    result_df['is_serendipity'] = False 

    if n > 1:
        watched_ids = [item['item_id'] for item in history] if history else []
        recommended_ids = result_df['id'].tolist()
        exclusion_list = set(watched_ids + recommended_ids)

        available_randoms = movies_df[~movies_df['id'].isin(exclusion_list)].copy()
        
        if not available_randoms.empty:
            random_item = available_randoms.sample(n=1)
            random_item['is_serendipity'] = True 
            result_df = pd.concat([result_df, random_item])

    result_items = []
    for _, row in result_df.iterrows():
        score = row['score'] if 'score' in row else row['vote_average']
        is_serend = (row['is_serendipity'] == True)
        
        item = Item(
            id=row['id'],
            name=row['title'],
            attributes={
                "genres": row['genres'],
                "decade": row['decade'],
                "rating": row['vote_average'],
                "match_score": "Aleatorio" if is_serend else round(score, 2),
                "serendipity": is_serend
            }
        )
        result_items.append(item)

    return {"items": result_items}