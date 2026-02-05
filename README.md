# Sistema Recomendador - Trabajo Final Integrador

Este repositorio contiene la implementación de un sistema recomendador de películas.

## Descripción

El sistema busca resolver dos escenarios clave del negocio:

1.  **Usuarios Nuevos (Cold Start):** Se utiliza un enfoque **Basado en Contenido**. Al no existir historial de transacciones, el sistema utiliza preferencias explícitas (Géneros y Décadas) declaradas por el usuario al registrarse para calcular un puntaje de afinidad.
2.  **Usuarios Recurrentes:** Se utiliza **Filtrado Colaborativo Basado en Ítems**. Se analiza el historial de compras para encontrar patrones ocultos y recomendar ítems similares a los ya adquiridos, utilizando la **Similitud del Coseno** sobre una matriz de interacciones.

## Tecnologías Utilizadas

* **Lenguaje:** Python 3.10+
* **API Framework:** FastAPI (Uvicorn).
* **Procesamiento de Datos:** Pandas (Manipulación de DataFrames).
* **Machine Learning:** Scikit-learn (Cálculo de matrices de similitud y distancia del coseno).
* **Persistencia:** JSON y CSV (Simulación de base de datos NoSQL y catálogo estático).

## Instalación y Configuración

Seguir estos pasos para ejecutar el proyecto en tu entorno local:

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/gianbarreto/TP-Final-CienciaDeDatos.git
    cd tp-ciencia-datos
    ```

2.  **Crear y activar entorno virtual:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # En Windows: .venv\Scripts\activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install fastapi "uvicorn[standard]" pandas scikit-learn numpy
    ```

## Generación de Datos

Dado que no hay una base de datos preexistente, la generamos:

1.  **Generar Catálogo de Películas:**
    Crea el archivo `movies_dataset.csv` con 100 ítems, incluyendo atributos como género, década y keywords.
    ```bash
    python data_gen.py
    ```

2.  **Generar Usuarios:**
    Crea el archivo `users.json` con 20 usuarios iniciales, sus preferencias y transacciones pasadas.
    ```bash
    python users_gen.py
    ```

## Ejecución de la API

Una vez generados los datos, iniciar el servidor de desarrollo:

```bash
uvicorn main:app --reload
```

## Guía de Prueba

**Prueba 1: Usuario Nuevo**

En el Endpoint POST /user copiar y pegar este JSON:

```bash
{
  "username": "user_test",
  "attributes": {
    "preferences": {
      "genres": ["Sci-Fi"],
      "decades": [1980]
    }
  }
}
```

Para verificar las recomendaciones para este nuevo usuario, usamos el Endpoint GET /user/{user_id}/recommend (Reemplazar {user_id} con el ID que se recibió al crear el nuevo usuario).

**Prueba 2: Usuario Recurrente**

En el Endpoint GET /user/{user_id}/recommend podemos usar cualquier user_id desde 101 a 120, debido a que son los usuarios ya precargados que tienen un historial de transacciones.
