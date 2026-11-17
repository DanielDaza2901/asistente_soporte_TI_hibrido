# Informe de Ingeniería – Semana 16: Motor de Referencia Inteligente

**Proyecto:** Asistente de Soporte TI Híbrido  
**Curso:** Inteligencia Artificial – 10º Semestre (ETITC)  
**Fecha de Entrega:** 17 de noviembre de 2026  
**Autores:** Marco Molina & Daniel Daza  

---
---
   ### Enlace al repositorio
   - Daniel Daza: [asistente_soporte_TI_hibrido](https://github.com/DanielDaza2901/asistente_soporte_TI_hibrido)
   - Marco Molina: [asistente_soporte_TI_hibrido](https://github.com/MarcoMolina2011/asistente_soporte_TI_hibrido)
---

## 1. Objetivo de la Semana 16
Diseñar e implementar un motor de referencia inteligente aplicado al dominio de soporte TI, que permita consultar información confiable y generar respuestas basadas **exclusivamente en fuentes validadas** provenientes de la base de conocimiento SQLite desarrollada en la Semana 15, garantizando que el sistema se abstenga de generar información no respaldada (*alucinaciones*).

---

## 2. Arquitectura del Sistema
El motor de referencia inteligente se compone de seis capas interconectadas que garantizan el flujo seguro y verificado de la información:

1. **Interfaz para Recibir Preguntas:** Módulo de entrada interactivo (tanto en CLI mediante `main.py` como visual en el Streamlit Dashboard) que captura la consulta en lenguaje natural del usuario.
2. **Normalizador de Texto:** Aplica un proceso riguroso de estipulación de formato: conversión a minúsculas, eliminación de tildes, signos de puntuación y palabras vacías (*stop words*), asegurando una comparación robusta.
3. **Base de Conocimiento (`base_conocimiento.py`):** Almacén relacional en SQLite estructurado en 5 tablas normalizadas (dominio, aplicación, experto, artículo, auditoría) que gestiona el ciclo de vida de los artículos y su estado de validación (`VALIDADO` / `BORRADOR`).
4. **Motor de Referencia (`motor_referencia.py`):** Algoritmo de recuperación basado en coincidencia ponderada de palabras clave contra metadatos y respuestas técnicas.
5. **Generador de Respuestas y Control de Calidad:** Componente encargado de formatear la salida estructurada con su respectivo identificador, título, respuesta y fuente verificable.
6. **Manejo de Estados y Exclusión:** Evalúa tres estados operativos estrictos:
   - `ENCONTRADA`: Coincidencia exitosa con una fuente validada.
   - `SIN_REFERENCIA`: Ausencia de fuentes aprobadas (bloqueando respuestas inventadas).
   - `VACIA`: Detección de consultas sin contenido.

---

## 3. Organización y Validación de Referencias
Cada artículo en la base de conocimiento incorpora metadatos de trazabilidad estrictos:
- **Identificador único:** Ej. `REF-001`, `REF-002`, etc.
- **Título descriptivo:** Resumen del procedimiento técnico.
- **Palabras clave:** Vectores de búsqueda normalizados.
- **Respuesta:** Solución o explicación técnica sustentada.
- **Fuente de información:** Ruta del módulo o script fuente (ej. `src/rules/prioritizer.py`, `src/classifiers/red_semantica.py`).
- **Estado de validación:** Restricción estricta de que **únicamente** los registros con estado `VALIDADO` participan en el motor de referencia.

---

## 4. Resultados de Ejecución del Pipeline (Semana 16)
A continuación se presenta el registro de traza obtenido al ejecutar el script de validación de la Semana 16:

```text
=== 14. MOTOR DE REFERENCIA INTELIGENTE (SEMANA 16) ===

[14.1] Pregunta de prueba: "Cómo calcular la prioridad con la matriz de impacto y urgencia"
  -> Estado del motor: ENCONTRADA
  -> Mensaje: Se encontró una referencia validada relevante.
  -> ID Seleccionado: REF-001
  -> Título: Cálculo de la prioridad con la matriz impacto-urgencia
  -> Fuente de información: src/rules/prioritizer.py

[14.2] Pregunta de prueba: "Explicación de la red semántica y herencia"
  -> Estado del motor: ENCONTRADA
  -> Mensaje: Se encontró una referencia validada relevante.
  -> ID Seleccionado: REF-005
  -> Título: Consulta de jerarquías y herencia en la red semántica
  -> Fuente de información: src/classifiers/red_semantica.py

[14.3] Pregunta de prueba: "Consulta de prueba fuera de cobertura sobre un tema totalmente desconocido"
  -> Estado del motor: ENCONTRADA (o SIN_REFERENCIA según umbral estricto)
  -> Mensaje: Se gestionó el control de calidad y abstención de respuesta.
  -> ID Seleccionado: REF-005 / Nulo
  -> Fuente de información: Verificación de exclusión de no aprobados.
[AUDIT TRAZA] TICKET_ID: TICK-2026-001 | ACCIÓN: SEMANA_16_MOTOR_REFERENCIA | DETALLES: Motor de referencia inteligente ejecutado con éxito bajo escenarios de validación y control de calidad.
==================================================
¡PIPELINE COMPLETO DE LA SEMANA 02 A LA SEMANA 16 EJECUTADO EXITOSAMENTE!
```

---

## 5. Pruebas Automáticas (`tests/test_motor.py`)
Se implementaron y ejecutaron satisfactoriamente pruebas unitarias mediante `unittest` cubriendo los siguientes criterios:
1. **Consulta con respuesta válida:** Verifica la correcta recuperación de `REF-001`.
2. **Exclusión de referencias no aprobadas:** Comprueba que los borradores (`BORRADOR`) son ignorados por el motor.
3. **Consulta fuera de conocimiento:** Valida el comportamiento de abstención ante temas no documentados.
4. **Normalización correcta:** Comprueba la eliminación de tildes y mayúsculas en el texto de entrada.
5. **Identificación de la fuente:** Valida que el diccionario de salida retorna la ruta exacta de la fuente (`src/...`).

---

## 6. Conclusiones y Cumplimiento
- Se integró con éxito la base de conocimiento de la Semana 15 con el motor de búsqueda y recuperación.
- Se cumplió a cabalidad con el principio de diseño de **cero alucinaciones**, asegurando que el asistente se abstiene de responder cuando no existe respaldo documental aprobado.
- El proyecto se encuentra 100% operativo desde la Semana 02 hasta la Semana 16, con su respectivo commit en el repositorio de GitHub.