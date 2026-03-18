# Sistema Recomendador - Trabajo Final Integrador - Ciencia de Datos - UTN FRCU

Este proyecto implementa un sistema de recomendaciones híbrido diseñado bajo la metodología CRISP-DM. El objetivo principal es optimizar las ventas de una plataforma con un catálogo estático de 100 películas, reemplazando la selección aleatoria por sugerencias personalizadas.

## Integrantes
Arlettaz, Joaquin.   
Barreto, Gian Marco.   

## Descripción

El sistema busca resolver dos escenarios clave del negocio:

1.  **Usuarios Nuevos (Cold Start):** Se utiliza un enfoque **Basado en Contenido**. Al no existir historial de transacciones, el sistema utiliza preferencias explícitas (Géneros y Décadas) declaradas por el usuario al registrarse para calcular un puntaje de afinidad.
2.  **Usuarios Recurrentes:** Se utiliza **Filtrado Colaborativo Basado en Ítems**. Se analiza el historial de compras para encontrar patrones ocultos y recomendar ítems similares a los ya adquiridos, utilizando la **Similitud del Coseno** sobre una matriz de interacciones.

## Tecnologías Utilizadas

* **Lenguaje:** Python 3.10+
* **API Framework:** FastAPI (Uvicorn).
* **Procesamiento de Datos:** Panda, Numpy.
* **Machine Learning:** Scikit-learn (Cálculo de matrices de similitud y distancia del coseno).
* **Persistencia:** JSON y CSV (Simulación de base de datos NoSQL y catálogo estático).

## Instalación y Configuración

Seguir estos pasos para ejecutar el proyecto en tu entorno local:

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/gianbarreto/TP-Final-CienciaDeDatos.git
    cd Tp-Final-CienciaDeDatos
    ```

2.  **Crear y activar entorno virtual:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # Para Linux/Mac, En Windows se realiza via: .venv\Scripts\activate
    ```

3.  **Instalar dependencias:**
    ```bash
    pip install fastapi "uvicorn[standard]" pandas scikit-learn numpy
    ```

## Generación de Datos

Dado que no hay una base de datos preexistente, la generamos:

1.  **Generar Catálogo de Películas:**
    ```bash
    python data_gen.py
    ```
    Crea el archivo `movies_dataset.csv` con 100 ítems, incluyendo atributos como género, década y keywords.

2.  **Generar Usuarios:**
    ```bash
    python users_gen.py
    ```
    Crea el archivo `users.json` con 20 usuarios iniciales, sus preferencias y transacciones pasadas.

## Ejecución de la API

Una vez generados los datos, iniciar el servidor de desarrollo:

```bash
uvicorn main:app --reload
```

Una vez corriendo la API, se ingresa por este enlace: http://127.0.0.1:8000/docs

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
