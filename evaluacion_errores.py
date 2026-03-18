import main
import numpy as np
import pandas as pd

def evaluar_mae_rmse():
    print("Iniciando evaluación MAE y RMSE...")
    main.startup_event()
    
    errores_abs_warm, errores_cuad_warm = [], []
    errores_abs_cold, errores_cuad_cold = [], []
    
    for user in main.users_db:
        history = user.get('history', [])
        prefs = user.get('attributes', {}).get('preferences', {})
        
        # --- WARM START ---
        if len(history) >= 5:
            corte = int(len(history) * 0.8)
            train_history = history[:corte]
            test_history = history[corte:]
            
            try:
                # Pedimos predecir todo el catálogo para buscar las ocultas
                df_recs = main.recommend_collaborative(train_history, n=100)
                for item in test_history:
                    item_id = item['item_id']
                    rating_real = item['rating']
                    
                    fila = df_recs[df_recs['id'] == item_id]
                    if not fila.empty:
                        rating_predicho = fila.iloc[0]['score']
                        # Solo evaluamos si hubo predicción válida (>0)
                        if rating_predicho > 0:
                            errores_abs_warm.append(abs(rating_real - rating_predicho))
                            errores_cuad_warm.append((rating_real - rating_predicho)**2)
            except Exception as e:
                pass

        # --- COLD START ---
        if prefs and len(history) > 0:
            try:
                df_recs_cold = main.recommend_cold_start(prefs, n=100)
                for item in history: # Comparamos contra todo el historial real
                    item_id = item['item_id']
                    rating_real = item['rating']
                    
                    fila = df_recs_cold[df_recs_cold['id'] == item_id]
                    if not fila.empty:
                        score_bruto = fila.iloc[0]['score']
                        # Normalizamos el score bruto (que puede ser 25) a escala 1-5 aprox.
                        rating_predicho = (score_bruto / 25.0) * 4 + 1 
                        
                        errores_abs_cold.append(abs(rating_real - rating_predicho))
                        errores_cuad_cold.append((rating_real - rating_predicho)**2)
            except Exception as e:
                pass

    # Cálculos Finales
    mae_warm = np.mean(errores_abs_warm) if errores_abs_warm else 0
    rmse_warm = np.sqrt(np.mean(errores_cuad_warm)) if errores_cuad_warm else 0
    
    mae_cold = np.mean(errores_abs_cold) if errores_abs_cold else 0
    rmse_cold = np.sqrt(np.mean(errores_cuad_cold)) if errores_cuad_cold else 0
    
    print("\n" + "="*40)
    print(" RESULTADOS WARM START (Colaborativo)")
    print("="*40)
    print(f"MAE:  {mae_warm:.2f}")
    print(f"RMSE: {rmse_warm:.2f}")
    
    print("\n" + "="*40)
    print(" RESULTADOS COLD START (Contenido)")
    print("="*40)
    print(f"MAE:  {mae_cold:.2f}")
    print(f"RMSE: {rmse_cold:.2f}")
    print("="*40)

if __name__ == '__main__':
    evaluar_mae_rmse()