# Reporte de Pruebas - Semana 05: Asistente de Soporte TI

## Integrantes del Proyecto
* **Marco Molina Molina**
* **Daniel Eduardo Daza Cuello**
* **Institución / Curso:** ETITC - 10º Semestre

## Enlace al Repositorio
[https://github.com/DanielDaza2901/asistente_soporte_TI_hibrido](https://github.com/DanielDaza2901/asistente_soporte_TI_hibrido)

---

Registro automatizado de ejecución del sistema híbrido utilizando la base de conocimiento de 30 entradas.

## Prueba 1
- **Consulta:** `El equipo esta muy caliente y el ventilador hace ruido`
- **Reglas Activadas:** `diagnostico_hardware_temperatura`
- **Evidencia (Base de Conocimiento):** Equipo caliente -> revisar ventilación y limpiar ventilador; verificar piezas visibles; ajustar tornillería; aplicar lubricante a partes móviles
- **Similitud Coseno:** `0.4714`
- **Clase Predicha:** `hardware`

## Prueba 2
- **Consulta:** `La conexion de internet cae constantemente y falla el enlace`
- **Reglas Activadas:** `diagnostico_conectividad_red`
- **Evidencia (Base de Conocimiento):** Internet cae -> revisar DNS y enlace de red; comprobar configuración del router; reiniciar modem; verificar cableado
- **Similitud Coseno:** `0.5652`
- **Clase Predicha:** `red`

## Prueba 3
- **Consulta:** `El disco duro esta lleno y la aplicacion esta muy lenta`
- **Reglas Activadas:** `optimizacion_recursos_sistema, gestion_almacenamiento`
- **Evidencia (Base de Conocimiento):** Disco lleno -> liberar espacio; eliminar archivos temporales; ampliar almacenamiento con disco externo
- **Similitud Coseno:** `0.3467`
- **Clase Predicha:** `rendimiento`

---

# Tabla de distribución por categorías de la Base de Conocimiento

| **Categoría** | **Situación / Casos Registrados** | **Acción Recomendada / Evidencia** |
|---|---|---|
| **Hardware** | Equipo caliente / ventilador ruidoso | Revisar ventilación y limpiar ventilador; verificar piezas visibles; lubricar partes móviles |
| | Sistema no enciende o placa base falla | Verificar fuente de poder; revisar conexiones de cables; inspeccionar condensadores |
| | Pantalla azul en sistema operativo | Actualizar controladores de video y chipset; ejecutar diagnóstico de RAM |
| | Fallas físicas en disco duro | Ejecutar comando chkdsk; verificar sectores defectuosos; respaldar información |
| | Periféricos y componentes adicionales | Revisar puertos USB; cambiar cables de datos; reinstalar drivers |
| **Red** | Conexión de internet intermitente | Revisar DNS y enlace de red; comprobar router; reiniciar módem; verificar cableado |
| | Falla total de conectividad local | Comprobar IP estático/DHCP; verificar estado de switch; probar ping al gateway |
| | Interferencia en red Wi-Fi | Cambiar canal inalámbrico; acercar al punto de acceso; actualizar firmware |
| **Seguridad** | Alerta de virus o troyano detectado | Ejecutar análisis completo; aislar el equipo; poner en cuarentena archivos |
| | Intento de acceso no autorizado | Revisar registros de eventos de seguridad; bloquear direcciones IP sospechosas |
| | Compromiso de credenciales de usuario | Forzar cambio inmediato de contraseña; revocar sesiones activas |
| **Rendimiento** | Aplicación lenta y alto consumo de memoria | Monitorear procesos en Administrador de tareas; finalizar procesos pesados |
| | Procesador (CPU) al 100% de uso | Identificar procesos en bucle; optimizar inicio; aplicar parches del SO |
| **Almacenamiento** | Disco lleno y falta de espacio libre | Liberar espacio eliminando temporales y caché; vaciar papelera; migrar datos |
| **Software** | Error crítico en aplicación o spooler | Revisar logs de aplicación; reiniciar servicio spooler; reinstalar drivers |

---

### Conclusiones:

#### 1. Funcionamiento del enfoque híbrido:
Combinar reglas lógicas con un sistema de búsqueda basado en texto permite aprovechar lo mejor de ambos mundos. Por un lado, las reglas aseguran que las alertas críticas sean detectadas con precisión determinista, y por otro, la similitud coseno recupera el procedimiento técnico más afín cuando el usuario describe un problema en lenguaje natural libre.

#### 2. Crecimiento y orden en la base de conocimiento:
Al estructurar las 30 entradas técnicas en el archivo `data/base_conocimiento.txt`, el asistente cuenta con una fuente de referencia amplia y organizada para soporte de hardware, red, seguridad, rendimiento y almacenamiento. Esto, junto con el registro en `artifacts/audit.log`, garantiza trazabilidad de extremo a extremo.

#### 3. Evolución global del proyecto:
La integración de la taxonomía (Semana 03), el planificador $A^*$ (Semana 04) y el sistema híbrido con TF-IDF (Semana 05) en un panel interactivo (`dashboard.py`) demuestra un avance técnico sólido para la entrega del Corte 1.