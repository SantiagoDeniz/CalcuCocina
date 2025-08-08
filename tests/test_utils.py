import unittest
from utils import cargar_ultimo_csv, guardar_ultimo_csv
import os

class TestUtils(unittest.TestCase):
    def setUp(self):
        self.tipo = "test"
        self.ruta = "archivo_prueba.csv"
        self.archivo = f"last_{self.tipo}_csv.txt"
        # Limpia antes
        if os.path.exists(self.archivo):
            os.remove(self.archivo)

    def tearDown(self):
        if os.path.exists(self.archivo):
            os.remove(self.archivo)

    def test_guardar_y_cargar_ultimo_csv(self):
        guardar_ultimo_csv(self.ruta, self.tipo)
        resultado = cargar_ultimo_csv(self.tipo)
        self.assertEqual(resultado, self.ruta)

if __name__ == "__main__":
    unittest.main()
