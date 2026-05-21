import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns #  seaborn para el heatmap

# 1. Cargar Datos
df_movies = pd.read_csv('movies_dataset.csv')
with open('users.json', 'r') as f:
    users = json.load(f)

# --- GRÁFICO DISTRIBUCIÓN DE GÉNEROS ---
plt.figure(figsize=(10, 6))
generos = df_movies['genres'].str.split('|', expand=True).stack().value_counts().head(10)
generos.plot(kind='bar', color='skyblue')
plt.title('Top 10 Géneros en el Catálogo (Fase II)')
plt.ylabel('Cantidad de Películas')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('distribucion_generos.png') # Se guarda como archivo
print("Archivo 'distribucion_generos.png' generado.")

# --- GRÁFICO HISTORIAL DE COMPRAS ---
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


# --- GRÁFICO MAPA DE CALOR DE ARQUETIPOS VS GÉNEROS ---

# 1. Armamos un diccionario para mapear rápido el ID de peli con sus géneros
movie_genres = df_movies.set_index('id')['genres'].str.split('|').to_dict()

# 2. Aplanamos los datos para poder cruzarlos
records = []
for u in users:
    arquetipo = u['attributes'].get('archetype', 'Desconocido')
    for interaccion in u['history']:
        movie_id = interaccion['item_id']
        rating = interaccion['rating']
        
        # Por cada género que tenga la película, sumamos un registro
        generos = movie_genres.get(movie_id, [])
        for g in generos:
            records.append({'Arquetipo': arquetipo, 'Genero': g, 'Rating': rating})

df_interacciones = pd.DataFrame(records)

# 3. Filtramos solo los géneros principales para que el gráfico no quede gigante
top_generos = ["Action", "Sci-Fi", "Drama", "Romance", "Animation", "Family", "Horror", "Thriller"]
df_filtrado = df_interacciones[df_interacciones['Genero'].isin(top_generos)]

# 4. Creamos la matriz pivot: Filas=Arquetipos, Columnas=Géneros, Valores=Promedio de Rating
matriz_calor = df_filtrado.pivot_table(index='Arquetipo', columns='Genero', values='Rating', aggfunc='mean')

# 5. Dibujamos
plt.figure(figsize=(10, 6))
sns.heatmap(matriz_calor, annot=True, cmap='coolwarm', vmin=1, vmax=5, fmt=".1f", linewidths=.5)
plt.title('Validación de Simulación: Promedio de Calificaciones por Arquetipo')
plt.xlabel('Género de la Película')
plt.ylabel('Arquetipo del Usuario')
plt.tight_layout()
plt.savefig('heatmap_arquetipos.png')
print("Archivo 'heatmap_arquetipos.png' generado.")