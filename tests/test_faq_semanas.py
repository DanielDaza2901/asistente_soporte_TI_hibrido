"""Pruebas del asistente de preguntas frecuentes (Semana 02 a Semana 14).
Ejecutar desde la raíz del proyecto:  python -m unittest discover -s tests -v
"""
import sys
import unittest
from pathlib import Path

_AQUI = Path(__file__).resolve().parent
for _c in (_AQUI, _AQUI.parent, _AQUI / "src", _AQUI.parent / "src"):
    if (_c / "classifiers").is_dir() and str(_c) not in sys.path:
        sys.path.insert(0, str(_c))

from classifiers.faq_semanas import AsistenteFAQ, FAQ_SEMANAS, SEMANAS

SEMANAS_IMPLEMENTADAS = {2, 3, 4, 5, 7, 8, 9, 10, 11, 13, 14}


class TestCatalogo(unittest.TestCase):
    def test_estructura_de_cada_pregunta(self):
        for faq in FAQ_SEMANAS:
            with self.subTest(id=faq["id"]):
                for campo in ("id", "semana", "tema", "pregunta", "respuesta", "claves", "ref"):
                    self.assertTrue(faq[campo] not in (None, ""), campo)
                self.assertIn(faq["semana"], SEMANAS)
                self.assertTrue(faq["pregunta"].startswith("¿") and faq["pregunta"].endswith("?"))

    def test_ids_unicos(self):
        ids = [f["id"] for f in FAQ_SEMANAS]
        self.assertEqual(len(ids), len(set(ids)))

    def test_cubre_todas_las_semanas_implementadas(self):
        cubiertas = {f["semana"] for f in FAQ_SEMANAS}
        self.assertTrue(SEMANAS_IMPLEMENTADAS <= cubiertas)
        self.assertIn(0, cubiertas)

    def test_al_menos_cuatro_preguntas_por_semana(self):
        for semana in SEMANAS_IMPLEMENTADAS:
            with self.subTest(semana=semana):
                self.assertGreaterEqual(len([f for f in FAQ_SEMANAS if f["semana"] == semana]), 4)


class TestBusqueda(unittest.TestCase):
    def setUp(self):
        self.asistente = AsistenteFAQ()

    def semana_top(self, consulta):
        r = self.asistente.buscar(consulta, k=1)
        return r[0]["semana"] if r else None

    def test_consultas_por_semana(self):
        casos = {
            "qué es la matriz de confusión": 2, "cómo se calcula la prioridad del ticket": 2,
            "qué áreas tiene la taxonomía": 3, "qué tecnologías usa el proyecto": 0,
            "qué métricas guarda el benchmark": 11, "dónde queda el informe de la semana 5": 5,
            "cómo funciona A*": 4, "para qué sirve minimax": 4, "qué es tf-idf": 5,
            "qué es un autómata finito": 7, "qué es base64": 8, "para qué sirve otsu": 9,
            "qué es lbp": 10, "qué modelos compara el benchmark": 11, "qué es un adr": 11,
            "qué son las reglas de horn": 13, "qué es el encadenamiento hacia adelante": 13,
            "qué es una red semántica": 14, "qué significa mundo cerrado": 14, "cómo ejecuto el proyecto": 0,
        }
        for consulta, semana in casos.items():
            with self.subTest(consulta=consulta):
                self.assertEqual(self.semana_top(consulta), semana)

    def test_ignora_tildes_y_mayusculas(self):
        a = self.asistente.buscar("CÓMO FUNCIONA A*")[0]["id"]
        b = self.asistente.buscar("como funciona a*")[0]["id"]
        self.assertEqual(a, b)

    def test_variantes_de_a_estrella(self):
        for consulta in ("cómo funciona A*", "cómo funciona a estrella", "cómo funciona A *"):
            with self.subTest(consulta=consulta):
                self.assertEqual(self.semana_top(consulta), 4)

    def test_similitud_en_rango_y_ordenada(self):
        r = self.asistente.buscar("qué es la similitud coseno", k=5)
        sims = [x["similitud"] for x in r]
        self.assertTrue(all(0.0 <= s <= 1.0 for s in sims))
        self.assertEqual(sims, sorted(sims, reverse=True))

    def test_respeta_k(self):
        self.assertLessEqual(len(self.asistente.buscar("modelo", k=2, umbral=0.0)), 2)

    def test_filtro_por_semana(self):
        for r in self.asistente.buscar("qué es una regla", k=5, semana=13, umbral=0.0):
            self.assertEqual(r["semana"], 13)

    def test_consulta_sin_relacion_devuelve_vacio(self):
        for consulta in ("receta de arroz con pollo", "quién ganó el mundial de fútbol", "asdfgh qwerty"):
            with self.subTest(consulta=consulta):
                self.assertEqual(self.asistente.buscar(consulta), [])

    def test_consulta_vacia(self):
        for consulta in ("", "   ", "¿?"):
            with self.subTest(consulta=repr(consulta)):
                self.assertEqual(self.asistente.buscar(consulta), [])

    def test_entrada_que_no_es_texto(self):
        for valor in (None, 42, ["a"]):
            with self.subTest(valor=valor):
                with self.assertRaises(ValueError):
                    self.asistente.buscar(valor)

    def test_el_resultado_no_modifica_el_catalogo(self):
        r = self.asistente.buscar("qué es lbp")[0]
        r["respuesta"] = "alterada"
        self.assertNotEqual(self.asistente.buscar("qué es lbp")[0]["respuesta"], "alterada")


class TestExploracion(unittest.TestCase):
    def setUp(self):
        self.asistente = AsistenteFAQ()

    def test_semanas_disponibles(self):
        self.assertEqual(self.asistente.semanas_disponibles(), sorted({f["semana"] for f in FAQ_SEMANAS}))

    def test_por_semana(self):
        lista = self.asistente.por_semana(14)
        self.assertTrue(lista)
        self.assertTrue(all(f["semana"] == 14 for f in lista))
        self.assertEqual(len(self.asistente.por_semana(None)), len(FAQ_SEMANAS))

    def test_sugerencias_son_preguntas_reales(self):
        preguntas = {f["pregunta"] for f in FAQ_SEMANAS}
        sugeridas = self.asistente.sugerencias(4)
        self.assertEqual(len(sugeridas), 4)
        self.assertTrue(set(sugeridas) <= preguntas)

    def test_cada_pregunta_se_recupera_a_si_misma(self):
        """La pregunta exacta del catálogo debe devolver esa misma pregunta en primer lugar."""
        for faq in FAQ_SEMANAS:
            with self.subTest(id=faq["id"]):
                self.assertEqual(self.asistente.buscar(faq["pregunta"], k=1, umbral=0.0)[0]["id"], faq["id"])


if __name__ == "__main__":
    unittest.main()