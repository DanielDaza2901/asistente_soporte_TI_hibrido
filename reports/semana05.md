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

----

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

----

### Conclusiones:
### 1.Funcionamiento del enfoque híbrido:
Combinar reglas lógicas con un sistema de búsqueda basado en texto nos permitió aprovechar lo mejor de ambos mundos. Por un lado, las reglas aseguran que las alertas críticas sean detectadas con precisión, y por otro, la similitud de texto encuentra soluciones parecidas en nuestra base de datos cuando el usuario describe un problema de forma libre.

### 2. Crecimiento y orden en la base de conocimiento:
Al estructurar las 30 entradas técnicas en el archivo de texto, logramos que el asistente tenga una fuente de referencia mucho más amplia y organizada para soporte de hardware y redes. Esto, acompañado del registro de auditoría, hace que sea muy fácil revisar el historial de lo que el sistema va diagnosticando paso a paso.

### 3. Evolución global del proyecto:
Completar esta quinta semana nos ayudó a amarrar todas las piezas que veníamos trabajando desde las fases pasadas (como la taxonomía, el planificador y el juego de estrategia) en una sola herramienta funcional. Ver todo esto integrado en el panel interactivo demuestra el avance real que hemos logrado en el desarrollo del asistente.

## Integrantes del Proyecto
* **Marco Molina Molina**
* **Daniel Eduardo Daza Cuello**
* **Institución / Curso:** ETITC - 10º Semestre

## Enlace al Repositorio
https://github.com/DanielDaza2901/asistente_soporte_TI_hibrido.git
https://github.com/MarcoMolina2011/asistente_soporte_TI_hibrido

