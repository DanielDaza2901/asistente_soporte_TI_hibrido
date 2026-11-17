"""
Pruebas unitarias del Motor de Referencia (Semana 16)
Asistente de Soporte TI Híbrido
"""
import unittest
import tempfile
from pathlib import Path
import sys

_AQUI = Path(__file__).resolve().parent
for _c in (_AQUI, _AQUI.parent, _AQUI / "src", _AQUI.parent / "src"):
    if (_c / "base_conocimiento.py").exists() and str(_c) not in sys.path:
        sys.path.insert(0, str(_c))

from classifiers.base_conocimiento import BaseConocimiento
from classifiers.motor_referencia import MotorReferencia, normalizar_texto

class TestMotorReferencia(unittest.TestCase):
    
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        db_path = Path(self.tmp.name) / "test_bc.db"
        self.bc = BaseConocimiento(ruta_db=db_path)
        self.bc.crear_esquema(con_datos=True, reiniciar=True)
        self.motor = MotorReferencia(bc=self.bc)

    def tearDown(self):
        self.tmp.cleanup()

    def test_1_consulta_con_respuesta_valida(self):
        """Demuestra una consulta exitosa que encuentra una referencia VALIDADA."""
        resultado = self.motor.consultar("calcular la prioridad con matriz impacto urgencia")
        self.assertEqual(resultado["estado"], "ENCONTRADA")
        self.assertIsNotNone(resultado["referencia"])
        self.assertIn("prioridad", resultado["referencia"]["titulo"].casefold())
        self.assertTrue(resultado["referencia"]["fuente"])

    def test_2_exclusion_referencia_no_aprobada(self):
        """Demuestra que un artículo en estado BORRADOR es excluido y no entregado como respuesta."""
        id_dom = self.bc.obtener_id("dominio", "Razonamiento simbólico")
        id_app = self.bc.obtener_id("aplicacion", "Red semántica de soporte TI")
        id_exp = self.bc.obtener_id("experto", "Carlos Rojas")
        
        titulo_secreto = "Procedimiento confidencial borrador secreto xyz123"
        self.bc.registrar_articulo(
            titulo=titulo_secreto,
            contenido="Este contenido es un borrador no validado y secreto.",
            id_dominio=id_dom,
            id_aplicacion=id_app,
            id_experto=id_exp,
            fuente="src/borrador.py"
        )
        
        # Consultar por el título secreto del borrador
        resultado = self.motor.consultar("procedimiento confidencial borrador secreto xyz123")
        # El motor debe retornar SIN_REFERENCIA por estar en estado BORRADOR
        self.assertEqual(resultado["estado"], "SIN_REFERENCIA")

    def test_3_pregunta_fuera_de_conocimiento(self):
        """Demuestra el comportamiento ante una pregunta fuera de cobertura (SIN_REFERENCIA)."""
        resultado = self.motor.consultar("receta para preparar lasaña boloñesa de pollo")
        self.assertEqual(resultado["estado"], "SIN_REFERENCIA")
        self.assertIsNone(resultado["referencia"])

    def test_4_normalizacion_correcta(self):
        """Demuestra la normalización correcta de mayúsculas, tildes y signos."""
        texto_sucio = "  ¡CÁLCULO de la PRIORIDAD con Matriz de Impacto!  "
        tokens = normalizar_texto(texto_sucio)
        self.assertIn("calculo", tokens)
        self.assertIn("prioridad", tokens)
        self.assertIn("matriz", tokens)
        self.assertIn("impacto", tokens)
        self.assertNotIn("cálculo", tokens) # Comprueba remoción de tildes

    def test_5_identificacion_fuente_utilizada(self):
        """Demuestra que la respuesta identifica claramente el ID, el título y la fuente utilizada."""
        resultado = self.motor.consultar("red semantica jerarquia herencia")
        self.assertEqual(resultado["estado"], "ENCONTRADA")
        ref = resultado["referencia"]
        self.assertTrue(ref["id"].startswith("REF-"))
        self.assertTrue(ref["fuente"])
        self.assertTrue(ref["titulo"])
        self.assertTrue(ref["respuesta"])

    def test_6_consulta_vacia(self):
        """Comprueba el manejo adecuado de consultas vacías o con espacios en blanco."""
        resultado = self.motor.consultar("   ")
        self.assertEqual(resultado["estado"], "VACIA")
        self.assertIn("ingresar una pregunta", resultado["mensaje"].casefold())


if __name__ == "__main__":
    unittest.main()