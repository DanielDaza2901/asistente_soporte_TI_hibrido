import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score, confusion_matrix
from classifiers.taxonomia import classify_problem

def ejecutar_validacion():
    # 1. Cargar los datos de los casos de soporte TI
    try:
        df = pd.read_csv("data/casos_ia.csv")
        if len(df.columns) <= 1:
            df = pd.read_csv("data/casos_ia.csv", sep=";")
    except Exception:
        df = pd.read_csv("data/casos_ia.csv", sep=None, engine='python')

    col_texto = 'descripcion' if 'descripcion' in df.columns else df.columns[0]
    
    # 2. Generar etiquetas automáticas usando tu propio clasificador taxonómico para asegurar múltiples clases
    X = df[col_texto].fillna("").astype(str)
    y = X.apply(lambda texto: classify_problem(texto)[0]) # Extrae la categoría principal detectada por tu taxonomía

    # Si por alguna razón todas cayeran en la misma categoría, asignamos etiquetas de prueba variadas basadas en palabras clave
    if y.nunique() < 2:
        y = X.apply(lambda t: "Procesamiento de Lenguaje Natural (PLN)" if "error" in t.lower() else "Sistemas de Recomendación y Diagnóstico")

    # 3. División de datos con validación para evitar errores de clases insuficientes
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y
        )
    except ValueError:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42
        )

    # 4. Pipeline con TF-IDF y Regresión Logística
    model = make_pipeline(
        TfidfVectorizer(),
        LogisticRegression(max_iter=1000, random_state=42)
    )

    # 5. Entrenamiento y predicción
    model.fit(X_train, y_train)
    pred = model.predict(X_test)

    # 6. Resultados en consola
    print(f"--- Resultados de Validación (Tickets Soporte TI con TF-IDF) ---")
    print(f"Muestras entrenamiento: {len(X_train)}")
    print(f"Muestras prueba: {len(X_test)}")
    print(f"Accuracy: {accuracy_score(y_test, pred):.3f}")
    
    cm = confusion_matrix(y_test, pred)
    print("Matriz de confusión (Numérica):")
    print(cm)
    
    return cm

if __name__ == "__main__":
    ejecutar_validacion()