"""Pruebas de la base de conocimiento empresarial (Semana 15).

Ejecutar desde la raíz del proyecto:
    python -m unittest tests.test_base_conocimiento -v
Las cinco pruebas exigidas en la sustentación están en la clase TestCincoPruebasObligatorias.
"""
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

_AQUI = Path(__file__).resolve().parent
for _c in (_AQUI, _AQUI.parent, _AQUI / "src", _AQUI.parent / "src"):
    if (_c / "base_conocimiento.py").exists() and str(_c) not in sys.path:
        sys.path.insert(0, str(_c))

from classifiers.base_conocimiento import (BORRADOR, VALIDADO, ArticuloNoEncontradoError, BaseConocimiento, DatosInvalidosError,
                               EstadoInvalidoError, ReferenciaInexistenteError, ejecutar_demostracion)

CONTENIDO = "Contenido de prueba con la extensión suficiente para cumplir la restricción de longitud mínima."


class BaseConocimientoTestCase(unittest.TestCase):
    """Cada prueba trabaja sobre una base nueva y temporal, cargada con sql/esquema.sql y sql/datos.sql."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.bc = BaseConocimiento(Path(self.tmp.name) / "kb.db")
        self.bc.crear_esquema(con_datos=True)
        self.dominio = self.bc.obtener_id("dominio", "Razonamiento simbólico")
        self.aplicacion = self.bc.obtener_id("aplicacion", "Red semántica de soporte TI")
        self.experto = self.bc.obtener_id("experto", "Carlos Rojas")
        self.herramienta = self.bc.obtener_id("herramienta", "Python")

    def tearDown(self):
        self.tmp.cleanup()

    def nuevo(self, titulo="Artículo de prueba", **cambios):
        datos = dict(titulo=titulo, contenido=CONTENIDO, id_dominio=self.dominio, id_aplicacion=self.aplicacion,
                     id_experto=self.experto, fuente="src/classifiers/red_semantica.py", id_herramienta=self.herramienta)
        datos.update(cambios)
        return self.bc.registrar_articulo(**datos)

    def titulos_visibles(self, dominio=None):
        return [a["titulo"] for a in self.bc.consultar_por_dominio(dominio or self.dominio)]


class TestCincoPruebasObligatorias(BaseConocimientoTestCase):
    def test_1_registro_inicia_como_borrador(self):
        """Registrar un artículo lo deja en estado BORRADOR y sin fecha de validación."""
        art = self.bc.obtener_articulo(self.nuevo("Registro inicial"))
        self.assertEqual(art["estado"], BORRADOR)
        self.assertIsNone(art["fecha_validacion"])

    def test_2_borrador_no_aparece_en_consultas_habituales(self):
        """Un BORRADOR no aparece al consultar por dominio ni en la lista de publicados."""
        self.nuevo("Solo borrador")
        self.assertNotIn("Solo borrador", self.titulos_visibles())
        self.assertNotIn("Solo borrador", [a["titulo"] for a in self.bc.listar_publicados()])

    def test_3_validar_lo_hace_visible(self):
        """Tras validarlo, el artículo pasa a VALIDADO y aparece en la consulta por dominio."""
        id_art = self.nuevo("Se publica")
        self.bc.validar_articulo(id_art)
        self.assertEqual(self.bc.obtener_articulo(id_art)["estado"], VALIDADO)
        self.assertIn("Se publica", self.titulos_visibles())

    def test_4_dominio_inexistente_es_rechazado(self):
        """No se puede registrar un artículo con un dominio que no existe."""
        with self.assertRaises(ReferenciaInexistenteError):
            self.nuevo("Dominio falso", id_dominio=9999)

    def test_5_experto_inexistente_es_rechazado(self):
        """No se puede registrar un artículo con un experto que no existe."""
        with self.assertRaises(ReferenciaInexistenteError):
            self.nuevo("Experto falso", id_experto=9999)


class TestEsquemaYDatos(BaseConocimientoTestCase):
    def test_existen_las_cinco_tablas(self):
        self.assertTrue(self.bc.existe_base())
        with self.bc._conexion() as con:
            tablas = {f[0] for f in con.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
        self.assertTrue({"dominio", "aplicacion", "experto", "herramienta", "articulo"} <= tablas)

    def test_datos_de_ejemplo_cargados(self):
        r = self.bc.resumen()
        self.assertEqual((r["dominio"], r["aplicacion"], r["experto"], r["herramienta"], r["articulo"]), (7, 11, 7, 8, 12))
        self.assertEqual((r["validados"], r["borradores"]), (9, 3))

    def test_el_script_sql_no_deja_violaciones_de_claves_foraneas(self):
        with self.bc._conexion() as con:
            self.assertEqual(con.execute("PRAGMA foreign_key_check").fetchall(), [])


class TestRegistroYValidacion(BaseConocimientoTestCase):
    def test_aplicacion_o_herramienta_inexistente(self):
        with self.assertRaises(ReferenciaInexistenteError):
            self.nuevo("App falsa", id_aplicacion=9999)
        with self.assertRaises(ReferenciaInexistenteError):
            self.nuevo("Herramienta falsa", id_herramienta=9999)

    def test_aplicacion_de_otro_dominio_se_rechaza(self):
        otro = self.bc.obtener_id("dominio", "Visión artificial")
        with self.assertRaises(DatosInvalidosError):
            self.nuevo("Incoherente", id_dominio=otro)

    def test_herramienta_es_opcional(self):
        art = self.bc.obtener_articulo(self.nuevo("Sin herramienta", id_herramienta=None))
        self.assertIsNone(art["herramienta"])

    def test_titulo_duplicado_para_la_misma_aplicacion(self):
        self.nuevo("Título repetido")
        with self.assertRaises(DatosInvalidosError):
            self.nuevo("Título repetido")

    def test_textos_invalidos(self):
        for campo, valor in (("titulo", "abc"), ("contenido", "corto"), ("fuente", " "), ("titulo", None), ("contenido", 123)):
            with self.subTest(campo=campo, valor=valor):
                cambios = {"titulo": "Válido para el resto", campo: valor}
                with self.assertRaises(DatosInvalidosError):
                    self.nuevo(**cambios)

    def test_identificadores_deben_ser_enteros(self):
        with self.assertRaises(DatosInvalidosError):
            self.nuevo("Id texto", id_dominio="3")

    def test_validar_inexistente(self):
        with self.assertRaises(ArticuloNoEncontradoError):
            self.bc.validar_articulo(9999)

    def test_validar_dos_veces(self):
        id_art = self.nuevo("Doble validación")
        self.bc.validar_articulo(id_art)
        with self.assertRaises(EstadoInvalidoError):
            self.bc.validar_articulo(id_art)

    def test_validar_registra_la_fecha(self):
        id_art = self.nuevo("Con fecha")
        self.bc.validar_articulo(id_art)
        self.assertTrue(self.bc.obtener_articulo(id_art)["fecha_validacion"])


class TestConsultas(BaseConocimientoTestCase):
    def test_consulta_por_id_y_por_nombre_sin_distinguir_mayusculas(self):
        por_id = self.titulos_visibles(self.dominio)
        self.assertEqual(por_id, self.titulos_visibles("razonamiento SIMBÓLICO".replace("SIMBÓLICO", "simbólico")))
        self.assertTrue(por_id)

    def test_dominio_inexistente_en_consulta(self):
        with self.assertRaises(ReferenciaInexistenteError):
            self.bc.consultar_por_dominio("No existe")
        with self.assertRaises(ReferenciaInexistenteError):
            self.bc.consultar_por_dominio(9999)

    def test_join_devuelve_dominio_aplicacion_experto_y_herramienta(self):
        fila = self.bc.consultar_por_dominio(self.dominio)[0]
        for campo in ("dominio", "aplicacion", "experto", "herramienta", "fuente", "estado"):
            self.assertTrue(fila[campo], campo)
        self.assertEqual(fila["dominio"], "Razonamiento simbólico")

    def test_publicados_solo_contiene_validados(self):
        self.assertTrue(all(a["estado"] == VALIDADO for a in self.bc.listar_publicados()))
        self.assertEqual(len(self.bc.listar_publicados()), 9)

    def test_borradores_de_ejemplo_no_son_visibles_hasta_validarse(self):
        self.assertEqual(self.bc.buscar_publicados("Canny"), [])
        pendiente = next(b for b in self.bc.listar_borradores() if "Canny" in b["titulo"])
        self.bc.validar_articulo(pendiente["id_articulo"])
        self.assertEqual(len(self.bc.buscar_publicados("Canny")), 1)

    def test_incluir_borradores_es_explicito(self):
        self.nuevo("Pendiente de revisión")
        self.assertIn("Pendiente de revisión", [a["titulo"] for a in self.bc.consultar_por_dominio(self.dominio, incluir_borradores=True)])
        self.assertNotIn("Pendiente de revisión", self.titulos_visibles())

    def test_contar_por_dominio(self):
        conteo = self.bc.contar_por_dominio()
        self.assertEqual(sum(c["validados"] for c in conteo), 9)
        self.assertEqual(sum(c["borradores"] for c in conteo), 3)


class TestIntegridadEnLaBaseDeDatos(BaseConocimientoTestCase):
    """Estas pruebas saltan el código Python y atacan directamente a SQLite."""

    INSERT = ("INSERT INTO articulo (titulo, contenido, id_dominio, id_aplicacion, id_experto, fuente{extra}) "
              "VALUES ('Directo SQL', '" + CONTENIDO + "', ?, ?, ?, 'fuente'{valores})")

    def ejecutar(self, sql, params=()):
        with self.bc._conexion() as con:
            con.execute(sql, params)

    def test_la_base_rechaza_insertar_directamente_como_validado(self):
        sql = self.INSERT.format(extra=", estado, fecha_validacion", valores=", 'VALIDADO', datetime('now')")
        with self.assertRaises(sqlite3.IntegrityError):
            self.ejecutar(sql, (self.dominio, self.aplicacion, self.experto))

    def test_la_base_rechaza_claves_foraneas_inexistentes(self):
        sql = self.INSERT.format(extra="", valores="")
        with self.assertRaises(sqlite3.IntegrityError):
            self.ejecutar(sql, (9999, self.aplicacion, self.experto))

    def test_la_base_rechaza_estados_invalidos(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.ejecutar("UPDATE articulo SET estado = 'ARCHIVADO' WHERE id_articulo = 1")

    def test_un_validado_no_vuelve_a_borrador(self):
        id_art = self.nuevo("Sin retroceso")
        self.bc.validar_articulo(id_art)
        with self.assertRaises(sqlite3.IntegrityError):
            self.ejecutar("UPDATE articulo SET estado = 'BORRADOR', fecha_validacion = NULL WHERE id_articulo = ?", (id_art,))

    def test_no_se_puede_borrar_un_dominio_con_articulos(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.ejecutar("DELETE FROM dominio WHERE id_dominio = ?", (self.dominio,))

    def test_correo_de_experto_unico_y_con_formato(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.ejecutar("INSERT INTO experto (nombre, cargo, correo, id_dominio) VALUES ('Alguien', 'Cargo de prueba', 'sin-arroba', ?)", (self.dominio,))
        with self.assertRaises(sqlite3.IntegrityError):
            self.ejecutar("INSERT INTO experto (nombre, cargo, correo, id_dominio) VALUES ('Otro', 'Cargo de prueba', 'carlos.rojas@ejemplo.org', ?)", (self.dominio,))


class TestDemostracion(unittest.TestCase):
    def test_la_demostracion_completa_termina_bien(self):
        with tempfile.TemporaryDirectory() as tmp:
            pasos = ejecutar_demostracion(Path(tmp) / "demo.db")
        self.assertEqual(len(pasos), 7)
        self.assertTrue(all(p["ok"] for p in pasos), [p["titulo"] for p in pasos if not p["ok"]])


if __name__ == "__main__":
    unittest.main()