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

---

## B. Representación (Formalización)
* **Estado inicial:** Situación inicial del incidente (`(0, 0, 0)` donde los subsistemas de red, base de datos y aplicación presentan fallas o no han sido diagnosticados).
* **Estados posibles:** Tuplas de niveles de recuperación de los componentes del sistema corporativo.
* **Acciones u operadores:** Procedimientos técnicos permitidos (ej. reiniciar red, aplicar script SQL, desplegar hotfix).
* **Transiciones y sucesores:** Cambios de estado generados tras aplicar una acción correctiva de soporte.
* **Meta:** Estado objetivo en el cual todos los subsistemas se encuentran operativos y verificados (`(2, 2, 2)`).
* **Costo de camino ($g(n)$):** Tiempo estimado o esfuerzo operativo acumulado en minutos para aplicar las soluciones técnicas.
* **Heurística ($h(n)$):** Distancia de Manhattan estimada para alcanzar el estado operativo óptimo desde la configuración actual.

---

## C. Implementación
Se han creado e integrado los siguientes componentes en el repositorio acumulativo:
* `src/classifiers/astar.py`: Implementación del algoritmo $A$* para la planificación de secuencias de soporte técnico de costo mínimo.
* `src/classifiers/minimax.py`: Implementación del algoritmo Minimax para la selección de decisiones racionales en entornos competitivos o bajo restricciones.
* `src/main.py`: Orquestador centralizado que ejecuta la validación de modelos, el procesamiento de tickets con auditoría (`audit.log`) y los algoritmos de búsqueda inteligente de la Semana 4.

---

## D. Resultados
Al ejecutar `src/main.py` integrando los módulos de planificación, el sistema calcula con éxito la ruta de menor costo operativo:
* **Secuencia generada:** Reiniciar interfaces de red -> Aplicar script de recuperación en Base de Datos -> Desplegar hotfix en microservicio backend.
* **Costo total de camino:** Unidades de esfuerzo optimizadas mediante la función de prioridad de $A$*.
* **Evaluación Minimax:** Selección óptima de la posición estratégica (`6`) sobre el espacio de estados actual de recursos.

---

## E. Análisis y Discusión
* **Ventajas:** Permite automatizar la toma de decisiones técnicas complejas reduciendo el tiempo de respuesta del equipo de soporte y garantizando trazabilidad en la auditoría.
* **Limitaciones:** El espacio de estados puede crecer exponencialmente si se incrementan los microservicios analizados o la profundidad del árbol de búsqueda.
* **Supuestos:** Los costos de las acciones técnicas son deterministas y conocidos de antemano para el cálculo eficiente de la heurística.

---

## F. Pruebas y Casos de Validación
Para verificar el comportamiento y la robustez del planificador $A^*$, se evaluaron tres escenarios con diferentes configuraciones iniciales y restricciones de estado:

### Caso de Prueba 1: Incidente Estándar (Estado Inicial Base)
* **Entrada / Configuración Inicial:** Estado inicial `(0, 0, 0)` con meta en `(2, 2, 2)`.
* **Resultado Obtenido:** Secuencia óptima de 6 pasos (2 reinicios de red, 2 de base de datos y 2 de backend).
* **Costo Acumulado:** 12 unidades de esfuerzo operativo.
* **Explicación y Comparación:** El algoritmo evalúa el camino de menor costo desde cero cumpliendo con la ruta teórica esperada.

### Caso de Prueba 2: Condición Parcialmente Recuperada
* **Entrada / Configuración Inicial:** Estado inicial avanzado `(1, 1, 0)` con meta en `(2, 2, 2)`.
* **Resultado Obtenido:** Secuencia reducida a 3 pasos (1 script de BD y 2 hotfixes de backend).
* **Costo Acumulado:** 8 unidades de esfuerzo operativo.
* **Explicación y Comparación:** La solución cambia de manera coherente frente al Caso 1, omitiendo pasos innecesarios y reduciendo el costo total de 12 a 8.

### Caso de Prueba 3: Restricciones de Nivel Preexistentes
* **Entrada / Configuración Inicial:** Estado inicial con componentes mixtos `(0, 2, 1)` y meta en `(2, 2, 2)`.
* **Resultado Obtenido:** Secuencia enfocada de 3 pasos (2 reinicios de red y 1 hotfix de backend).
* **Costo Acumulado:** 5 unidades de esfuerzo operativo.
* **Explicación y Comparación:** Como la Base de Datos ya está en el nivel objetivo `(2)`, el planificador la ignora dinámicamente y optimiza el esfuerzo en los componentes restantes.

---
## G. Conclusiones
* **Efectividad de la Planificación Óptima:** La integración del algoritmo $A^*$ demostró ser altamente eficiente para automatizar la resolución de incidencias en soporte de TI, permitiendo calcular rutas de menor esfuerzo operativo y costos acumulados exactos bajo diferentes configuraciones de estado inicial.
* **Adaptabilidad ante Cambios de Entorno:** A través de las pruebas realizadas con estados iniciales modificados (parcialmente recuperados o con restricciones preexistentes), se comprobó que el planificador ajusta dinámicamente sus secuencias y reduce el esfuerzo de resolución de forma lógica y coherente.
* **Robustez del Sistema Híbrido:** La consolidación de los módulos de taxonomía, validación de modelos, trazabilidad de auditoría y algoritmos de búsqueda avanzada en un orquestador centralizado (`src/main.py`) garantiza una arquitectura escalable, auditable y alineada con los requerimientos de ingeniería de software e inteligencia artificial.