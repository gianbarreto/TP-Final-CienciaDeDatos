import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics.pairwise import cosine_similarity

# 1. Carga de datos
try:
    with open('users.json', 'r', encoding='utf-8') as f:
        users_db = json.load(f)
    movies_df = pd.read_csv('movies_dataset.csv')
except FileNotFoundError:
    print("Error: Asegurate de tener users.json y movies_dataset.csv en esta carpeta.")
    exit()

# 2. Preparación de la Matriz de Interacciones
interactions = []
for user in users_db:
    for rec in user.get('history', []):
        interactions.append((user['id'], rec['item_id'], rec['rating']))

df_inter = pd.DataFrame(interactions, columns=['user_id', 'item_id', 'rating'])
user_item_matrix = df_inter.pivot_table(index='user_id', columns='item_id', values='rating').fillna(0)
item_user_matrix = user_item_matrix.T

# 3. Cálculo de Similitud
sim_matrix = cosine_similarity(item_user_matrix)
sim_df = pd.DataFrame(sim_matrix, index=item_user_matrix.index, columns=item_user_matrix.index)

# --- GRÁFICO 1: Heatmap de Evaluación ---
plt.figure(figsize=(10, 8))
# Seleccionamos las primeras 12 películas para que el gráfico sea legible
subset_ids = item_user_matrix.index[:12] 
titles = movies_df.set_index('id')['title'].to_dict()
labels = [titles.get(i, f"ID:{i}") for i in subset_ids]

sns.heatmap(sim_df.loc[subset_ids, subset_ids], annot=True, cmap='RdPu', xticklabels=labels, yticklabels=labels)
plt.title('Gráfico 1: Matriz de Similitud entre Ítems (Aprendizaje del Modelo)')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('grafico_heatmap.png')
plt.show()

# --- GRÁFICO 2: Distribución de Scores Predichos (Y estimada) ---
def predict_affinity_all():
    all_scores = []
    for u in users_db:
        history = u.get('history', [])
        if not history: continue
        
        user_ratings = {item['item_id']: item['rating'] for item in history}
        watched = list(user_ratings.keys())
        
        for item_id in sim_df.index:
            if item_id in watched: continue
            
            sims = sim_df.loc[item_id, watched]
            rats = [user_ratings[w] for w in watched]
            
            if sims.sum() > 0:
                score = np.dot(sims, rats) / sims.sum()
                all_scores.append(score)
    return all_scores

scores = predict_affinity_all()

plt.figure(figsize=(9, 6))
sns.histplot(scores, bins=15, kde=True, color='purple')
plt.axvline(np.mean(scores), color='red', linestyle='--', label=f'Media: {np.mean(scores):.2f}')
plt.title('Gráfico 2: Distribución de Puntajes de Afinidad Predichos (Y Estimada)')
plt.xlabel('Puntaje de Afinidad Estimado (1-5)')
plt.ylabel('Cantidad de Recomendaciones')
plt.legend()
plt.tight_layout()
plt.savefig('grafico_distribucion.png')
plt.show()