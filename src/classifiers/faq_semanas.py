"""
Preguntas frecuentes del Asistente de Soporte TI Híbrido (Semana 02 a Semana 14).

El asistente recupera la pregunta más parecida a la consulta del usuario con el mismo
enfoque de la Semana 05: vectores TF-IDF y similitud coseno. Se combinan dos canales:
palabras (con raíz simplificada) y n-gramas de caracteres, que toleran plurales,
tildes y pequeñas variaciones de escritura.
"""
import math
import re
import unicodedata
from collections import Counter

# Semana -> (tema, página del dashboard donde se ve). La semana 0 agrupa lo general.
SEMANAS = {
    0: ("General", "Resumen Ejecutivo"),
    2: ("Validación, priorización y auditoría", "Matriz de Confusión"),
    3: ("Clasificador taxonómico de tickets", "Resumen Ejecutivo"),
    4: ("Planificación A* y Minimax", "Planificador A* & Minimax"),
    5: ("Sistema híbrido Reglas + TF-IDF", "Sistema Híbrido & TF-IDF"),
    7: ("Representaciones del reconocimiento", "Representaciones del Reconocimiento"),
    8: ("Red neuronal, Base64, SQLite y ontología", "Red Neuronal & Ontología"),
    9: ("Visión artificial", "Visión Artificial (Semana 09)"),
    10: ("Histogramas y texturas LBP", "Histogramas y Texturas LBP (Semana 10)"),
    11: ("Benchmark y decisiones de modelos", "Benchmark y Decisiones de Modelos (Semana 11)"),
    13: ("Motor de inferencia lógica", "Motor de Inferencia (Semana 13)"),
    14: ("Redes semánticas", "Redes Semánticas (Semana 14)"),
}


def _f(id_, semana, pregunta, respuesta, claves, ref):
    return {"id": id_, "semana": semana, "tema": SEMANAS[semana][0], "pregunta": pregunta,
            "respuesta": respuesta, "claves": claves, "ref": ref}


FAQ_SEMANAS = [
    # ------------------------------------------------------------------ General
    _f("G-1", 0, "¿Qué hace el Asistente de Soporte TI Híbrido?",
       "Es un sistema de soporte técnico que automatiza la clasificación de consultas, recupera conocimiento técnico, aplica reglas de negocio y prioriza incidentes con trazabilidad completa. Combina machine learning, visión artificial y razonamiento simbólico en un pipeline modular que va de la Semana 02 a la 14.",
       "proyecto objetivo asistente soporte ti hibrido que hace descripcion general automatizar clasificar priorizar", "src/main.py"),
    _f("G-2", 0, "¿Cómo instalo y ejecuto el proyecto?",
       "Instala las dependencias con `pip install scikit-learn==1.5.0` y `pip install -r requirements.txt` (se recomienda un entorno virtual `.venv`). Luego, desde la raíz: `python src/main.py` ejecuta el pipeline completo, `streamlit run dashboard.py` abre este panel y `python -m unittest discover -s tests -v` corre las pruebas (con `PYTHONPATH=src`).",
       "instalar ejecutar correr iniciar comando dependencias requirements pip venv arrancar proyecto dashboard streamlit pruebas", "README.md · src/main.py"),
    _f("G-3", 0, "¿Dónde se guardan los resultados y las evidencias?",
       "En `artifacts/`: `audit.log`, `modelo_mlp.pkl`, `mejor_modelo.pkl`, `benchmark.csv`, `soporte_evidencia.db`, `ontologia.graphml` y `semana09_vision.png`. Los informes en Markdown se generan en `reports/` (`semana03.md`, `semana05.md` y `semana11_adr.md`). Se crean al ejecutar el pipeline.",
       "artifacts artefactos archivos guardan resultados salidas carpeta generados reports informes", "artifacts/ · reports/"),
    _f("G-4", 0, "¿Qué es el registro de auditoría audit.log?",
       "Cada acción del orquestador se escribe con `registrar_traza(ticket_id, accion, detalles)` en `artifacts/audit.log`, usando el módulo `logging` de Python, con marca de tiempo, nivel y el mensaje `TICKET_ID | ACCIÓN | DETALLES`. También se imprime en consola. La página Trazas de Auditoría lo lee y lo muestra.",
       "auditoria traza log registro trazabilidad registrar_traza eventos logging", "audit/logger_audit.py"),
    _f("G-5", 0, "¿Qué significa que el sistema sea híbrido?",
       "Que mezcla enfoques distintos en lugar de depender de uno solo: reglas expertas, TF-IDF con similitud coseno, modelos de machine learning y razonamiento simbólico.",
       "hibrido hibrida combina mezcla enfoques tecnicas", "classifiers/sistema_hibrido.py"),
    _f("G-6", 0, "¿Qué tecnologías usa el proyecto?",
       "Python 3.13+, Streamlit para el dashboard, Plotly para los gráficos interactivos, scikit-learn (TF-IDF y modelos de machine learning), Pandas y NumPy para el procesamiento, y Pydantic para validar la estructura de los tickets.",
       "tecnologias stack herramientas librerias python streamlit plotly scikit-learn pandas numpy pydantic", "requirements.txt"),
    _f("G-7", 0, "¿Cómo está organizado el repositorio?",
       "`src/` contiene el código (`audit/`, `classifiers/`, `knowledge/`, `rules/` y `main.py`), `data/` la base de conocimiento, `artifacts/` las evidencias generadas, `reports/` los informes, `tests/` las pruebas y, en la raíz, `dashboard.py`, `requirements.txt` y `README.md`.",
       "estructura repositorio carpetas organizacion archivos directorios proyecto src data tests", "README.md"),
    _f("G-8", 0, "¿Quiénes desarrollaron el proyecto?",
       "Marco Molina Molina y Daniel Eduardo Daza Cuello, estudiantes de 10º semestre de la Escuela Tecnológica Instituto Técnico Central (ETITC).",
       "autores desarrolladores estudiantes equipo integrantes institucion etitc", "README.md"),
    # ---------------------------------------------------------------- Semana 02
    _f("S02-1", 2, "¿Qué es la matriz de confusión y qué muestra?",
       "Es una tabla que cruza la clase real con la clase predicha: la diagonal son los aciertos y lo demás son errores. En el proyecto muestra 35 aciertos de 38 muestras de prueba.",
       "matriz confusion aciertos errores real predicha tabla", "classifiers/evaluacion_modelo.py"),
    _f("S02-2", 2, "¿Qué modelo y qué datos se usaron para validar?",
       "Un pipeline con StandardScaler y LogisticRegression (`max_iter=1000`) sobre el dataset Iris (150 muestras, 3 clases: Setosa, Versicolor y Virginica), con división estratificada 75/25 y `random_state=42`: 112 muestras de entrenamiento y 38 de prueba.",
       "modelo base regresion logistica datos iris dataset entrenamiento prueba muestras 150 112 38 random_state", "classifiers/evaluacion_modelo.py"),
    _f("S02-3", 2, "¿Cuál es el accuracy y la tasa de error del modelo base?",
       "92.1% (0.921) de accuracy global y 7.9% de error, es decir 3 errores en 38 muestras, concentrados en casos límite entre clases contiguas.",
       "accuracy precision exactitud tasa error porcentaje 92.1 resultado", "classifiers/evaluacion_modelo.py"),
    _f("S02-4", 2, "¿Por qué se usa una división estratificada?",
       "Para que las proporciones de cada clase sean las mismas en entrenamiento y en prueba. Así la evaluación es más justa y reproducible.",
       "estratificada division train test split proporciones clases reproducible", "classifiers/evaluacion_modelo.py"),
    _f("S02-5", 2, "¿Por qué se estandarizan los datos con StandardScaler?",
       "La regresión logística es sensible a la escala de las variables. El código ajusta StandardScaler solo con los datos de entrenamiento (`fit_transform`) y lo aplica a los de prueba (`transform`): así ninguna variable domina y no hay fuga de información.",
       "standardscaler estandarizar escalar normalizar variables pipeline escala fit transform fuga informacion", "classifiers/evaluacion_modelo.py"),
    _f("S02-6", 2, "¿Cómo se calcula la prioridad de un ticket?",
       "`calcular_prioridad(impacto, urgencia)` usa una matriz 3x3 con los valores Bajo, Medio y Alto: Alto con Alto da «Crítica»; Alto con Medio (o Medio con Alto) da «Alta»; Medio con Medio, Alto con Bajo y Bajo con Alto dan «Media»; el resto da «Baja». Si un valor no se reconoce, devuelve «Media».",
       "prioridad priorizacion impacto urgencia calcular_prioridad matriz critica alta media baja triage motor de reglas", "rules/prioritizer.py"),
    _f("S02-7", 2, "¿Cómo funciona la trazabilidad y la auditoría?",
       "Cada acción se registra con `registrar_traza` en `artifacts/audit.log`, mediante el módulo `logging`, con marca de tiempo, el ticket, la acción y el detalle. La página Trazas de Auditoría lo muestra.",
       "trazabilidad auditoria traza log registrar_traza audit.log eventos persistente logging", "audit/logger_audit.py"),
    _f("S02-8", 2, "¿Qué trazas deja el procesamiento de un ticket?",
       "Tres: RECEPCION (la descripción recibida), TAXONOMIA (categoría principal y detectadas) y PRIORIZACION (impacto, urgencia y prioridad asignada).",
       "traza recepcion taxonomia priorizacion auditoria registra ticket acciones", "audit/logger_audit.py"),
    # ---------------------------------------------------------------- Semana 03
    _f("S03-1", 3, "¿Cómo se clasifica un ticket de soporte?",
       "`classify_problem` normaliza el texto (minúsculas, sin tildes), cuenta las palabras clave de cada una de las 7 categorías con límites de palabra y elige la de mayor puntaje. Si ninguna coincide devuelve «Requiere análisis».",
       "clasificar clasificacion taxonomia categoria ticket classify_problem problema palabras clave puntaje clasificador taxonomico", "classifiers/taxonomia.py"),
    _f("S03-2", 3, "¿Qué áreas tiene la taxonomía de incidencias?",
       "Siete: Procesamiento de Lenguaje Natural (PLN), Aprendizaje Automático Predictivo, Búsqueda y Optimización de PC, Sistemas Expertos y Reglas de Soporte, Automatización y Mantenimiento de Software, Seguridad y Análisis de Errores (Logs), y Sistemas de Recomendación y Diagnóstico.",
       "areas categorias taxonomia siete 7 pln aprendizaje predictivo optimizacion pc sistemas expertos automatizacion seguridad logs recomendacion diagnostico", "classifiers/taxonomia.py"),
    _f("S03-3", 3, "¿Cómo se valida el clasificador de la Semana 03?",
       "Se compara la categoría principal automática de cada caso de `data/casos_ia.csv` con una referencia manual de 20 casos, y se genera el informe `reports/semana03.md` con la tabla y el porcentaje de coincidencia. El resumen del dashboard reporta 100%.",
       "validar validacion clasificador referencia manual casos csv casos_ia coincidencia porcentaje informe semana03", "classifiers/taxonomia.py"),
    _f("S03-4", 3, "¿Qué ticket de ejemplo procesa el pipeline?",
       "`main.py` procesa el ticket TICK-2026-001: la aplicación de nómina se cierra inesperadamente al generar el informe fiscal mensual, con impacto y urgencia Altos. El clasificador lo ubica en «Seguridad y Análisis de Errores (Logs)» y su prioridad es Crítica.",
       "ticket ejemplo tick-2026-001 nomina informe fiscal contabilidad caso demo", "src/main.py"),
    _f("S03-5", 3, "¿Qué reglas adicionales usa la taxonomía?",
       "Además de las palabras clave base, `CUSTOM_RULES` añade términos del contexto empresarial, como ventas, comercial, gerencia, operaciones, administración, financiero, DNS o troyano, para afinar la clasificación.",
       "reglas adicionales custom_rules palabras clave terminos empresariales ventas gerencia operaciones", "classifiers/taxonomia.py"),
    # ---------------------------------------------------------------- Semana 04
    _f("S04-1", 4, "¿Cómo funciona el planificador A*?",
       "Busca la secuencia de acciones de menor costo para llevar la red, la base de datos y el backend desde el estado inicial (0, 0, 0) hasta la meta (2, 2, 2). Usa una cola de prioridad (`heapq`) y la función f(n) = g(n) + h(n): costo real acumulado más una estimación heurística.",
       "astar a estrella planificador busqueda ruta optima secuencia acciones costo estado heapq cola prioridad", "classifiers/astar.py"),
    _f("S04-2", 4, "¿Qué heurística usa A* y por qué es admisible?",
       "La distancia de Manhattan al estado meta. Es admisible porque nunca sobreestima el costo real que falta, y eso garantiza que la ruta encontrada sea óptima.",
       "heuristica manhattan admisible distancia h(n) astar optima", "classifiers/astar.py"),
    _f("S04-3", 4, "¿Cómo se representa el estado en A*?",
       "Como una tupla (red, bd, app) con niveles de recuperación de 0 a 2. La meta es (2, 2, 2) y el dashboard ofrece 3 escenarios iniciales.",
       "estado tupla red bd app niveles meta escenarios espacio de estados", "classifiers/astar.py"),
    _f("S04-4", 4, "¿Cuál es el costo mínimo cuando todo está caído?",
       "Para el estado inicial (0, 0, 0) el costo mínimo es de 12 unidades de esfuerzo: subir cada componente al nivel 2 cuesta 2×1 en la red, 2×2 en la base de datos y 2×3 en el backend.",
       "costo minimo todo caido 12 unidades esfuerzo estado inicial 0 0 0 suma", "classifiers/astar.py"),
    _f("S04-5", 4, "¿Qué es Minimax y cómo se aplica a la ciberdefensa?",
       "Es un algoritmo de decisión adversarial. El código modela un tablero de 9 nodos de infraestructura con 8 líneas ganadoras (como el tres en raya): el Blue Team (X) defiende y el Red Team (O) ataca. Minimax explora todas las jugadas y elige el nodo que maximiza el resultado del defensor, suponiendo que el atacante juega de la mejor manera.",
       "minimax ciberdefensa adversarial blue team red team juego decision servidores matriz tablero nodos lineas", "classifiers/minimax.py"),
    _f("S04-6", 4, "¿Cuál es la función de utilidad de Minimax?",
       "+1 si el Blue Team completa una línea de tres nodos, -1 si la completa el Red Team y 0 si el tablero se llena sin ganador (contención).",
       "funcion utilidad minimax valores puntaje +1 0 -1 evaluacion linea ganadora empate", "classifiers/minimax.py"),
    _f("S04-7", 4, "¿Qué devuelve la simulación de ciberdefensa?",
       "La posición y el nodo seleccionados, la acción defensiva recomendada y una justificación técnica (`simular_ciberdefensa`). Con el tablero de ejemplo elige el nodo 6, Servidor de Backups, y recomienda «Blindar y aislar Servidor de Backups».",
       "simular_ciberdefensa resultado posicion nodo accion defensiva justificacion salida backups", "classifiers/minimax.py"),
    _f("S04-8", 4, "¿Qué acciones y costos tiene el planificador A*?",
       "Tres acciones, cada una sube un nivel del componente: reiniciar interfaces de red (costo 1), aplicar el script de recuperación en la base de datos (costo 2) y desplegar el hotfix en el microservicio backend (costo 3).",
       "acciones costos planificador astar reiniciar interfaces red script recuperacion base de datos hotfix backend", "classifiers/astar.py"),
    _f("S04-9", 4, "¿Qué nodos de infraestructura modela Minimax?",
       "Nueve: Firewall Perimetral, Servidor Web (DMZ), Gateway VPN, Directorio Activo, Base de Datos Central, Servidor de Correo, Servidor de Backups, Almacenamiento NAS y Balanceador de Carga.",
       "nodos infraestructura minimax firewall servidor web dmz vpn directorio activo base de datos correo backups nas balanceador", "classifiers/minimax.py"),
    # ---------------------------------------------------------------- Semana 05
    _f("S05-1", 5, "¿Qué es el sistema híbrido de la Semana 05?",
       "Un motor de tres capas: reglas (8 reglas por palabras clave), recuperación RAG con TF-IDF y similitud coseno sobre los 30 procedimientos de `data/base_conocimiento.txt`, y un clasificador de machine learning (regresión logística sobre TF-IDF). Genera un informe automático en Markdown.",
       "sistema hibrido reglas tfidf motor semana 5 consulta evidencia tres capas rag ml informe markdown", "classifiers/sistema_hibrido.py"),
    _f("S05-2", 5, "¿Qué es TF-IDF y para qué se usa aquí?",
       "TF-IDF pondera cada término por su frecuencia en un documento y por lo raro que es en el corpus. Se usa para convertir los 30 procedimientos de la base de conocimiento y la consulta en vectores comparables.",
       "tfidf tf-idf frecuencia termino documento vectorizar ponderacion corpus", "classifiers/sistema_hibrido.py"),
    _f("S05-3", 5, "¿Qué es la similitud coseno?",
       "Mide el ángulo entre dos vectores: 1 indica textos con el mismo contenido y 0 indica que no comparten términos. Se usa para elegir el procedimiento más parecido a la consulta.",
       "similitud coseno cosine angulo vectores parecido medida", "classifiers/sistema_hibrido.py"),
    _f("S05-4", 5, "¿Qué devuelve SistemaHibridoSoporte.procesar?",
       "Un diccionario con la consulta, las reglas activadas (o `regla_generica_soporte` si ninguna aplica), la evidencia recuperada, la similitud y la clase predicha.",
       "procesar sistemahibridosoporte devuelve resultado diccionario reglas evidencia similitud clase salida regla generica", "classifiers/sistema_hibrido.py"),
    _f("S05-5", 5, "¿Qué es la base de conocimiento (KB)?",
       "Un archivo con 30 procedimientos numerados, `data/base_conocimiento.txt`, con el formato problema -> procedimiento. Alimenta al motor TF-IDF y se muestra en la página Base de Conocimiento.",
       "base de conocimiento kb procedimientos 30 catalogo soluciones archivo txt formato", "data/base_conocimiento.txt"),
    _f("S05-6", 5, "¿Qué significa RAG en este proyecto?",
       "Recuperación aumentada (RAG): el sistema busca soluciones y documentación técnica previa asociadas al error reportado y las usa como evidencia, en lugar de responder sin respaldo.",
       "rag recuperacion aumentada generacion retrieval recuperador evidencia respaldo documentacion", "classifiers/sistema_hibrido.py"),
    _f("S05-7", 5, "¿Dónde se genera el informe de la Semana 05?",
       "`generar_reporte` crea un informe automático en Markdown en `reports/semana05.md` con los resultados de las pruebas del sistema híbrido.",
       "informe reporte semana 5 markdown generar_reporte reports semana05 resultados", "classifiers/sistema_hibrido.py"),
    _f("S05-8", 5, "¿Qué clases predice el clasificador de machine learning del sistema híbrido?",
       "Seis: hardware, red, rendimiento, seguridad, almacenamiento y software. Es una regresión logística sobre TF-IDF entrenada con 33 ejemplos de texto.",
       "clases predice clasificador machine learning regresion logistica hardware red rendimiento seguridad almacenamiento software 33 ejemplos", "classifiers/sistema_hibrido.py"),
    _f("S05-9", 5, "¿Qué reglas expertas tiene el sistema híbrido?",
       "Ocho reglas por palabras clave: temperatura, conectividad de red, optimización de recursos, amenazas de seguridad, gestión de almacenamiento, periféricos de impresión, redes y servidores, y gestión de identidad y accesos.",
       "reglas expertas ocho 8 palabras clave temperatura conectividad seguridad almacenamiento impresion servidores identidad accesos", "classifiers/sistema_hibrido.py"),
    # ---------------------------------------------------------------- Semana 07
    _f("S07-1", 7, "¿Qué tres representaciones del reconocimiento se implementaron?",
       "Numérica (distancia euclidiana sobre telemetría), simbólica (sistema experto con hechos y reglas SI-ENTONCES) y por autómata (un AFD que valida secuencias de eventos).",
       "representaciones reconocimiento tres enfoques numerica simbolica automata semana 7", "classifiers/representaciones.py"),
    _f("S07-2", 7, "¿Cómo funciona la representación numérica?",
       "Convierte el ticket en el vector [8.5, 9.0, 0.95] y mide su distancia euclidiana al perfil crítico [10, 10, 1.0]: resulta 1.803. Si la distancia es menor a 3.0 se activa una alerta de triaje y el ticket pasa directamente a un especialista humano.",
       "numerica distancia euclidiana vector telemetria perfil critico colapso triaje umbral 3.0 especialista humano", "classifiers/representaciones.py"),
    _f("S07-3", 7, "¿Cómo funciona la representación simbólica?",
       "Transforma los síntomas en hechos y aplica reglas por inclusión de conjuntos. Si están `pantalla_azul` y `reinicio_constante`, concluye falla de hardware físico y desvía a soporte de campo presencial. Si están `olvido_contrasena` y `active_directory`, concluye restablecimiento de credenciales y lo envía a un bot de nivel 1.",
       "simbolica sistema experto hechos reglas si entonces diagnostico sintomas conjuntos pantalla azul credenciales bot", "classifiers/representaciones.py"),
    _f("S07-4", 7, "¿Qué valida el autómata finito determinista (AFD)?",
       "Audita una secuencia de eventos con el alfabeto O (operativo), E (error) y T (timeout). Acepta la secuencia si termina con un error seguido de un timeout (`ET`): acepta `OOET` y `OOOEET`, y rechaza `OEE` (sin timeout) y `ETOO` (se recuperó).",
       "automata finito determinista afd alfabeto cronologia secuencia falla en cascada ET timeout estados q0 q1 q2 acepta rechaza", "classifiers/representaciones.py"),
    _f("S07-5", 7, "¿Qué diferencia hay entre una representación numérica y una simbólica?",
       "La numérica trabaja con magnitudes y distancias, es continua y aproximada. La simbólica trabaja con hechos y reglas discretas, es exacta y explicable.",
       "diferencia numerica simbolica comparar continua discreta explicable", "classifiers/representaciones.py"),
    # ---------------------------------------------------------------- Semana 08
    _f("S08-1", 8, "¿Qué integra la Semana 08?",
       "Un clasificador MLP, la carga de una imagen en Base64 con su descripción, la persistencia de la evidencia en SQLite y una ontología GraphML. El diagnóstico de la imagen se obtiene buscando en la base de conocimiento palabras del nombre y la descripción.",
       "semana 8 integra mlp base64 sqlite ontologia graphml evidencia imagen", "classifiers/reconocimiento.py"),
    _f("S08-2", 8, "¿Qué predice la red neuronal MLP?",
       "Clasifica en 4 clases de soporte (el dashboard las muestra como Hardware, Red, Software y Seguridad) a partir de cuatro características numéricas: impacto de la aplicación, urgencia, temperatura del servidor y fallos de red. Es un `MLPClassifier` con capas de 32 y 16 neuronas.",
       "mlp red neuronal predice categorias hardware red software seguridad impacto urgencia temperatura fallos clasificador capas neuronas", "classifiers/reconocimiento.py"),
    _f("S08-3", 8, "¿Qué es Base64 y por qué se usa con imágenes?",
       "Es una codificación que representa datos binarios como texto. Permite guardar la imagen junto con su descripción como evidencia dentro de la base de datos y enlazarla con el resto del flujo.",
       "base64 codificar imagen texto binario evidencia", "classifiers/reconocimiento.py"),
    _f("S08-4", 8, "¿Dónde se guardan la evidencia y las inferencias?",
       "En la tabla `evidencia_tickets` de `artifacts/soporte_evidencia.db`: vector de entrada, imagen en Base64, descripción, diagnóstico de la imagen, etiqueta real, predicción de la IA y fecha.",
       "sqlite base de datos evidencia guarda soporte_evidencia db tabla evidencia_tickets columnas inferencias persistente", "classifiers/reconocimiento.py"),
    _f("S08-5", 8, "¿Qué es la ontología GraphML?",
       "Un grafo dirigido (`artifacts/ontologia.graphml`, creado con networkx) con 6 conceptos y 7 relaciones: modelo MLP, ticket de soporte, categoría de falla, predicción IA, base de conocimiento e imagen de diagnóstico.",
       "ontologia graphml networkx grafo conceptos relaciones significado dominio seis siete", "classifiers/reconocimiento.py"),
    _f("S08-6", 8, "¿Dónde se guarda el modelo MLP entrenado?",
       "Serializado con pickle en `artifacts/modelo_mlp.pkl`. Si no existe, hay que ejecutar `python src/main.py` para entrenarlo.",
       "modelo mlp pkl pickle guardado serializado entrenado archivo modelo_mlp", "classifiers/reconocimiento.py"),
    _f("S08-7", 8, "¿Con qué datos se entrena el MLP y qué accuracy tiene?",
       "Con 200 muestras sintéticas aleatorias (semilla 42, 4 características y 4 clases) y una división 75/25. Sirve para demostrar el flujo completo, no para predecir telemetría real: su accuracy es cercano al azar (0.25 con 4 clases).",
       "datos entrenamiento mlp sinteticos aleatorios accuracy precision bajo azar muestras 200", "classifiers/reconocimiento.py"),
    _f("S08-8", 8, "¿Cómo se diagnostica la imagen en la Semana 08?",
       "No se analizan los píxeles: el código busca en `data/base_conocimiento.txt` la primera línea cuyas palabras (de más de 3 letras) aparezcan en el nombre del archivo o en la descripción, y devuelve ese procedimiento como diagnóstico.",
       "diagnostico imagen kb palabras clave nombre archivo descripcion buscar coincidencia procedimiento", "classifiers/reconocimiento.py"),
    # ---------------------------------------------------------------- Semana 09
    _f("S09-1", 9, "¿Qué hace el módulo de visión artificial?",
       "Convierte evidencia visual en información numérica: detecta contornos con Canny, calcula un umbral automático con Otsu y cuenta regiones conectadas en la imagen.",
       "vision artificial imagenes procesamiento contornos umbral regiones semana 9 pipeline", "classifiers/vision.py"),
    _f("S09-2", 9, "¿Qué es el detector de bordes Canny?",
       "Un algoritmo que aplica un filtro gaussiano (sigma=2.0 en el proyecto) y detecta los gradientes, es decir, los cambios bruscos de intensidad, para aislar los límites estructurales del hardware defectuoso.",
       "canny bordes contornos deteccion sigma intensidad gradiente filtro gaussiano", "classifiers/vision.py"),
    _f("S09-3", 9, "¿Qué es el umbral de Otsu?",
       "Un método que calcula automáticamente el punto del histograma que mejor separa los píxeles en dos clases (claro y oscuro) para generar una máscara binaria.",
       "otsu umbral automatico mascara binaria histograma segmentacion umbralizacion", "classifiers/vision.py"),
    _f("S09-4", 9, "¿Para qué sirven las regiones conectadas?",
       "Permiten contar grupos de píxeles unidos en la máscara. Es el primer paso para aislar piezas o zonas afectadas antes de pasarlas a un modelo.",
       "regiones conectadas etiquetado componentes conexas contar grupos pixeles", "classifiers/vision.py"),
    _f("S09-5", 9, "¿Qué imágenes analiza la visión artificial?",
       "Tres fallas de ejemplo: disco duro dañado (`disco_duro.png`), pantalla azul (`pantalla_azul.png`) y router sin conexión (`router.png`).",
       "imagenes ejemplos disco duro pantalla azul router fallas archivos png", "classifiers/vision.py"),
    _f("S09-6", 9, "¿Qué evidencia genera la visión artificial?",
       "La figura `artifacts/semana09_vision.png` (160 DPI) con tres paneles: imagen original en escala de grises, contornos de Canny y máscara binaria de Otsu. La función devuelve además el umbral y el número de regiones.",
       "evidencia genera artefactos salida imagen pipeline vision png figura paneles umbral regiones", "classifiers/vision.py"),
    # ---------------------------------------------------------------- Semana 10
    _f("S10-1", 10, "¿Qué es LBP (Local Binary Patterns)?",
       "Un descriptor de textura que compara cada píxel con sus vecinos y codifica el patrón como un número. El proyecto usa radio 1, 8 vecinos y el método `uniform`, que produce un histograma de 10 intervalos.",
       "lbp local binary patterns textura descriptor histograma vecinos radio uniform intervalos", "classifiers/texturas.py"),
    _f("S10-2", 10, "¿Qué compara la Semana 10?",
       "Un componente en estado óptimo contra uno averiado, lado a lado, con sus imágenes, sus histogramas de intensidad y de LBP, y sus vectores de características.",
       "semana 10 comparativa bueno malo optimo averiado histogramas lado a lado", "classifiers/texturas.py"),
    _f("S10-3", 10, "¿Qué fallas de hardware se analizan?",
       "Disco duro (daño por golpe, rayones en la superficie magnética y no gira), router (conexión intermitente) y pantalla (daño por golpe y no arranca).",
       "fallas hardware disco duro golpe rayones no gira router intermitente pantalla no arranca", "classifiers/texturas.py"),
    _f("S10-4", 10, "¿Qué es el vector de características de la Semana 10?",
       "Es el vector que devuelve `procesar_imagen_proyecto`, con 3 valores: el área media y la desviación estándar del área de las regiones, y la cantidad de regiones (se descartan las de menos de 50 píxeles). Los histogramas de intensidad (32 intervalos) y de LBP se devuelven aparte.",
       "vector caracteristicas features numpy extraccion area media desviacion estandar cantidad regiones 50 pixeles", "classifiers/texturas.py"),
    _f("S10-5", 10, "¿Cómo se asocia un diagnóstico a una imagen en la Semana 10?",
       "El código calcula los histogramas y el vector de características, y el diagnóstico textual de cada imagen se toma del diccionario `FALLOS_DESCRIPCION` según su nombre de archivo. La comparación entre componente sano y averiado se hace contrastando sus histogramas y vectores en el dashboard.",
       "diagnostico asociar imagen fallos descripcion diccionario nombre archivo anomalia textura sano averiado", "classifiers/texturas.py"),
    _f("S10-6", 10, "¿Qué hace la función procesar_imagen_proyecto?",
       "Convierte la imagen a escala de grises, calcula el histograma de intensidad y el LBP, aplica el umbral de Otsu, etiqueta las regiones y devuelve la imagen, la máscara, los dos histogramas y el vector de características.",
       "procesar_imagen_proyecto funcion pasos pipeline gris histograma lbp otsu etiquetado devuelve", "classifiers/texturas.py"),
    # ---------------------------------------------------------------- Semana 11
    _f("S11-1", 11, "¿Qué modelos compara el benchmark de la Semana 11?",
       "Regresión Logística (con StandardScaler), Random Forest (250 árboles) y MLPClassifier (una capa de 64 neuronas, con StandardScaler), con el mismo protocolo: `train_test_split` 75/25, semilla 42 y estratificación.",
       "benchmark modelos comparar regresion logistica random forest mlp mlpclassifier semana 11 protocolo particion semilla arboles", "classifiers/benchmark.py"),
    _f("S11-2", 11, "¿Qué métricas y qué criterio se usan para elegir el mejor modelo?",
       "Se registran el accuracy y el tiempo de entrenamiento (`fit_seconds`) en `artifacts/benchmark.csv`. La tabla se ordena por accuracy y el modelo con el valor más alto es el ganador: se serializa como `mejor_modelo.pkl`.",
       "metrica metricas accuracy tiempo entrenamiento fit_seconds elegir mejor modelo ganador seleccion criterio benchmark csv", "classifiers/benchmark.py"),
    _f("S11-3", 11, "¿Dónde se guarda el mejor modelo?",
       "Serializado en `artifacts/mejor_modelo.pkl`.",
       "mejor modelo guardado serializado pkl ubicacion archivo mejor_modelo", "classifiers/benchmark.py"),
    _f("S11-4", 11, "¿Qué es un ADR?",
       "Un Registro de Decisión Arquitectónica: documento que justifica por qué se eligió un modelo. `ejecutar_benchmark_semana11` lo genera automáticamente en `reports/semana11_adr.md`, junto con la tabla de resultados.",
       "adr registro decision arquitectonica justificacion tecnica informe documento semana11_adr", "classifiers/benchmark.py"),
    _f("S11-5", 11, "¿Qué accuracy obtuvo el modelo óptimo del benchmark?",
       "En la ejecución de referencia ganó MLPClassifier con 0.98 de accuracy, frente a 0.9778 de la Regresión Logística y 0.9667 del Random Forest. Los valores pueden variar levemente según la versión de scikit-learn.",
       "accuracy modelo optimo 98 resultado benchmark mejor desempeno ganador mlp resultados", "classifiers/benchmark.py"),
    _f("S11-6", 11, "¿Por qué el benchmark debe ser reproducible?",
       "Para que cualquiera obtenga los mismos resultados con la misma semilla y partición de datos. Así la elección del modelo se justifica con evidencia verificable.",
       "reproducible reproducibilidad semilla particion protocolo resultados repetir", "classifiers/benchmark.py"),
    _f("S11-7", 11, "¿Con qué dataset se hace el benchmark?",
       "Con `load_digits` de scikit-learn (1797 imágenes de dígitos escritos a mano de 8x8 píxeles, 10 clases), como conjunto de referencia reproducible. No usa tickets reales.",
       "dataset datos benchmark load_digits digitos escritos a mano 1797 referencia conjunto", "classifiers/benchmark.py"),
    # ---------------------------------------------------------------- Semana 13
    _f("S13-1", 13, "¿Qué es el motor de inferencia de la Semana 13?",
       "Un sistema basado en reglas de Horn con encadenamiento hacia adelante que deduce diagnósticos a partir de hechos observados y explica cada paso.",
       "motor inferencia semana 13 reglas horn deduce diagnosticos logica proposicional", "classifiers/motor_inferencia.py"),
    _f("S13-2", 13, "¿Qué es una regla de Horn?",
       "Una implicación con premisas unidas por conjunción (∧) y una sola conclusión. Por ejemplo: `imagen_procesada_ok ∧ textura_anomala_detectada → diagnostico_hardware_fallido`.",
       "regla horn implicacion premisas conclusion conjuncion clausula", "classifiers/motor_inferencia.py"),
    _f("S13-3", 13, "¿Qué es el encadenamiento hacia adelante?",
       "Partir de los hechos iniciales, aplicar toda regla cuyas premisas se cumplan, añadir su conclusión como hecho nuevo y repetir hasta que no se deduzca nada más.",
       "encadenamiento hacia adelante forward chaining hechos iniciales deducir proceso", "classifiers/motor_inferencia.py"),
    _f("S13-4", 13, "¿Cuántas reglas tiene el motor y qué cubren?",
       "Diez reglas (R1 a R10): diagnóstico de hardware y escalamiento por SLA (R1-R3), falla de enlace WAN (R4-R5), saturación de almacenamiento (R6-R7), incidentes de seguridad de credenciales (R8-R9) y falla crítica del software de nómina (R10).",
       "cuantas reglas diez 10 r1 r10 catalogo cobertura escalamiento sla wan almacenamiento seguridad nomina", "classifiers/motor_inferencia.py"),
    _f("S13-5", 13, "¿Qué es el Modus Ponens y cómo se muestra?",
       "Si se cumple P y existe la regla P → Q, entonces se concluye Q. El motor registra cada regla aplicada y la muestra como una explicación paso a paso de cómo llegó a cada conclusión.",
       "modus ponens explicabilidad explicacion paso a paso traza razonamiento", "classifiers/motor_inferencia.py"),
    _f("S13-6", 13, "¿Qué pasa si falta una premisa?",
       "La conclusión final no se alcanza, pero sí los pasos intermedios. Una conclusión no demostrada no significa que sea falsa: indica que no hay evidencia suficiente en los hechos iniciales.",
       "falta premisa conclusion no demostrada insuficiente evidencia faltan hechos", "classifiers/motor_inferencia.py"),
    _f("S13-7", 13, "¿Qué pruebas tiene el motor de inferencia?",
       "Pruebas unittest de conclusión demostrada, conclusión no demostrada, inmutabilidad de los hechos de entrada y ausencia de ciclos infinitos.",
       "pruebas unittest motor inferencia inmutabilidad ciclos infinitos casos", "tests/test_motor_inferencia.py"),
    # ---------------------------------------------------------------- Semana 14
    _f("S14-1", 14, "¿Qué es una red semántica?",
       "Un grafo dirigido de conceptos unidos por relaciones. Cada hecho es un triple (sujeto, relación, objeto), por ejemplo (servidor_bd, es_un, hardware_critico).",
       "red semantica grafo triples conceptos relaciones sujeto objeto semana 14", "classifiers/red_semantica.py"),
    _f("S14-2", 14, "¿Qué conceptos y relaciones tiene la red semántica?",
       "8 conceptos de soporte TI (servidor_bd, estacion_trabajo, hardware_critico, hardware_estandar, activo_corporativo, alimentacion_redundante, sobrecalentamiento y limpieza_ventilacion) y 3 relaciones: es_un, requiere y se_resuelve_con.",
       "conceptos relaciones cuales cuantos ocho 8 tres 3 es_un requiere se_resuelve_con dominio", "classifiers/red_semantica.py"),
    _f("S14-3", 14, "¿Cómo se infiere por jerarquía (es_un)?",
       "Con la regla de transitividad: si A es_un B y B es_un C, entonces A es_un C. Una búsqueda en anchura encuentra la cadena de hechos que lo prueba; por eso servidor_bd es un activo_corporativo aunque ese triple no esté almacenado.",
       "inferencia jerarquia es_un transitividad cadena prueba busqueda anchura", "classifiers/red_semantica.py"),
    _f("S14-4", 14, "¿Cómo funciona la herencia de propiedades?",
       "Si A es_un B y B requiere P, entonces A requiere P. Así servidor_bd hereda alimentacion_redundante de activo_corporativo. Solo la relación `requiere` se hereda.",
       "herencia propiedades hereda requiere alimentacion redundante subcategoria", "classifiers/red_semantica.py"),
    _f("S14-5", 14, "¿Cómo se interpretan las oraciones en la red semántica?",
       "Se normaliza el texto y se reconocen tres formatos: `A es un B`, `A requiere B` (o necesita) y `A se resuelve con B`. Si no coincide ninguno se lanza `ValueError` sin modificar la red.",
       "interpretar oraciones normalizar formatos triple valueerror validacion lenguaje", "classifiers/red_semantica.py"),
    _f("S14-6", 14, "¿Qué significa que una consulta no tenga evidencia?",
       "La red trabaja con mundo cerrado: concluye solo lo que puede demostrar con los hechos cargados. Un `False` significa no demostrado, no falso.",
       "sin evidencia mundo cerrado false no demostrado consulta suposicion", "classifiers/red_semantica.py"),
    _f("S14-7", 14, "¿Cómo se evitan los ciclos en la red semántica?",
       "Con un conjunto de nodos visitados durante la búsqueda: un ciclo como A es_un B y B es_un A no produce un bucle infinito.",
       "ciclos visitados bucle infinito control recorrido grafo", "classifiers/red_semantica.py"),
    _f("S14-8", 14, "¿Cuántas pruebas tiene la Semana 14?",
       "41 pruebas unittest en 5 clases: normalización, interpretación de oraciones, relaciones explícitas, inferencia por jerarquía y herencia.",
       "pruebas tests unittest cuantas 41 semana 14 red semantica clases", "tests/test_red_semantica.py"),
    _f("S14-9", 14, "¿Cómo se integra la base de conocimiento a la red semántica?",
       "En la red ampliada del dashboard, cada uno de los 30 casos es_un categoría técnica, cada categoría es_un activo_corporativo y requiere un recurso propio. Por herencia, cada caso recibe esos requisitos.",
       "red ampliada kb 30 casos integracion categoria tecnica herencia dashboard", "dashboard.py"),
]

# ---------------------------------------------------------------------------
# Motor de búsqueda: TF-IDF + similitud coseno
# ---------------------------------------------------------------------------
_STOP = frozenset(
    "a al algo ante cada como con contra cual cuales cuando cuanto cuantos cuantas de del desde donde "
    "durante e el ella ellos en entre es esa ese eso esta este esto estos fue ha han hace hacen hacer "
    "hay la las le les lo los me mi mis muy ni no nos o otra otro para pero por porque puede pueden "
    "que quien se ser si sin sobre son su sus tambien te tiene tienen tu un una uno unos unas y ya "
    "explicame dime quiero saber".split())


def _normalizar_texto(texto: str) -> str:
    base = unicodedata.normalize("NFD", str(texto).casefold())
    base = "".join(c for c in base if unicodedata.category(c) != "Mn")
    base = re.sub(r"\ba\s*\*", " astar ", base)
    base = re.sub(r"\ba estrella\b", " astar ", base)
    base = re.sub(r"tf\s*-?\s*idf", " tfidf ", base)
    base = re.sub(r"standard\s*scaler", " standardscaler ", base)
    return base


def _raiz(token: str) -> str:
    if len(token) > 4 and token.endswith("es"):
        token = token[:-2]
    elif len(token) > 3 and token.endswith("s"):
        token = token[:-1]
    if len(token) > 4 and token[-1] in "aeo":
        token = token[:-1]
    return token


def _palabras(texto: str) -> list:
    return [_raiz(t) for t in re.findall(r"[a-z0-9]+", _normalizar_texto(texto))
            if t not in _STOP and len(t) > 1]


def _caracteres(texto: str, n: int = 4) -> list:
    gramas = []
    for t in re.findall(r"[a-z0-9]+", _normalizar_texto(texto)):
        if t in _STOP or len(t) < 3:
            continue
        marcado = f"_{t}_"
        gramas += [marcado[i:i + n] for i in range(max(1, len(marcado) - n + 1))]
    return gramas


class _Tfidf:
    """TF-IDF con idf suavizado y vectores normalizados (L2)."""

    def __init__(self, documentos: list):
        self.n = len(documentos)
        df = Counter()
        for doc in documentos:
            df.update(set(doc))
        self.idf = {t: math.log((1 + self.n) / (1 + c)) + 1.0 for t, c in df.items()}
        self.vectores = [self.vectorizar(doc) for doc in documentos]

    def vectorizar(self, tokens: list) -> dict:
        tf = Counter(t for t in tokens if t in self.idf)
        vec = {t: (1 + math.log(c)) * self.idf[t] for t, c in tf.items()}
        norma = math.sqrt(sum(v * v for v in vec.values()))
        return {t: v / norma for t, v in vec.items()} if norma else {}

    @staticmethod
    def coseno(a: dict, b: dict) -> float:
        if len(a) > len(b):
            a, b = b, a
        return sum(v * b.get(t, 0.0) for t, v in a.items())


class AsistenteFAQ:
    """Recupera las preguntas frecuentes más parecidas a una consulta."""

    PESO_PALABRAS = 0.7
    PESO_CARACTERES = 0.3

    def __init__(self, faqs: list = None):
        self.faqs = list(FAQ_SEMANAS if faqs is None else faqs)
        textos_p = [" ".join([f["pregunta"]] * 3 + [f["claves"]] * 2 + [f["respuesta"]]) for f in self.faqs]
        textos_c = [f"{f['pregunta']} {f['claves']}" for f in self.faqs]
        self._palabras = _Tfidf([_palabras(t) for t in textos_p])
        self._caracteres = _Tfidf([_caracteres(t) for t in textos_c])

    def semanas_disponibles(self) -> list:
        return sorted({f["semana"] for f in self.faqs})

    def por_semana(self, semana=None) -> list:
        return [dict(f) for f in self.faqs if semana is None or f["semana"] == semana]

    def sugerencias(self, n: int = 4) -> list:
        """Preguntas de ejemplo, una por semana distinta."""
        ids = ("S04-1", "S05-2", "S13-4", "S14-3", "S10-1", "S09-3", "S11-4", "S02-1")
        por_id = {f["id"]: f["pregunta"] for f in self.faqs}
        return [por_id[i] for i in ids if i in por_id][:n]

    def buscar(self, consulta: str, k: int = 3, semana=None, umbral: float = 0.15) -> list:
        """Devuelve hasta k preguntas con su similitud (0-1), de mayor a menor.
        Lista vacía si la consulta está vacía o ninguna supera el umbral."""
        if not isinstance(consulta, str):
            raise ValueError("La consulta debe ser un texto.")
        if not consulta.strip():
            return []
        qp = self._palabras.vectorizar(_palabras(consulta))
        qc = self._caracteres.vectorizar(_caracteres(consulta))
        if not qp and not qc:
            return []
        resultados = []
        for i, faq in enumerate(self.faqs):
            if semana is not None and faq["semana"] != semana:
                continue
            s = (self.PESO_PALABRAS * _Tfidf.coseno(qp, self._palabras.vectores[i])
                 + self.PESO_CARACTERES * _Tfidf.coseno(qc, self._caracteres.vectores[i]))
            if s >= umbral:
                resultados.append((s, i))
        resultados.sort(key=lambda x: (-x[0], x[1]))
        return [{**self.faqs[i], "similitud": round(min(s, 1.0), 4)} for s, i in resultados[:k]]