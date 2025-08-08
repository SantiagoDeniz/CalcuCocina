import unittest
import os
from editor import editar_csv_ingredientes

class TestEditor(unittest.TestCase):
    def test_editar_csv_ingredientes_existe(self):
        # Solo verifica que la función existe y es callable
        self.assertTrue(callable(editar_csv_ingredientes))

if __name__ == "__main__":
    unittest.main()
