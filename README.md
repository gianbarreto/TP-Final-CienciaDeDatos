# Sistema Recomendador - Trabajo Final Integrador

Este repositorio contiene la implementación de un sistema recomendador de películas desarrollado bajo la metodología **CRISP-DM**.

## Descripción del Trabajo

El sistema busca resolver dos escenarios clave del negocio:

1.  **Usuarios Nuevos (Cold Start):** Se utiliza un enfoque **Basado en Conocimiento/Contenido**. Al no existir historial de transacciones, el sistema utiliza preferencias explícitas (Géneros y Décadas) declaradas por el usuario al registrarse para calcular un puntaje de afinidad.
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

Una vez generados los datos, inicia el servidor de desarrollo:

```bash
uvicorn main:app --reload