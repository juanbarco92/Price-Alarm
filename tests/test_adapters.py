"""
Tests automatizados para validar adaptadores.

Este módulo contiene tests unitarios y de integración para validar
que los adaptadores funcionan correctamente.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
from playwright.sync_api import sync_playwright

# Agregar directorio padre al path
sys.path.append(str(Path(__file__).parent.parent))

from adapters import alkosto, test_adapter

class TestAdapterBase(unittest.TestCase):
    """Clase base para tests de adaptadores."""
    
    @classmethod
    def setUpClass(cls):
        """Configuración inicial para todos los tests."""
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)
        cls.page = cls.browser.new_page()
        
        # Configurar página
        cls.page.set_viewport_size({"width": 1280, "height": 720})
        cls.page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    @classmethod
    def tearDownClass(cls):
        """Limpieza después de todos los tests."""
        cls.browser.close()
        cls.playwright.stop()

class TestTestAdapter(TestAdapterBase):
    """Tests para el adaptador de prueba."""
    
    def test_get_price_pampers(self):
        """Test con URL que contiene 'pampers'."""
        url = "https://example.com/pampers-product"
        product_name, current_price, old_price = test_adapter.get_price(self.page, url)
        
        self.assertIn("Pampers", product_name)
        self.assertIsInstance(current_price, float)
        self.assertGreater(current_price, 0)
        # old_price puede ser None en el simulador
    
    def test_get_price_generic(self):
        """Test con URL genérica."""
        url = "https://example.com/generic-product"
        product_name, current_price, old_price = test_adapter.get_price(self.page, url)
        
        self.assertIsInstance(product_name, str)
        self.assertIsInstance(current_price, float)
        self.assertGreater(current_price, 0)

class TestAlkostoAdapter(TestAdapterBase):
    """Tests para el adaptador de Alkosto."""
    
    def test_parse_price_formats(self):
        """Test para diferentes formatos de precio."""
        test_cases = [
            ("$1.234.567", 1234567.0),
            ("$ 1,234,567", 1234567.0),
            ("1.234.567 COP", 1234567.0),
            ("$45.000", 45000.0),
            ("45,000", 45000.0),
            ("$1.234.567,89", 1234567.89),
            ("1,234,567.89", 1234567.89),
            ("", 0.0),
            ("texto sin números", 0.0)
        ]
        
        for price_text, expected in test_cases:
            with self.subTest(price_text=price_text):
                result = alkosto._parse_price(price_text)
                self.assertEqual(result, expected, 
                               f"Failed for '{price_text}': expected {expected}, got {result}")
    
    @patch('adapters.alkosto._extract_product_name')
    @patch('adapters.alkosto._extract_current_price')
    @patch('adapters.alkosto._extract_old_price')
    def test_get_price_mock(self, mock_old_price, mock_current_price, mock_product_name):
        """Test de get_price con mocks para evitar dependencias de red."""
        # Configurar mocks
        mock_product_name.return_value = "Producto de Prueba"
        mock_current_price.return_value = 45000.0
        mock_old_price.return_value = 50000.0
        
        # Crear página mock
        page_mock = MagicMock()
        
        result = alkosto.get_price(page_mock, "https://www.alkosto.com/test")
        
        self.assertEqual(result[0], "Producto de Prueba")
        self.assertEqual(result[1], 45000.0)
        self.assertEqual(result[2], 50000.0)
        
        # Verificar que se llamaron los métodos
        page_mock.goto.assert_called_once()
        mock_product_name.assert_called_once()
        mock_current_price.assert_called_once()
        mock_old_price.assert_called_once()

class TestSelectorValidation(TestAdapterBase):
    """Tests para validar que los selectores CSS están actualizados."""
    
    def create_test_html(self, product_name: str, current_price: str, old_price: str = None):
        """Crea HTML de prueba para validar selectores."""
        old_price_html = f'<span class="old-price">{old_price}</span>' if old_price else ""
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Test Product Page</title></head>
        <body>
            <h1 class="product-title">{product_name}</h1>
            <div class="price-container">
                <span class="current-price">{current_price}</span>
                {old_price_html}
            </div>
        </body>
        </html>
        """
        return html
    
    def test_extract_with_known_html(self):
        """Test extracción con HTML controlado."""
        html = self.create_test_html(
            "Producto de Prueba", 
            "$45.000", 
            "$50.000"
        )
        
        # Cargar HTML en la página
        self.page.set_content(html)
        
        # Test extracción de nombre
        try:
            name = alkosto._extract_product_name(self.page)
            self.assertEqual(name, "Producto de Prueba")
        except ValueError:
            self.fail("No se pudo extraer nombre con HTML conocido")
        
        # Test extracción de precio actual
        try:
            price = alkosto._extract_current_price(self.page)
            self.assertEqual(price, 45000.0)
        except ValueError:
            self.fail("No se pudo extraer precio actual con HTML conocido")
        
        # Test extracción de precio anterior
        old_price = alkosto._extract_old_price(self.page)
        self.assertEqual(old_price, 50000.0)

def run_tests():
    """Ejecuta todos los tests."""
    # Crear suite de tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar tests
    suite.addTests(loader.loadTestsFromTestCase(TestTestAdapter))
    suite.addTests(loader.loadTestsFromTestCase(TestAlkostoAdapter))
    suite.addTests(loader.loadTestsFromTestCase(TestSelectorValidation))
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ejecutar tests de adaptadores")
    parser.add_argument("--test", help="Ejecutar test específico")
    
    args = parser.parse_args()
    
    if args.test:
        # Ejecutar test específico
        unittest.main(argv=[''], verbosity=2, exit=False, 
                     defaultTest=f"__main__.{args.test}")
    else:
        # Ejecutar todos los tests
        success = run_tests()
        sys.exit(0 if success else 1)
