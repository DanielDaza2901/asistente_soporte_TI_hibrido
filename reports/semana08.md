# Reporte Técnico - Semana 08: Representaciones del Reconocimiento

**Proyecto:** Asistente de Soporte TI Híbrido  
**Integrantes:** Marco Molina Molina & Daniel Eduardo Daza Cuello  
**Institución:** ETITC - 10.º Semestre

## Enlace al Repositorio
[https://github.com/DanielDaza2901/asistente_soporte_TI_hibrido](https://github.com/DanielDaza2901/asistente_soporte_TI_hibrido)

---
# Informe Técnico - Semana 08: Representaciones del Reconocimiento

## 1. ¿Qué reconoce el sistema?
El sistema está diseñado para reconocer, clasifica y diagnosticar incidentes dentro del ecosistema del **Asistente de Soporte TI Híbrido**. Identifica cuatro categorías de fallas operativas (Falla Física de Hardware, Conectividad/Red, Aplicación/Software, y Seguridad). El sistema no solo reconoce patrones en vectores numéricos de telemetría, sino que también reconoce y contextualiza evidencia visual (imágenes) cruzando la sintomatología textual del usuario directamente con los 30 procedimientos estandarizados de la Base de Conocimiento operativa.

## 2. ¿Cómo funciona el modelo?
El proceso de reconocimiento se divide en dos enfoques integrados:
* **Modelo Neuronal (MLP):** Se implementó una Red Neuronal Artificial `MLPClassifier` (Multilayer Perceptron) mediante *scikit-learn*, configurada con capas ocultas `(32, 16)`. El modelo recibe un arreglo numérico con telemetría de red y hardware. Se entrena con un split de 75/25, procesando patrones ocultos para generar una predicción y calculando su métrica de validación (*Accuracy*).
* **Análisis de Evidencia Visual:** El pipeline convierte las imágenes de diagnóstico subidas a una cadena codificada en **Base64**. Posteriormente, extrae el texto de la descripción y lee dinámicamente el archivo físico `data/base_conocimiento.txt` para encontrar un "Match" exacto, determinando el procedimiento a aplicar.

## 3. Información que registra la base de datos (SQLite)
Se diseñó una estructura persistente e histórica en `artifacts/soporte_evidencia.db` que registra la evidencia de forma acumulativa (fila por fila en cada ejecución). La tabla `evidencia_tickets` permite auditar:
* **`id`**: Identificador único autoincremental de la evidencia.
* **`vector_entrada`**: Los datos numéricos exactos analizados por el MLP.
* **`imagen_base64`**: La evidencia visual del error convertida a texto cifrado universal.
* **`descripcion_imagen`**: Los metadatos o síntomas reportados.
* **`diagnostico_imagen`**: El diagnóstico o coincidencia directa (Match) extraída de la Base de Conocimiento.
* **`etiqueta_real` y `prediccion_ia`**: Clases numéricas utilizadas para validar el acierto de la IA.
* **`fecha`**: Timestamp automático del momento de la auditoría.

## 4. Conceptos y relaciones de la ontología (GraphML)
El conocimiento del dominio y el significado del proceso de soporte TI se representaron formalmente en el archivo `artifacts/ontologia.graphml`. Se implementaron **6 conceptos propios** y **7 relaciones semánticas** construidas como frases lógicas:

1. `modelo_mlp` $\rightarrow$ **reconoce patrones en** $\rightarrow$ `ticket_soporte`
2. `ticket_soporte` $\rightarrow$ **representa problema de** $\rightarrow$ `categoria_falla`
3. `modelo_mlp` $\rightarrow$ **produce salida de** $\rightarrow$ `prediccion_ia`
4. `prediccion_ia` $\rightarrow$ **asigna clase a** $\rightarrow$ `categoria_falla`
5. `base_conocimiento_txt` $\rightarrow$ **explica procedimiento de** $\rightarrow$ `categoria_falla`
6. `imagen_diagnostico_ti` $\rightarrow$ **evidencia incidente en** $\rightarrow$ `ticket_soporte`
7. `base_conocimiento_txt` $\rightarrow$ **contextualiza analisis de** $\rightarrow$ `imagen_diagnostico_ti`

## 5. Limitaciones encontradas
* **Dependencia de datos simulados:** Actualmente, el entrenamiento numérico del MLP se basa en matrices generadas con distribuciones aleatorias estructuradas. Para paso a producción, el modelo requiere ser reentrenado con un dataset histórico de telemetría real.
* **Cruce semántico vs. Visión Artificial pura:** El análisis de las imágenes aún depende fuertemente de la descripción textual del usuario para hacer heurística cruzada contra la KB. En fases futuras, se podría implementar una Red Neuronal Convolucional (CNN) orientada estrictamente a la extracción de características de los píxeles de la imagen.
* **Carga en la Interfaz (Frontend):** Las cadenas Base64 son demasiado extensas, por lo que fue necesario limitar visualmente los primeros caracteres en el Dashboard de Streamlit para no colapsar el renderizado del navegador, aunque en SQLite se guardan íntegramente.

## 6. Conclusión de Integración
La integración de la Semana 08 demuestra el flujo completo de la inteligencia artificial aplicada al soporte técnico: **Entrada de Telemetría ➔ Modelo MLP (Predicción) ➔ Base de Evidencia SQLite (Registro persistente) ➔ Ontología GraphML (Significado e interpretación)**[cite: 8]. Esto valida que la predicción de una red neuronal no opera como una "caja negra" aislada, sino que se encuentra debidamente auditada y contextualizada dentro del dominio corporativo del Asistente Híbrido TI.