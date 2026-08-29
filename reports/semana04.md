# Informe de la Semana 04: Marco Tecnológico de la Inteligencia Artificial

## Integrantes del Proyecto
* **Marco Molina Molina**
* **Daniel Eduardo Daza Cuello**
* **Institución / Curso:** ETITC - 10º Semestre

## Enlace al Repositorio
[https://github.com/DanielDaza2901/asistente_soporte_TI_hibrido](https://github.com/DanielDaza2901/asistente_soporte_TI_hibrido)

---
## A. Descripción del problema
En el sistema de **Asistente de Soporte TI**, la resolución eficiente de incidencias críticas requiere determinar la secuencia óptima de acciones correctivas (como reinicios de red, optimización de base de datos o despliegue de hotfixes) para minimizar el tiempo de inactividad del sistema. Asimismo, se evalúan escenarios donde intervienen restricciones del entorno o decisiones adversariales de recursos.

## B. Representación (Formalización)
* **Estado inicial:** Situación inicial del incidente (`(0, 0, 0)` donde los subsistemas de red, base de datos y aplicación presentan fallas o no han sido diagnosticados).
* **Estados posibles:** Tuplas de niveles de recuperación de los componentes del sistema corporativo.
* **Acciones u operadores:** Procedimientos técnicos permitidos (ej. reiniciar red, aplicar script SQL, desplegar hotfix).
* **Transiciones y sucesores:** Cambios de estado generados tras aplicar una acción correctiva de soporte.
* **Meta:** Estado objetivo en el cual todos los subsistemas se encuentran operativos y verificados (`(2, 2, 2)`).
* **Costo de camino ($g(n)$):** Tiempo estimado o esfuerzo operativo acumulado en minutos para aplicar las soluciones técnicas.
* **Heurística ($h(n)$):** Distancia de Manhattan estimada para alcanzar el estado operativo óptimo desde la configuración actual.

## C. Implementación
Se han creado e integrado los siguientes componentes en el repositorio acumulativo:
* `src/classifiers/astar.py`: Implementación del algoritmo $A$* para la planificación de secuencias de soporte técnico de costo mínimo.
* `src/classifiers/minimax.py`: Implementación del algoritmo Minimax para la selección de decisiones racionales en entornos competitivos o bajo restricciones.
* `src/main.py`: Orquestador centralizado que ejecuta la validación de modelos, el procesamiento de tickets con auditoría (`audit.log`) y los algoritmos de búsqueda inteligente de la Semana 4.

## D. Resultados
Al ejecutar `src/main.py` integrando los módulos de planificación, el sistema calcula con éxito la ruta de menor costo operativo:
* **Secuencia generada:** Reiniciar interfaces de red -> Aplicar script de recuperación en Base de Datos -> Desplegar hotfix en microservicio backend.
* **Costo total de camino:** Unidades de esfuerzo optimizadas mediante la función de prioridad de $A$*.
* **Evaluación Minimax:** Selección óptima de la posición estratégica (`6`) sobre el espacio de estados actual de recursos.

## E. Análisis y Discusión
* **Ventajas:** Permite automatizar la toma de decisiones técnicas complejas reduciendo el tiempo de respuesta del equipo de soporte y garantizando trazabilidad en la auditoría.
* **Limitaciones:** El espacio de estados puede crecer exponencialmente si se incrementan los microservicios analizados o la profundidad del árbol de búsqueda.
* **Supuestos:** Los costos de las acciones técnicas son deterministas y conocidos de antemano para el cálculo eficiente de la heurística.