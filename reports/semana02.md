# Documentación de la Práctica - Semana 02: Arquitectura Base, Auditoría y Motor de Reglas

## 👥 Integrantes del Proyecto
* **Marco Molina Molina**
* **Daniel Eduardo Daza Cuello**
* **Institución / Curso:** ETITC - 10º Semestre

## 🔗 Enlace al Repositorio
[https://github.com/DanielDaza2901/asistente_soporte_TI_hibrido](https://github.com/DanielDaza2901/asistente_soporte_TI_hibrido)

---

## 1. Resumen del Módulo
Durante la **Semana 02**, se estableció la arquitectura fundamental del **Asistente de Soporte TI Híbrido**. El objetivo principal fue construir los cimientos del proyecto orientados a la gestión de incidentes de software de PC en entornos empresariales, incorporando mecanismos estrictos de trazabilidad, logging y reglas de negocio deterministas para la priorización de tickets.

## 2. Componentes y Estructura Desarrollada
* **Sistema de Auditoría y Trazabilidad (`src/audit/logger_audit.py`)**: Implementa un sistema de registro basado en la librería estándar `logging` de Python, configurado para generar trazas persistentes en `artifacts/audit.log` con marcas de tiempo precisas.
* **Motor de Reglas y Priorización (`src/rules/prioritizer.py`)**: Desarrollado bajo un enfoque de sistemas expertos, evalúa el Impacto y la Urgencia para determinar de manera automatizada la Prioridad de atención.
* **Validación del Modelo (Matriz de Confusión)**: Se integró un módulo de validación con el dataset *Iris* para evaluar la robustez del clasificador. El sistema alcanzó un **Accuracy de 0.921**, permitiendo visualizar mediante la matriz de confusión la precisión del modelo en la clasificación multiclase.

## 3. Flujo Principal del Sistema (`src/main.py`)
El flujo actual orquesta la ejecución del sistema:
1. **Validación:** Ejecución de la matriz de confusión y métricas de rendimiento.
2. **Recepción:** Captura inicial de la descripción del problema reportado.
3. **Taxonomía:** Clasificación del incidente mediante IA (Semana 03).
4. **Priorización:** Ejecución del motor de reglas para asignar la criticidad del ticket.
5. **Trazabilidad:** Almacenamiento automático de toda la secuencia en `artifacts/`.

## 4. Conclusión y Resultados
La arquitectura base construida permitió estructurar modularmente el proyecto, garantizando transparencia técnica y trazabilidad auditable. La integración de la validación matemática mediante la matriz de confusión asegura que el sistema sea capaz de clasificar problemas con una alta precisión, cumpliendo con los estándares de ingeniería requeridos.