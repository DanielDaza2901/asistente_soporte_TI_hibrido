import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix

def ejecutar_validacion():
    """
    Ejecuta la validación del modelo base de clasificación multiclase (Semana 02).
    Utiliza el dataset Iris como benchmark estándar reproducible del curso:
    - 150 muestras totales con split 75/25 estratificado (112 entrenamiento / 38 prueba).
    - Pipeline: StandardScaler + LogisticRegression(max_iter=1000).
    - Accuracy esperado: 0.921 (92.1%).
    - Retorna la matriz de confusión 3x3 de las clases evaluadas.
    """
    # 1. Carga las 150 muestras del dataset Iris divididas en características (X) y etiquetas (y).
    X, y = load_iris(return_X_y=True)

    # 2. Divide el dataset en 75% entrenamiento (112) y 25% prueba (38), manteniendo la proporción de clases.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    # 3. Normaliza las características (media 0, varianza 1) calculando parámetros con train y aplicándolos a test.
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 4. Instancia y entrena el modelo de Regresión Logística multiclase sobre los datos escalados.
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train_scaled, y_train)

    # 5. Genera predicciones con el conjunto de prueba y calcula el accuracy global y la matriz de confusión.
    pred = model.predict(X_test_scaled)
    acc = accuracy_score(y_test, pred)
    cm = confusion_matrix(y_test, pred)

    # 6. Imprime los resultados de rendimiento y métricas clave formateados en consola.
    print("--- Resultados de Validación del Modelo Base (Semana 02) ---")
    print(f"Muestras entrenamiento: {len(X_train)}")
    print(f"Muestras prueba:        {len(X_test)}")
    print(f"Accuracy Global:        {acc:.3f} ({acc*100:.1f}%)")
    print("Matriz de confusión (Numérica):")
    print(cm)

    # 7. Devuelve la matriz de confusión 3x3 para ser consumida por otros módulos (ej. el Dashboard).
    return cm

# 8. Punto de entrada principal: ejecuta la función de validación al correr el archivo directamente.
if __name__ == "__main__":
    ejecutar_validacion()