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
