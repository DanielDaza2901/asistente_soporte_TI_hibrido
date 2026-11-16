-- =====================================================================
-- Semana 15 - Base de conocimiento empresarial del Asistente de Soporte TI
-- Esquema SQLite: 5 tablas, claves primarias/foráneas y restricciones.
-- Ejecutar sobre una base vacía (reinicia las tablas si ya existen).
-- =====================================================================
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS articulo;
DROP TABLE IF EXISTS herramienta;
DROP TABLE IF EXISTS experto;
DROP TABLE IF EXISTS aplicacion;
DROP TABLE IF EXISTS dominio;

-- 1) Dominios de conocimiento del proyecto (áreas temáticas)
CREATE TABLE dominio (
    id_dominio   INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre       TEXT NOT NULL UNIQUE CHECK (length(trim(nombre)) >= 3),
    descripcion  TEXT NOT NULL CHECK (length(trim(descripcion)) >= 10)
);

-- 2) Aplicaciones o módulos del sistema; cada una pertenece a un dominio
CREATE TABLE aplicacion (
    id_aplicacion  INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre         TEXT NOT NULL UNIQUE CHECK (length(trim(nombre)) >= 3),
    descripcion    TEXT NOT NULL CHECK (length(trim(descripcion)) >= 10),
    modulo         TEXT NOT NULL CHECK (length(trim(modulo)) >= 3),   -- ruta en el repositorio
    id_dominio     INTEGER NOT NULL,
    FOREIGN KEY (id_dominio) REFERENCES dominio (id_dominio)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

-- 3) Expertos responsables; cada uno tiene un dominio de especialidad
CREATE TABLE experto (
    id_experto  INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT NOT NULL CHECK (length(trim(nombre)) >= 3),
    cargo       TEXT NOT NULL CHECK (length(trim(cargo)) >= 3),
    correo      TEXT NOT NULL UNIQUE CHECK (correo LIKE '%_@_%._%'),
    id_dominio  INTEGER NOT NULL,
    FOREIGN KEY (id_dominio) REFERENCES dominio (id_dominio)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

-- 4) Herramientas de desarrollo utilizadas en el proyecto
CREATE TABLE herramienta (
    id_herramienta  INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre          TEXT NOT NULL UNIQUE CHECK (length(trim(nombre)) >= 2),
    tipo            TEXT NOT NULL CHECK (tipo IN
        ('LENGUAJE', 'BASE_DE_DATOS', 'LIBRERIA', 'FRAMEWORK', 'PRUEBAS', 'CONTROL_DE_VERSIONES')),
    descripcion     TEXT NOT NULL CHECK (length(trim(descripcion)) >= 10)
);

-- 5) Artículos o procedimientos: unen dominio, aplicación, experto y (opcional) herramienta
CREATE TABLE articulo (
    id_articulo       INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo            TEXT NOT NULL CHECK (length(trim(titulo)) >= 5),
    contenido         TEXT NOT NULL CHECK (length(trim(contenido)) >= 20),
    id_dominio        INTEGER NOT NULL,
    id_aplicacion     INTEGER NOT NULL,
    id_experto        INTEGER NOT NULL,
    id_herramienta    INTEGER,                                   -- opcional
    fuente            TEXT NOT NULL CHECK (length(trim(fuente)) >= 3),
    estado            TEXT NOT NULL DEFAULT 'BORRADOR' CHECK (estado IN ('BORRADOR', 'VALIDADO')),
    fecha_registro    TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    fecha_validacion  TEXT,
    UNIQUE (titulo, id_aplicacion),
    -- Un artículo VALIDADO siempre tiene fecha de validación; un BORRADOR nunca.
    CHECK ((estado = 'VALIDADO' AND fecha_validacion IS NOT NULL)
        OR (estado = 'BORRADOR'  AND fecha_validacion IS NULL)),
    FOREIGN KEY (id_dominio)      REFERENCES dominio (id_dominio)           ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (id_aplicacion)   REFERENCES aplicacion (id_aplicacion)     ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (id_experto)      REFERENCES experto (id_experto)           ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY (id_herramienta)  REFERENCES herramienta (id_herramienta)   ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE INDEX idx_articulo_dominio_estado ON articulo (id_dominio, estado);

-- Regla de negocio 1: todo artículo nuevo nace como BORRADOR.
CREATE TRIGGER trg_articulo_inicia_borrador
BEFORE INSERT ON articulo
WHEN NEW.estado <> 'BORRADOR'
BEGIN
    SELECT RAISE(ABORT, 'Un articulo nuevo debe registrarse como BORRADOR');
END;

-- Regla de negocio 2: la aplicación del artículo debe pertenecer a su dominio.
CREATE TRIGGER trg_articulo_coherencia_dominio
BEFORE INSERT ON articulo
WHEN EXISTS (SELECT 1 FROM aplicacion
             WHERE id_aplicacion = NEW.id_aplicacion AND id_dominio <> NEW.id_dominio)
BEGIN
    SELECT RAISE(ABORT, 'La aplicacion no pertenece al dominio indicado');
END;

-- Regla de negocio 3: un artículo VALIDADO no puede volver a BORRADOR.
CREATE TRIGGER trg_articulo_sin_retroceso
BEFORE UPDATE OF estado ON articulo
WHEN OLD.estado = 'VALIDADO' AND NEW.estado = 'BORRADOR'
BEGIN
    SELECT RAISE(ABORT, 'Un articulo VALIDADO no puede volver a BORRADOR');
END;