# Semana 03: Taxonomía de IA en Entorno Empresarial (Soporte TI)

## Integrantes del Proyecto
* **Marco Molina Molina**
* **Daniel Eduardo Daza Cuello**
* **Institución / Curso:** ETITC - 10º Semestre

## Enlace al Repositorio
[https://github.com/DanielDaza2901/asistente_soporte_TI_hibrido](https://github.com/DanielDaza2901/asistente_soporte_TI_hibrido)

---

## Validación del Modelo (Matriz de Confusión)
Como requerimiento adicional de la Semana 02, se implementó una validación mediante matriz de confusión usando el dataset *Iris*. El sistema alcanzó un **Accuracy de 0.921**, demostrando la robustez del entorno base para tareas de clasificación multiclase.

---

## Resultado automático frente a clasificación manual de referencia
| Caso | Categoría automática principal | Categorías detectadas | Manual | Estado |
|---|---|---|---|---|
| 1 | Procesamiento de Lenguaje Natural (PLN) | Procesamiento de Lenguaje Natural (PLN) | Seguridad y Análisis de Errores (Logs) | Revisar |
| 2 | Procesamiento de Lenguaje Natural (PLN) | Procesamiento de Lenguaje Natural (PLN), Aprendizaje Automático Predictivo | Sistemas de Recomendación y Diagnóstico | Revisar |
| 3 | Aprendizaje Automático Predictivo | Aprendizaje Automático Predictivo, Búsqueda y Optimización de PC | Aprendizaje Automático Predictivo | Coincide |
| 4 | Búsqueda y Optimización de PC | Búsqueda y Optimización de PC, Sistemas de Recomendación y Diagnóstico | Búsqueda y Optimización de PC | Coincide |
| 5 | Sistemas de Recomendación y Diagnóstico | Sistemas de Recomendación y Diagnóstico, Seguridad y Análisis de Errores (Logs) | Sistemas de Recomendación y Diagnóstico | Coincide |
| 6 | Seguridad y Análisis de Errores (Logs) | Seguridad y Análisis de Errores (Logs), Procesamiento de Lenguaje Natural (PLN) | Seguridad y Análisis de Errores (Logs) | Coincide |
| 7 | Búsqueda y Optimización de PC | Búsqueda y Optimización de PC, Sistemas Expertos y Reglas de Soporte, Sistemas de Recomendación y Diagnóstico | Búsqueda y Optimización de PC | Coincide |
| 8 | Procesamiento de Lenguaje Natural (PLN) | Procesamiento de Lenguaje Natural (PLN) | Procesamiento de Lenguaje Natural (PLN) | Coincide |
| 9 | Aprendizaje Automático Predictivo | Aprendizaje Automático Predictivo | Aprendizaje Automático Predictivo | Coincide |
| 10 | Sistemas Expertos y Reglas de Soporte | Sistemas Expertos y Reglas de Soporte, Seguridad y Análisis de Errores (Logs), Sistemas de Recomendación y Diagnóstico | Sistemas Expertos y Reglas de Soporte | Coincide |
| 11 | Automatización y Mantenimiento de Software | Automatización y Mantenimiento de Software, Sistemas de Recomendación y Diagnóstico | Automatización y Mantenimiento de Software | Coincide |
| 12 | Procesamiento de Lenguaje Natural (PLN) | Procesamiento de Lenguaje Natural (PLN), Búsqueda y Optimización de PC | Procesamiento de Lenguaje Natural (PLN) | Coincide |
| 13 | Automatización y Mantenimiento de Software | Automatización y Mantenimiento de Software | Automatización y Mantenimiento de Software | Coincide |
| 14 | Sistemas Expertos y Reglas de Soporte | Sistemas Expertos y Reglas de Soporte | Sistemas Expertos y Reglas de Soporte | Coincide |
| 15 | Procesamiento de Lenguaje Natural (PLN) | Procesamiento de Lenguaje Natural (PLN) | Seguridad y Análisis de Errores (Logs) | Revisar |
| 16 | Sistemas de Recomendación y Diagnóstico | Sistemas de Recomendación y Diagnóstico | Sistemas de Recomendación y Diagnóstico | Coincide |
| 17 | Seguridad y Análisis de Errores (Logs) | Seguridad y Análisis de Errores (Logs) | Seguridad y Análisis de Errores (Logs) | Coincide |
| 18 | Sistemas Expertos y Reglas de Soporte | Sistemas Expertos y Reglas de Soporte, Sistemas de Recomendación y Diagnóstico | Sistemas Expertos y Reglas de Soporte | Coincide |
| 19 | Automatización y Mantenimiento de Software | Automatización y Mantenimiento de Software, Búsqueda y Optimización de PC, Aprendizaje Automático Predictivo | Automatización y Mantenimiento de Software | Coincide |
| 20 | Búsqueda y Optimización de PC | Búsqueda y Optimización de PC, Sistemas Expertos y Reglas de Soporte | Búsqueda y Optimización de PC | Coincide |

Coincidencia con la referencia: **85.00%** (17/20).

---

Documentación de la Práctica - Semana 03: Taxonomía de IA en Soporte de Software Empresarial
## 1. Resumen del Módulo
Durante la Semana 03, se implementó el módulo de clasificación y taxonomía inteligente para el Asistente de Soporte TI Híbrido. El sistema está diseñado para procesar de manera automatizada incidencias de software de PC en un entorno corporativo multi-departamental (Contabilidad, Recursos Humanos, Ventas, Logística, Gerencia, etc.), categorizando los tickets y facilitando la toma de decisiones del equipo técnico.

---

## 2. Arquitectura y Componentes Desarrollados
Conjunto de Datos (data/casos_ia.csv):

Se definieron 20 casos de prueba reales centrados exclusivamente en problemas de software de computadora (sistemas operativos, suites ofimáticas, aplicaciones ERP, antivirus corporativos, políticas de rendimiento y parches).

Cada caso está contextualizado en un departamento específico de la empresa para reflejar un escenario de negocio real.

Clasificador Taxonómico (src/classifiers/semana03_taxonomia.py):

Implementa una estructura basada en dataclasses y reglas de procesamiento de lenguaje natural liviano (normalización de texto, eliminación de tildes y caracteres especiales).

Clasifica las incidencias en 7 categorías principales de IA aplicada a soporte:

Procesamiento de Lenguaje Natural (PLN).

Aprendizaje Automático Predictivo.

Búsqueda y Optimización de PC.

Sistemas Expertos y Reglas de Soporte.

Automatización y Mantenimiento de Software.

Seguridad y Análisis de Errores (Logs).

Sistemas de Recomendación y Diagnóstico.

Motor de Reglas y Validación de Referencia:

Contiene reglas personalizadas (CUSTOM_RULES) orientadas a palabras clave empresariales y departamentales.

Valida automáticamente los resultados frente a un conjunto de referencia manual (MANUAL_REFERENCE), generando un indicador de precisión (Accuracy) reflejado en el reporte markdown (reports/semana03.md).

---

## 3. Integración en el Flujo del Asistente (src/main.py)
La taxonomía se integró al flujo central del proyecto junto con el sistema de auditoría (audit/logger_audit.py) y el motor de priorización (rules/prioritizer.py).

El flujo de procesamiento de un ticket ahora realiza lo siguiente:

Recepción y Registro: Se recibe la descripción del problema del usuario y se genera una traza inicial en artifacts/audit.log.

Clasificación por IA: La descripción es analizada por la taxonomía de la Semana 03 para determinar la categoría técnica y el área afectada.

Priorización: El motor de reglas evalúa el impacto y la urgencia para asignar un nivel de prioridad.

Trazabilidad Completa: Todas las etapas quedan debidamente auditadas y registradas para su trazabilidad técnica.

---

## 4. Resultados y Métricas
Precisión de Clasificación: La ejecución del script compara la salida algorítmica con la pauta manual, logrando un alto porcentaje de acierto en la categorización de los 20 escenarios corporativos.

Trazabilidad: Los archivos generados en artifacts/ y reports/ garantizan la reproducibilidad y el cumplimiento de los entregables académicos del proyecto.

---

