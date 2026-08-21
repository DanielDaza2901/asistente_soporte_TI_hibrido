Documentación de la Práctica - Semana 02: Arquitectura Base, Auditoría y Motor de Reglas
1. Resumen del Módulo
Durante la Semana 02, se estableció la arquitectura fundamental del Asistente de Soporte TI Híbrido. El objetivo principal fue construir los cimientos del proyecto orientados a la gestión de incidentes de software de PC en entornos empresariales, incorporando mecanismos estrictos de trazabilidad, logging y reglas de negocio deterministas para la priorización de tickets.

2. Componentes y Estructura Desarrollada
Sistema de Auditoría y Trazabilidad (src/audit/logger_audit.py):

Implementa un sistema de registro basado en la librería estándar logging de Python.

Configurado para generar y almacenar trazas persistentes en el archivo artifacts/audit.log.

Registra de forma estandarizada el identificador del ticket (TICKET_ID), la acción ejecutada (ACCIÓN) y los detalles del evento con marcas de tiempo precisas (YYYY-MM-DD HH:MM:SS).

Motor de Reglas y Priorización (src/rules/prioritizer.py):

Desarrollado bajo un enfoque de sistemas expertos basados en reglas lógicas.

Evalúa variables clave del incidente como el Impacto (Alto, Medio, Bajo) y la Urgencia para determinar de manera automatizada la Prioridad de atención que requiere el soporte técnico.

Flujo Principal del Sistema (src/main.py):

Orquesta la ejecución inicial simulando la recepción de un ticket de soporte corporativo.

Conecta la entrada del problema con el módulo de auditoría para asegurar que cada paso quede documentado en los registros del sistema.

3. Integración y Trazabilidad de Eventos
El flujo implementado en esta semana garantiza que cualquier interacción o procesamiento dentro del asistente sea transparente y auditable. Los eventos clave registrados en los artefactos de la aplicación incluyen:

Recepción del Ticket: Captura inicial de la descripción del problema reportado por el usuario.

Aplicación de Reglas: Ejecución del motor de priorización para clasificar el nivel de atención.

Persistencia de Logs: Almacenamiento automático en la carpeta artifacts/ para su posterior revisión y auditoría técnica.

4. Conclusión y Resultados
La arquitectura base construida en la Semana 02 permitió estructurar modularmente el proyecto, facilitando la incorporación posterior de clasificadores inteligentes basados en taxonomías y aprendizaje automático durante la Semana 03.