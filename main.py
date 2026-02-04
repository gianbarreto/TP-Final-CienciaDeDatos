import json
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

app = FastAPI(
    title="Sistema Recomendador - PeliMovies",
    description="API para recomendación de películas.",
    version="1.0.0"
)

movies_df = None
users_db = []
item_similarity_df = pd.DataFrame()

MOVIES_FILE = 'movies_dataset.csv'
USERS_FILE = 'users.json'

class UserPreferences(BaseModel):
    genres: List[str] = []
    decades: List[int] = []

class UserAttributes(BaseModel):
    preferences: Optional[UserPreferences] = None
    extra: Dict[str, Any] = {} 

class User(BaseModel):
    id: Optional[int] = None
    username: str
    attributes: Optional[UserAttributes] = None

class Item(BaseModel):
    id: int
    name: str
    attributes: Dict[str, Any]

class ItemArray(BaseModel):
    items: List[Item]

def train_model():
    global item_similarity_df
    
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
    
    print(f"Matriz de similitud: {item_similarity_df.shape}")

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

    new_user = user.dict()
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

@app.get("/user/{user_id}/recommend", response_model=ItemArray, tags=["Sistema recomendador"])
def recommend(user_id: int, n: int = 5):
    user = next((u for u in users_db if u['id'] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    history = user.get('history', [])
    
    if not history:
        user_attrs = user.get('attributes', {})
        prefs = {}
        if user_attrs and 'preferences' in user_attrs:
            prefs = user_attrs['preferences']
        elif user_attrs and isinstance(user_attrs, dict):
             prefs = user_attrs.get('preferences', {})
        
        result_df = recommend_cold_start(prefs, n)
        
    else:
        result_df = recommend_collaborative(history, n)

    result_items = []
    for _, row in result_df.iterrows():
        score = row['score'] if 'score' in row else row['vote_average']
        
        item = Item(
            id=row['id'],
            name=row['title'],
            attributes={
                "genres": row['genres'],
                "decade": row['decade'],
                "rating": row['vote_average'],
                "match_score": round(score, 2) # Dato útil para debug
            }
        )
        result_items.append(item)

    return {"items": result_items}