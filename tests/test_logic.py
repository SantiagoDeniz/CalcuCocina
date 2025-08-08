import unittest
from logic import dividir_partes_respuesta

class TestLogic(unittest.TestCase):
    def test_dividir_partes_respuesta(self):
        texto = "visible\n=== NO INCLUIR ESTO EN EL MENSAJE PRINCIPAL ===\noculto"
        visible, oculto = dividir_partes_respuesta(texto)
        self.assertEqual(visible, "visible")
        self.assertTrue("oculto" in oculto)

if __name__ == "__main__":
    unittest.main()
