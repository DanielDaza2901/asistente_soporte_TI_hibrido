"""
Base de conocimiento empresarial del Asistente de Soporte TI Híbrido (Semana 15).

Organiza el conocimiento del proyecto en SQLite con cinco tablas relacionadas:

    dominio ──< aplicacion          cada aplicación pertenece a un dominio
    dominio ──< experto             cada experto tiene un dominio de especialidad
    articulo >── dominio, aplicacion, experto, herramienta (opcional)

Flujo de un artículo:   registrar  ->  BORRADOR  ->  validar  ->  VALIDADO (visible)

Reglas que se garantizan en DOS niveles: en Python (mensajes claros) y en la propia
base de datos (restricciones CHECK, claves foráneas y disparadores en sql/esquema.sql).
"""
import sqlite3
from contextlib import contextmanager
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
DIR_SQL = RAIZ / "sql"
RUTA_DB = RAIZ / "artifacts" / "base_conocimiento.db"

BORRADOR = "BORRADOR"
VALIDADO = "VALIDADO"
TABLAS = ("dominio", "aplicacion", "experto", "herramienta", "articulo")
_CLAVES = {"dominio": "id_dominio", "aplicacion": "id_aplicacion", "experto": "id_experto",
           "herramienta": "id_herramienta", "articulo": "id_articulo"}

# Consulta base con SQL JOIN: relaciona artículo, dominio, aplicación, experto y herramienta.
SQL_ARTICULOS = """
SELECT a.id_articulo, a.titulo, a.contenido, a.estado, a.fuente,
       a.fecha_registro, a.fecha_validacion,
       d.id_dominio, d.nombre AS dominio,
       ap.nombre AS aplicacion, ap.modulo AS modulo,
       e.nombre AS experto, e.cargo AS cargo_experto,
       h.nombre AS herramienta
  FROM articulo a
  JOIN dominio d          ON d.id_dominio = a.id_dominio
  JOIN aplicacion ap      ON ap.id_aplicacion = a.id_aplicacion
  JOIN experto e          ON e.id_experto = a.id_experto
  LEFT JOIN herramienta h ON h.id_herramienta = a.id_herramienta
"""


# ----------------------------------------------------------------------------- errores
class BaseConocimientoError(Exception):
    """Error general de la base de conocimiento."""


class DatosInvalidosError(BaseConocimientoError):
    """Los datos no cumplen las reglas (texto vacío o corto, duplicado, dominio incoherente...)."""


class ReferenciaInexistenteError(BaseConocimientoError):
    """Se hace referencia a un dominio, aplicación, experto o herramienta que no existe."""


class ArticuloNoEncontradoError(BaseConocimientoError):
    """El artículo indicado no existe."""


class EstadoInvalidoError(BaseConocimientoError):
    """La operación no es válida para el estado actual del artículo."""


def _texto(valor, nombre, minimo):
    if not isinstance(valor, str) or len(valor.strip()) < minimo:
        raise DatosInvalidosError(f"El campo «{nombre}» debe ser un texto de al menos {minimo} caracteres.")
    return valor.strip()


def _entero(valor, nombre):
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise DatosInvalidosError(f"El identificador de «{nombre}» debe ser un número entero.")
    return valor


def _traducir_integridad(error):
    mensaje = str(error)
    if "UNIQUE" in mensaje:
        return "Ya existe un registro con ese valor único (por ejemplo, el mismo título para la misma aplicación)."
    if "FOREIGN KEY" in mensaje:
        return "La referencia indicada no existe o el registro está en uso."
    if "CHECK" in mensaje:
        return "Los datos no cumplen las restricciones de la base de datos."
    return mensaje


# ----------------------------------------------------------------------------- clase principal
class BaseConocimiento:
    """Acceso a la base de conocimiento. Cada operación abre y cierra su propia conexión."""

    def __init__(self, ruta_db=None, dir_sql=None):
        self.ruta_db = Path(ruta_db) if ruta_db else RUTA_DB
        self.dir_sql = Path(dir_sql) if dir_sql else DIR_SQL

    @contextmanager
    def _conexion(self):
        con = sqlite3.connect(self.ruta_db)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON")   # SQLite no aplica las claves foráneas sin esto
        try:
            with con:                              # confirma si todo sale bien; revierte si hay error
                yield con
        finally:
            con.close()

    # ------------------------------------------------------------------ creación
    def crear_esquema(self, con_datos=True, reiniciar=False):
        """Crea las tablas con sql/esquema.sql y, si se pide, carga sql/datos.sql."""
        esquema, datos = self.dir_sql / "esquema.sql", self.dir_sql / "datos.sql"
        for archivo in (esquema, datos if con_datos else esquema):
            if not archivo.exists():
                raise BaseConocimientoError(f"No se encontró el archivo SQL: {archivo}")
        self.ruta_db.parent.mkdir(parents=True, exist_ok=True)
        if reiniciar and self.ruta_db.exists():
            self.ruta_db.unlink()
        con = sqlite3.connect(self.ruta_db)
        try:
            con.executescript(esquema.read_text(encoding="utf-8"))
            if con_datos:
                con.executescript(datos.read_text(encoding="utf-8"))
            con.commit()
        except sqlite3.Error as error:
            raise BaseConocimientoError(f"No se pudo crear la base de datos: {error}") from error
        finally:
            con.close()

    def existe_base(self):
        """True si el archivo existe y contiene las cinco tablas."""
        if not self.ruta_db.exists():
            return False
        try:
            with self._conexion() as con:
                nombres = {f[0] for f in con.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
        except sqlite3.Error:
            return False
        return set(TABLAS) <= nombres

    # ------------------------------------------------------------------ catálogos
    def listar_dominios(self):
        with self._conexion() as con:
            return [dict(f) for f in con.execute("SELECT * FROM dominio ORDER BY nombre")]

    def listar_aplicaciones(self, id_dominio=None):
        sql, par = "SELECT * FROM aplicacion", ()
        if id_dominio is not None:
            sql, par = sql + " WHERE id_dominio = ?", (id_dominio,)
        with self._conexion() as con:
            return [dict(f) for f in con.execute(sql + " ORDER BY nombre", par)]

    def listar_expertos(self):
        with self._conexion() as con:
            return [dict(f) for f in con.execute(
                "SELECT e.*, d.nombre AS dominio FROM experto e JOIN dominio d ON d.id_dominio = e.id_dominio ORDER BY e.nombre")]

    def listar_herramientas(self):
        with self._conexion() as con:
            return [dict(f) for f in con.execute("SELECT * FROM herramienta ORDER BY nombre")]

    def obtener_id(self, tabla, nombre):
        """Identificador de un registro a partir de su nombre (sin distinguir mayúsculas)."""
        if tabla not in _CLAVES:
            raise DatosInvalidosError(f"Tabla desconocida: {tabla}")
        columna = "titulo" if tabla == "articulo" else "nombre"
        with self._conexion() as con:
            fila = con.execute(f"SELECT {_CLAVES[tabla]} FROM {tabla} WHERE {columna} = ? COLLATE NOCASE", (nombre,)).fetchone()
        if fila is None:
            raise ReferenciaInexistenteError(f"No existe {tabla} con el nombre «{nombre}».")
        return fila[0]

    def resumen(self):
        """Cantidad de filas por tabla y de artículos por estado."""
        with self._conexion() as con:
            datos = {t: con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in TABLAS}
            for clave, estado in (("validados", VALIDADO), ("borradores", BORRADOR)):
                datos[clave] = con.execute("SELECT COUNT(*) FROM articulo WHERE estado = ?", (estado,)).fetchone()[0]
        return datos

    def contar_por_dominio(self):
        """Artículos validados y borradores por dominio (JOIN con agregación)."""
        sql = """SELECT d.nombre AS dominio,
                        SUM(CASE WHEN a.estado = 'VALIDADO' THEN 1 ELSE 0 END) AS validados,
                        SUM(CASE WHEN a.estado = 'BORRADOR' THEN 1 ELSE 0 END) AS borradores
                   FROM dominio d LEFT JOIN articulo a ON a.id_dominio = d.id_dominio
                  GROUP BY d.id_dominio ORDER BY d.nombre"""
        with self._conexion() as con:
            return [{"dominio": f["dominio"], "validados": f["validados"] or 0, "borradores": f["borradores"] or 0}
                    for f in con.execute(sql)]

    # ------------------------------------------------------------------ registro y validación
    @staticmethod
    def _exigir(con, tabla, valor, etiqueta):
        if con.execute(f"SELECT 1 FROM {tabla} WHERE {_CLAVES[tabla]} = ?", (valor,)).fetchone() is None:
            raise ReferenciaInexistenteError(f"No existe {etiqueta} con id {valor}.")

    def registrar_articulo(self, titulo, contenido, id_dominio, id_aplicacion, id_experto, fuente, id_herramienta=None):
        """Registra un artículo nuevo. SIEMPRE nace como BORRADOR. Devuelve su id."""
        titulo, contenido, fuente = _texto(titulo, "título", 5), _texto(contenido, "contenido", 20), _texto(fuente, "fuente", 3)
        _entero(id_dominio, "dominio"), _entero(id_aplicacion, "aplicación"), _entero(id_experto, "experto")
        if id_herramienta is not None:
            _entero(id_herramienta, "herramienta")
        with self._conexion() as con:
            self._exigir(con, "dominio", id_dominio, "el dominio")
            self._exigir(con, "aplicacion", id_aplicacion, "la aplicación")
            self._exigir(con, "experto", id_experto, "el experto")
            if id_herramienta is not None:
                self._exigir(con, "herramienta", id_herramienta, "la herramienta")
            app = con.execute("SELECT nombre, id_dominio FROM aplicacion WHERE id_aplicacion = ?", (id_aplicacion,)).fetchone()
            if app["id_dominio"] != id_dominio:
                raise DatosInvalidosError(f"La aplicación «{app['nombre']}» no pertenece al dominio indicado.")
            try:
                cur = con.execute(
                    "INSERT INTO articulo (titulo, contenido, id_dominio, id_aplicacion, id_experto, id_herramienta, fuente) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (titulo, contenido, id_dominio, id_aplicacion, id_experto, id_herramienta, fuente))
            except sqlite3.IntegrityError as error:
                raise DatosInvalidosError(_traducir_integridad(error)) from error
            return cur.lastrowid

    def validar_articulo(self, id_articulo):
        """Pasa un artículo de BORRADOR a VALIDADO y registra la fecha de validación."""
        _entero(id_articulo, "artículo")
        with self._conexion() as con:
            fila = con.execute("SELECT estado FROM articulo WHERE id_articulo = ?", (id_articulo,)).fetchone()
            if fila is None:
                raise ArticuloNoEncontradoError(f"No existe el artículo con id {id_articulo}.")
            if fila["estado"] == VALIDADO:
                raise EstadoInvalidoError(f"El artículo {id_articulo} ya está VALIDADO.")
            con.execute("UPDATE articulo SET estado = 'VALIDADO', fecha_validacion = datetime('now', 'localtime') "
                        "WHERE id_articulo = ? AND estado = 'BORRADOR'", (id_articulo,))

    # ------------------------------------------------------------------ consultas
    def obtener_articulo(self, id_articulo):
        """Un artículo en cualquier estado (uso interno de revisión)."""
        with self._conexion() as con:
            fila = con.execute(SQL_ARTICULOS + " WHERE a.id_articulo = ?", (id_articulo,)).fetchone()
        if fila is None:
            raise ArticuloNoEncontradoError(f"No existe el artículo con id {id_articulo}.")
        return dict(fila)

    def _resolver_dominio(self, con, dominio):
        if isinstance(dominio, int) and not isinstance(dominio, bool):
            self._exigir(con, "dominio", dominio, "el dominio")
            return dominio
        if isinstance(dominio, str):
            fila = con.execute("SELECT id_dominio FROM dominio WHERE nombre = ? COLLATE NOCASE", (dominio.strip(),)).fetchone()
            if fila is None:
                raise ReferenciaInexistenteError(f"No existe el dominio «{dominio}».")
            return fila[0]
        raise DatosInvalidosError("El dominio debe indicarse por su id o por su nombre.")

    def consultar_por_dominio(self, dominio, incluir_borradores=False):
        """Artículos de un dominio. Por defecto SOLO los VALIDADO (consulta habitual)."""
        with self._conexion() as con:
            id_dominio = self._resolver_dominio(con, dominio)
            sql = SQL_ARTICULOS + " WHERE a.id_dominio = ?"
            if not incluir_borradores:
                sql += " AND a.estado = 'VALIDADO'"
            return [dict(f) for f in con.execute(sql + " ORDER BY a.titulo", (id_dominio,))]

    def listar_publicados(self):
        """Todos los artículos VALIDADO de todos los dominios."""
        with self._conexion() as con:
            return [dict(f) for f in con.execute(SQL_ARTICULOS + " WHERE a.estado = 'VALIDADO' ORDER BY d.nombre, a.titulo")]

    def listar_borradores(self):
        """Cola de revisión: artículos BORRADOR pendientes de validar."""
        with self._conexion() as con:
            return [dict(f) for f in con.execute(SQL_ARTICULOS + " WHERE a.estado = 'BORRADOR' ORDER BY a.fecha_registro, a.id_articulo")]

    def buscar_publicados(self, texto, dominio=None):
        """Busca texto en título y contenido, solo entre los artículos VALIDADO."""
        texto = _texto(texto, "texto de búsqueda", 2)
        patron = f"%{texto}%"
        with self._conexion() as con:
            sql, par = SQL_ARTICULOS + " WHERE a.estado = 'VALIDADO' AND (a.titulo LIKE ? OR a.contenido LIKE ?)", [patron, patron]
            if dominio is not None:
                sql += " AND a.id_dominio = ?"
                par.append(self._resolver_dominio(con, dominio))
            return [dict(f) for f in con.execute(sql + " ORDER BY a.titulo", par)]


# ----------------------------------------------------------------------------- demostración
TITULO_DEMO = "Registro de oraciones en la red semántica"
CONTENIDO_DEMO = ("interpretar_oracion convierte oraciones como «A es un B» o «A requiere B» en triples y los almacena "
                  "en la red; las oraciones fuera de esos formatos lanzan ValueError sin modificar la red.")


def ejecutar_demostracion(ruta_db=None, dir_sql=None):
    """Ejecuta el flujo exigido en la sustentación sobre una base nueva y devuelve los pasos."""
    bc = BaseConocimiento(ruta_db, dir_sql)
    pasos = []

    def paso(titulo, lineas, ok=True):
        pasos.append({"id": str(len(pasos) + 1), "titulo": titulo, "lineas": lineas, "ok": bool(ok)})

    bc.crear_esquema(con_datos=True, reiniciar=True)
    r = bc.resumen()
    paso("Base creada con sql/esquema.sql y sql/datos.sql",
         [f"Tablas: dominio={r['dominio']}, aplicacion={r['aplicacion']}, experto={r['experto']}, "
          f"herramienta={r['herramienta']}, articulo={r['articulo']}",
          f"Artículos de ejemplo: {r['validados']} VALIDADO y {r['borradores']} BORRADOR"])

    id_dom = bc.obtener_id("dominio", "Razonamiento simbólico")
    id_app = bc.obtener_id("aplicacion", "Red semántica de soporte TI")
    id_exp = bc.obtener_id("experto", "Carlos Rojas")
    id_her = bc.obtener_id("herramienta", "Python")
    nuevo = bc.registrar_articulo(TITULO_DEMO, CONTENIDO_DEMO, id_dom, id_app, id_exp, "src/classifiers/red_semantica.py", id_her)
    art = bc.obtener_articulo(nuevo)
    paso("Registrar un artículo nuevo",
         [f"Título: {art['titulo']}", f"Dominio: {art['dominio']} | Aplicación: {art['aplicacion']}",
          f"Experto: {art['experto']} | Fuente: {art['fuente']}", f"Estado inicial: {art['estado']}"],
         ok=art["estado"] == BORRADOR)

    visibles = [a["titulo"] for a in bc.consultar_por_dominio("Razonamiento simbólico")]
    paso("Consulta habitual por dominio (solo VALIDADO): el borrador NO aparece",
         [f"Artículos visibles en «Razonamiento simbólico»: {len(visibles)}",
          f"¿Aparece el borrador «{TITULO_DEMO}»? {'SÍ' if TITULO_DEMO in visibles else 'NO'}"],
         ok=TITULO_DEMO not in visibles)

    bc.validar_articulo(nuevo)
    art = bc.obtener_articulo(nuevo)
    paso("Validar el artículo", [f"Estado actual: {art['estado']} (validado el {art['fecha_validacion']})"],
         ok=art["estado"] == VALIDADO)

    visibles = [a["titulo"] for a in bc.consultar_por_dominio("Razonamiento simbólico")]
    paso("Consulta por dominio después de validar: el artículo SÍ aparece",
         [f"Artículos visibles en «Razonamiento simbólico»: {len(visibles)}",
          f"¿Aparece «{TITULO_DEMO}»? {'SÍ' if TITULO_DEMO in visibles else 'NO'}"],
         ok=TITULO_DEMO in visibles)

    fila = next(a for a in bc.consultar_por_dominio(id_dom) if a["id_articulo"] == nuevo)
    paso("Consulta con SQL JOIN (artículo + dominio + aplicación + experto + herramienta)",
         [f"{fila['titulo']} | {fila['dominio']} | {fila['aplicacion']} | {fila['experto']} | {fila['herramienta']}"])

    lineas, todo_ok = [], True
    for etiqueta, llamada in (
            ("Dominio inexistente", lambda: bc.registrar_articulo(TITULO_DEMO + " 2", CONTENIDO_DEMO, 9999, id_app, id_exp, "fuente")),
            ("Experto inexistente", lambda: bc.registrar_articulo(TITULO_DEMO + " 3", CONTENIDO_DEMO, id_dom, id_app, 9999, "fuente"))):
        try:
            llamada()
            lineas.append(f"{etiqueta}: NO se rechazó (error)")
            todo_ok = False
        except ReferenciaInexistenteError as error:
            lineas.append(f"{etiqueta}: rechazado -> {error}")
    try:
        with bc._conexion() as con:
            con.execute("INSERT INTO articulo (titulo, contenido, id_dominio, id_aplicacion, id_experto, fuente, estado, fecha_validacion) "
                        "VALUES ('Intento directo', 'Contenido de prueba suficientemente largo', ?, ?, ?, 'fuente', 'VALIDADO', datetime('now'))",
                        (id_dom, id_app, id_exp))
        lineas.append("INSERT directo como VALIDADO: NO se rechazó (error)")
        todo_ok = False
    except sqlite3.IntegrityError as error:
        lineas.append(f"INSERT directo como VALIDADO: rechazado por la base de datos -> {error}")
    paso("Integridad: referencias inexistentes y estado inicial", lineas, ok=todo_ok)
    return pasos


def formatear_demostracion(pasos):
    partes = []
    for p in pasos:
        partes.append(f"[{p['id']}] {p['titulo']}  ({'OK' if p['ok'] else 'FALLO'})")
        partes += [f"    {linea}" for linea in p["lineas"]]
    return "\n".join(partes)


if __name__ == "__main__":
    print("=== SEMANA 15: BASE DE CONOCIMIENTO EMPRESARIAL (SQLite) ===")
    print(formatear_demostracion(ejecutar_demostracion()))
    print(f"\nBase de datos generada en: {RUTA_DB}")