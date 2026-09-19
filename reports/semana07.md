# Reporte Semana 07: Representaciones del Reconocimiento

**Proyecto:** Asistente de Soporte TI Híbrido  
**Integrantes:** Marco Molina Molina & Daniel Eduardo Daza Cuello  
**Institución:** ETITC - 10º Semestre  

## Enlace al Repositorio
[https://github.com/DanielDaza2901/asistente_soporte_TI_hibrido](https://github.com/DanielDaza2901/asistente_soporte_TI_hibrido)

---


## 1. Aplicación al Proyecto (Adaptaciones realizadas)

En la Semana 07, el objetivo principal fue aplicar los conceptos de **Representaciones del Reconocimiento** (Numérica, Simbólica y Autómatas) para demostrar cómo un sistema inteligente debe transformar la realidad de una infraestructura de TI a distintos formalismos según la naturaleza del problema a resolver.

Alineados con el ecosistema de nuestro **Asistente de Soporte TI Híbrido** (que abarca desde la captura de métricas y automatización de procesos hasta la supervisión de redes y ciberdefensa), los ejemplos conceptuales se implementaron en tres dominios prácticos:

1. **Representación Numérica (Triaje de Tickets):** Se implementó un vector de características compuesto por *Impacto en Infraestructura (1-10)*, *Urgencia de Tiempo (1-10)* y *Sentimiento Negativo en NLP (0.0-1.0)*. Mediante el cálculo de la **Distancia Euclidiana** frente a un vector de referencia de *Escalamiento Inmediato*, el sistema clasifica de forma cuantitativa la criticidad del ticket para decidir si requiere atención humana prioritaria o manejo automatizado.
2. **Representación Simbólica (Diagnóstico y Enrutamiento):** Se diseñó un motor de inferencia basado en una base de hechos discretos extraídos de las solicitudes del usuario (ej. `pantalla_azul`, `reinicio_constante`, `codigo_stop`). Mediante reglas expertas booleanas de tipo *SI-ENTONCES*, el sistema deduce conclusiones diagnósticas precisas (como fallas físicas de hardware) y deriva el caso al módulo de campo correspondiente.
3. **Representación por Autómata (Reconocimiento de Patrones de Logs):** Se estructuró un Autómata Finito Determinista (AFD) para auditar cronologías y sucesos en los registros del sistema. Utilizando el alfabeto técnico **`O` (Operativo), `E` (Error) y `T` (Timeout)**, el autómata reconoce formalmente secuencias críticas como el patrón de **falla en cascada (`ET`)**, permitiendo alertar al NOC de manera temprana ante fallas de infraestructura complejas.

---

## 2. Tabla Comparativa de Representaciones

El siguiente cuadro analiza cómo cada enfoque procesa la información y detalla sus capacidades y limitaciones dentro del entorno de soporte técnico.

| Representación | Información que utiliza | Qué puede reconocer | Ventajas | Limitaciones | Información que puede perderse |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Numérica** | Arreglos matemáticos continuos (vectores multidimensionales de métricas de impacto y NLP). | Grados de proximidad, similitud matemática y tendencias estadísticas de criticidad. | Operaciones altamente optimizadas mediante álgebra lineal. Excelente para umbrales de triaje ambiguos. | Funciona como una "caja negra"; no explica de forma explícita el fallo técnico subyacente. | Se pierde el contexto semántico detallado del componente averiado y la relación de causa-efecto. |
| **Simbólica** | Hechos discretos explícitos, palabras clave y reglas lógicas booleanas estructuradas. | Causa y efecto directo; diagnósticos estructurados basados en síntomas técnicos exactos. | Alta interpretabilidad y auditabilidad. Facilita justificar formalmente por qué se sugirió una solución. | Rigidez analítica; si una combinación de síntomas no está mapeada en las reglas expertas, el sistema no puede inferir. | Los matices cuantitativos de escala (grados de urgencia numérica, métricas continuas de rendimiento). |
| **Autómata** | Secuencias temporales de eventos discretos en cronologías o estados (alfabeto formal `O, E, T`). | Patrones de comportamiento secuencial, bucles y fallas en cascada a lo largo del tiempo. | Excelente para modelar la evolución dinámica de un sistema y validar estados lógicos estrictos. | Dependencia de la completitud de las transiciones; eventos fuera del alfabeto son descartados. | Contexto estático del ticket; el autómata valida la secuencia de eventos pero ignora el detalle descriptivo de los datos. |

---

## 3. Conclusión de Integración

La práctica de la Semana 07 demuestra que en el desarrollo de un **Asistente Híbrido de Soporte TI** robusto, depender de una sola representación limitaría severamente las capacidades del Help Desk.

La integración de los tres enfoques potencia el sistema: la **lógica simbólica** diagnostica el error técnico a partir de los síntomas literales del usuario; los **modelos numéricos** miden la criticidad y proximidad a escenarios de alto riesgo mediante distancia euclidiana; y los **autómatas** supervisan la observabilidad y los flujos temporales de eventos (`O, E, T`), garantizando una respuesta integral, automatizada y confiable en los entornos SOC/NOC.