import pandas as pd
import json
import matplotlib.pyplot as plt

# 1. Cargar Datos
df_movies = pd.read_csv('movies_dataset.csv')
with open('users.json', 'r') as f:
    users = json.load(f)

# --- GRÁFICO 1: DISTRIBUCIÓN DE GÉNEROS ---
plt.figure(figsize=(10, 6))
generos = df_movies['genres'].str.split('|', expand=True).stack().value_counts().head(10)
generos.plot(kind='bar', color='skyblue')
plt.title('Top 10 Géneros en el Catálogo (Fase II)')
plt.ylabel('Cantidad de Películas')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('distribucion_generos.png') # Se guarda como archivo
print("Archivo 'distribucion_generos.png' generado.")

# --- GRÁFICO 2: HISTORIAL DE COMPRAS ---
plt.figure(figsize=(10, 6))
compras = [len(u['history']) for u in users]
plt.hist(compras, bins=range(min(compras), max(compras) + 2), color='salmon', edgecolor='black', align='left')
plt.title('Distribución de Compras por Usuario (Validación de Negocio)')
plt.xlabel('Número de Artículos Comprados')
plt.ylabel('Cantidad de Usuarios')
plt.axvline(7.7, color='red', linestyle='dashed', linewidth=2, label=f'Promedio: 7.7')
plt.legend()
plt.savefig('comportamiento_usuarios.png') # Se guarda como archivo
print("Archivo 'comportamiento_usuarios.png' generado.")


# --- GRÁFICO 3: DISTRIBUCIÓN DE RATINGS DEL CATÁLOGO ---
plt.figure(figsize=(10, 6))
plt.hist(df_movies['vote_average'], bins=10, color='mediumseagreen', edgecolor='black')
plt.title('Distribución de Ratings en el Catálogo (Fase II)')
plt.xlabel('Rating (Promedio de Votos)')
plt.ylabel('Cantidad de Películas')

# Marcamos el promedio que ya calculamos
promedio_rating = df_movies['vote_average'].mean()
plt.axvline(promedio_rating, color='red', linestyle='dashed', linewidth=2, label=f'Promedio: {promedio_rating:.2f}')

plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('distribucion_ratings.png')
print("Archivo 'distribucion_ratings.png' generado.")