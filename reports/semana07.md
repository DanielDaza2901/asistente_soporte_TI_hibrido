# Reporte Semana 07: Representaciones del Reconocimiento

**Proyecto:** Asistente de Soporte TI Híbrido
**Integrantes:** Marco Molina Molina & Daniel Eduardo Daza Cuello
**Institución:** ETITC - 10º Semestre

## Enlace al Repositorio
[https://github.com/DanielDaza2901/asistente_soporte_TI_hibrido](https://github.com/DanielDaza2901/asistente_soporte_TI_hibrido)


## 1. Aplicación al Proyecto (Adaptaciones realizadas)

En la Semana 07, el objetivo fue aplicar los conceptos de Representaciones del Reconocimiento (Numérica, Simbólica y Autómatas) para demostrar cómo la Inteligencia Artificial debe "traducir" la realidad a distintos formatos según el tipo de problema a resolver.

Alineados con el enfoque de nuestro Asistente de Soporte TI, los ejemplos teóricos se han adaptado a los siguientes dominios prácticos de infraestructura y help desk:

*   **Representación Numérica:** Se implementó el cálculo de distancias (Norma Euclidiana) entre vectores de características técnicas (telemetría). El sistema compara el estado actual de los servidores (Uso de CPU %, Uso de RAM %, Latencia de Red ms) contra un "perfil crítico" predefinido para predecir colapsos inminentes basándose en proximidad matemática.
*   **Representación Simbólica:** Se diseñó un sistema experto basado en hechos discretos y reglas deterministas. A partir de los síntomas extraídos del lenguaje natural del ticket de soporte (ejemplo: `ping_fallido`, `servidor_no_responde`, `luces_rojas_switch`), se dispara una conclusión diagnóstica (caída masiva de red) mediante inferencia lógica directa (SI-ENTONCES).
*   **Representación por Autómata:** Se estructuró un Autómata Finito Determinista (AFD) para auditar secuencias de logs temporales (O: Operativo, E: Error, T: Timeout). Reconoce estrictamente si la cronología de eventos refleja un patrón de falla en cascada (finalización en ET) o si el sistema logró recuperarse.

--- 

## 2. Tabla Comparativa de Representaciones

El siguiente cuadro analiza cómo cada enfoque procesa la información y detalla sus capacidades y limitaciones dentro del entorno de soporte técnico.

| Representación | Información que utiliza | Qué puede reconocer | Ventajas | Limitaciones | Información que puede perderse |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Numérica** | Arreglos matemáticos continuos (vectores con métricas como telemetría, latencia, uso de RAM). | Grados de proximidad o similitud; tendencias estadísticas y agrupaciones de anomalías de rendimiento. | Operaciones altamente optimizadas (álgebra lineal). Excelente para clasificar datos inexactos o ruidosos mediante umbrales (distancias). | Es una "caja negra". No explica fácilmente por qué falló un servidor, solo indica numéricamente que se parece a un perfil de colapso. | Se pierde el contexto semántico del incidente, secuencias de eventos y la relación de causa-efecto. |
| **Simbólica** | Hechos discretos explícitos, palabras clave (ej. ping fallido) y reglas lógicas. | Causa y efecto directo; diagnósticos estructurados basados en condiciones exactas. | Altamente interpretable. Es fácil auditar por qué el sistema tomó una decisión (trazabilidad). | Rigidez. Si un síntoma no está mapeado exactamente en las reglas, el sistema falla (no maneja bien la ambigüedad). | Los matices de intensidad (qué tan lento está el servidor) o datos continuos. |
| **Autómatas** | Secuencias temporales de estados o eventos (ej. logs sucesivos O -> E -> T). | Patrones de comportamiento en el tiempo, fallas en cascada y flujos de procesos estructurados. | Perfecto para analizar la evolución temporal de un incidente y validar flujos estrictos (ej. protocolos de red). | Poca flexibilidad ante secuencias no previstas. Si el orden varía levemente, el autómata rechaza la cadena. | Contexto de por qué se pasó de un estado a otro; solo evalúa si el salto de estado es válido. |

---

## 3. Conclusión de Integración

La práctica de la Semana 07 demuestra que en el desarrollo de un **Asistente Híbrido** de Soporte TI real, depende de una sola representación limitaría severamente el alcance del análisis.

Las tres representaciones deben operar conjuntamente: el **autómata** y la **lógica simbólica** auditan la consistencia cronológica y determinista del ticket (proporcionando explicabilidad y justificación al ingeniero de soporte), mientras que los **modelos numéricos vectoriales** asumen la responsabilidad cuando se evalúan estadísticas de rendimiento y comparaciones complejas (RAM/CPU/TF-IDF)  que requieren cálculos de proximidad y tolerancia al ruido.




