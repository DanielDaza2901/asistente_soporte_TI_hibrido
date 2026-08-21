# Asistente de Soporte TI Híbrido

Sistema inteligente de soporte técnico diseñado para automatizar la clasificación de consultas, recuperar conocimiento técnico, aplicar reglas de negocio y priorizar incidentes garantizando trazabilidad completa.

##  Arquitectura del Sistema

El proyecto combina un enfoque modular y híbrido adaptado a las necesidades de soporte de software de PC corporativo:
- **Clasificador Taxonómico (Semana 03):** Categoriza automáticamente las incidencias corporativas en 7 áreas clave (PLN, Aprendizaje Predictivo, Optimización de PC, Sistemas Expertos, Automatización, Seguridad/Logs y Diagnóstico) considerando el impacto por departamento (Contabilidad, Recursos Humanos, Ventas, Logística, Gerencia, etc.).
- **Recuperador (RAG / Base de Conocimiento):** Busca soluciones y documentación técnica previa asociada a los errores reportados.
- **Motor de Reglas y Priorización (Semana 02):** Aplica políticas empresariales combinando Urgencia e Impacto para definir prioridades de atención.
- **Trazabilidad y Auditoría (Semana 02):** Registra cada acción, evento y cambio de estado en un sistema persistente estructurado (`artifacts/audit.log`).

## 🛠️ Stack Tecnológico
- **Python 3.13+** - Lenguaje base.
- **Scikit-learn** - Clasificación de texto mediante Machine Learning.
- **Pandas / NumPy** - Procesamiento y manejo de datos estructurados.
- **Pydantic** - Validación estricta de esquemas y tickets.

##  Instalación y Configuración

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/DanielDaza2901/asistente_soporte_ti.git](https://github.com/DanielDaza2901/asistente_soporte_ti.git)
   cd asistente_soporte_ti

##  Estructura del Proyecto

```text
asistente_soporte_ti/
├── artifacts/          # Logs de auditoría y trazas del sistema (audit.log)
├── data/               # Conjuntos de datos estructurados (casos_ia.csv)
├── notebooks/          # Notebooks de experimentación y análisis
├── reports/            # Informes automáticos y documentación de prácticas (Semana 02 y 03)
├── src/                # Código fuente principal
│   ├── audit/          # Módulo de trazabilidad y logging
│   ├── classifiers/    # Módulos de taxonomía e IA (semana03_taxonomia.py)
│   ├── knowledge/      # Base de conocimiento técnico
│   ├── rules/          # Motor de reglas y priorización
│   └── main.py         # Orquestador principal del flujo del asistente
├── tests/              # Pruebas unitarias e integración
├── README.md           # Documentación general del proyecto
└── requirements.txt    # Dependencias del entorno
