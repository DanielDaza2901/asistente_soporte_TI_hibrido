# Reporte de Pruebas - Semana 05: Asistente de Soporte TI

Registro automatizado de ejecucion del sistema hibrido utilizando la base de conocimiento de 30 entradas.

## Prueba 1
- **Consulta:** `El equipo esta muy caliente y el ventilador hace ruido`
- **Reglas Activadas:** `diagnostico_hardware_temperatura`
- **Evidencia (Base de Conocimiento):** 1. Equipo caliente -> revisar ventilación y limpiar ventilador; verificar piezas visibles; ajustar tornillería; aplicar lubricante a partes móviles
- **Similitud Coseno:** `0.4714`
- **Clase Predicha:** `hardware`

## Prueba 2
- **Consulta:** `La conexion de internet cae constantemente y falla el enlace`
- **Reglas Activadas:** `diagnostico_conectividad_red`
- **Evidencia (Base de Conocimiento):** 2. Internet cae -> revisar DNS y enlace de red; comprobar configuración del router; reiniciar modem; verificar cableado
- **Similitud Coseno:** `0.5652`
- **Clase Predicha:** `seguridad`

## Prueba 3
- **Consulta:** `El disco duro esta lleno y la aplicacion esta muy lenta`
- **Reglas Activadas:** `optimizacion_recursos_sistema, gestion_almacenamiento`
- **Evidencia (Base de Conocimiento):** 12. Disco lleno -> liberar espacio; eliminar archivos temporales; ampliar almacenamiento con disco externo
- **Similitud Coseno:** `0.3316`
- **Clase Predicha:** `seguridad`

---

* **Integración del Módulo Híbrido (`sistema_hibrido.py`):** Se desarrolló y estructuró el componente central encargado de unificar los motores lógicos y estadísticos dentro de la jerarquía del proyecto (`src/classifiers/`), permitiendo su ejecución automatizada y centralizada desde el script principal (`src/main.py`).
* **Conexión con la Base de Conocimiento:** Se implementó la carga dinámica del repositorio documental almacenado en `data/base_conocimiento.txt`, extrayendo las guías técnicas estandarizadas para el diagnóstico de incidentes.
* **Vectorización y Similitud Coseno:** Se aplicó el modelo **TF-IDF** (*Term Frequency-Inverse Document Frequency*) en conjunto con la **Similitud Coseno** de `scikit-learn` para comparar las consultas de los usuarios con la base de conocimiento y extraer la evidencia documental más relevante.
* **Clasificación Automática de Texto:** Se integró un clasificador basado en regresión logística entrenado con un pipeline de características textuales para categorizar de manera predictiva los incidentes reportados (hardware, red, rendimiento, seguridad, etc.).
* **Trazabilidad y Auditoría:** Se vinculó la ejecución del sistema híbrido al sistema de registros mediante la función `registrar_traza`, asegurando el monitoreo continuo en el archivo de auditoría (`artifacts/audit.log`).

---
# Tabla de distribución por categorías
 
| **Categoría** | **Situación / Casos Registrados** | **Acción Recomendada / Evidencia** |
|---------------|-----------------------------------|------------------------------------|
| **Hardware**  | Equipo caliente / ventilador ruidoso | Revisar ventilación y limpiar ventilador; verificar piezas visibles; ajustar tornillería; aplicar lubricante a partes móviles |
|               | Sistema no enciende o placa base falla | Verificar fuente de poder; revisar conexiones internas de cables; inspeccionar condensadores de la placa base |
|               | Pantalla azul en sistema operativo | Actualizar controladores de video y chipset; ejecutar diagnóstico de memoria RAM; verificar integridad del sistema |
|               | Fallas físicas en disco duro | Ejecutar comando chkdsk; verificar sectores defectuosos; respaldar información crítica de inmediato |
|               | Periféricos y componentes adicionales | Revisar conexión de puertos USB; cambiar cables de datos; reinstalar drivers específicos del fabricante |
| **Red**       | Conexión de internet intermitente | Revisar DNS y enlace de red; comprobar configuración del router; reiniciar módem; verificar cableado estructurado |
|               | Falla total de conectividad local | Comprobar direccionamiento IP estático/DHCP; verificar estado del switch; probar conectividad con ping al gateway |
|               | Interferencia en red Wi-Fi | Cambiar canal de transmisión inalámbrica; acercar el equipo al punto de acceso; actualizar firmware del router |
| **Seguridad** | Alerta de virus o troyano detectado | Ejecutar análisis completo con antivirus corporativo; aislar el equipo de la red; poner en cuarentena archivos maliciosos |
|               | Intento de acceso no autorizado | Revisar registros de eventos de seguridad (Security logs); bloquear direcciones IP sospechosas; cambiar credenciales |
|               | Compromiso de credenciales de usuario | Forzar cambio inmediato de contraseña; revocar sesiones activas; verificar políticas de complejidad de claves |
| **Rendimiento** | Aplicación lenta y alto consumo de memoria | Monitorear procesos en el Administrador de tareas; finalizar procesos consumidores de recursos; ampliar memoria RAM si es necesario |
|               | Procesador (CPU) al 100% de uso | Identificar procesos colgados o bucles infinitos; optimizar servicios de inicio; aplicar parches del sistema operativo |
| **Almacenamiento** | Disco lleno y falta de espacio libre | Liberar espacio eliminando archivos temporales y caché; vaciar papelera de reciclaje; migrar datos a almacenamiento externo o en la nube |
| **Software**  | Error crítico en aplicación de negocio | Revisar trazas de error (logs de aplicación); aplicar hotfix o parche correctivo; reinstalar dependencias del sistema |

---
## 3. Conclusiones Técnicas

1. **Robustez del Enfoque Híbrido:** La integración de reglas deterministas (basadas en conocimiento experto) junto con modelos probabilísticos y de aprendizaje automático (TF-IDF y Regresión Logística) permite mitigar las limitaciones individuales de cada enfoque. Las reglas aseguran respuestas críticas predecibles, mientras que la recuperación de documentos basada en similitud vectorial aporta flexibilidad ante variaciones en el lenguaje natural del usuario.
2. **Eficiencia en la Recuperación Documental:** El uso de métricas de distancia vectorial sobre el corpus de conocimiento permitió automatizar la búsqueda de manuales de solución de forma rápida y precisa, reduciendo los tiempos de diagnóstico en el primer nivel de atención de soporte TI.
3. **Escalabilidad de la Arquitectura:** La modularización del código —separando la lógica de negocio y clasificación en `src/classifiers/` y centralizando la ejecución secuencial en `src/main.py`— garantiza que el sistema sea altamente extensible para incorporar nuevas semanas de desarrollo, algoritmos de optimización o bases de datos relacionales en futuras fases del proyecto.

---

## Integrantes del Proyecto
* **Marco Molina Molina**
* **Daniel Eduardo Daza Cuello**
* **Institución / Curso:** ETITC - 10º Semestre

## Enlace al Repositorio
[https://github.com/DanielDaza2901/asistente_soporte_TI_hibrido](https://github.com/DanielDaza2901/asistente_soporte_TI_hibrido)

---

