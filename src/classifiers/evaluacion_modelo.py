from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay

def ejecutar_validacion():
    # 1. Cargar datos
    RANDOM_STATE = 42
    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=RANDOM_STATE, stratify=y
    )

    # 2. Pipeline de modelo
    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)
    )

    # 3. Entrenamiento y predicción
    model.fit(X_train, y_train)
    pred = model.predict(X_test)

    # 4. Reporte de métricas
    print(f"--- Resultados de Validación (Iris) ---")
    print(f"Muestras entrenamiento: {len(X_train)}")
    print(f"Muestras prueba: {len(X_test)}")
    print(f"Accuracy: {accuracy_score(y_test, pred):.3f}")
    
    cm = confusion_matrix(y_test, pred)
    print("Matriz de confusión (Numérica):")
    print(cm)
    
    return cm

if __name__ == "__main__":
    ejecutar_validacion()