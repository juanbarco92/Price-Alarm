# Testing de Adaptadores

Esta carpeta contiene herramientas para testear y debuggear adaptadores de scraping.

## Scripts Disponibles

### 1. `test_adapter_interactive.py` - Tester Interactivo
Script principal para probar adaptadores de forma interactiva y debuggear problemas.

**Uso básico:**
```bash
python tests/test_adapter_interactive.py --url "https://www.alkosto.com/producto/p/123" --adapter alkosto
```

**Opciones disponibles:**
- `--url`: URL del producto a testear (requerido)
- `--adapter`: Adaptador a usar (alkosto, test)
- `--debug`: Muestra información detallada de debugging
- `--screenshot`: Toma screenshot de la página
- `--no-headless`: Ejecuta navegador visible
- `--verbose`: Logging detallado

**Ejemplos:**
```bash
# Test básico
python tests/test_adapter_interactive.py --url "https://www.alkosto.com/producto" --adapter alkosto

# Test con debugging para ver selectores disponibles
python tests/test_adapter_interactive.py --url "https://www.alkosto.com/producto" --adapter alkosto --debug

# Test con screenshot y navegador visible
python tests/test_adapter_interactive.py --url "https://www.alkosto.com/producto" --adapter alkosto --screenshot --no-headless
```

### 2. `test_adapters.py` - Tests Automatizados
Tests unitarios y de integración para validar adaptadores.

**Ejecutar todos los tests:**
```bash
python tests/test_adapters.py
```

**Ejecutar test específico:**
```bash
python tests/test_adapters.py --test TestAlkostoAdapter.test_parse_price_formats
```

### 3. `compare_adapters.py` - Comparador Multi-Producto
Permite probar múltiples productos y generar reportes comparativos.

**Usar con URLs individuales:**
```bash
python tests/compare_adapters.py --urls "https://alkosto.com/producto1" "https://alkosto.com/producto2"
```

**Usar con archivo de URLs:**
```bash
python tests/compare_adapters.py --file tests/test_urls.txt
```

**Con salida personalizada:**
```bash
python tests/compare_adapters.py --file tests/test_urls.txt --output resultados_hoy.json
```

## Archivos de Configuración

### `test_urls.txt`
Archivo con URLs de prueba, una por línea. Úsalo para tener un conjunto estándar de productos para testing.

### `screenshots/`
Carpeta donde se guardan los screenshots tomados durante el testing. Útil para análisis visual de páginas problemáticas.

## Flujo de Trabajo Recomendado

### 1. **Primer Test de un Adaptador**
```bash
# Probar con debugging para entender la estructura de la página
python tests/test_adapter_interactive.py --url "TU_URL" --adapter alkosto --debug --screenshot
```

### 2. **Ajustar Selectores CSS**
- Revisar la salida del debugging
- Modificar selectores en el adaptador
- Repetir hasta que funcione

### 3. **Validar con Tests Automatizados**
```bash
python tests/test_adapters.py
```

### 4. **Probar Múltiples Productos**
```bash
python tests/compare_adapters.py --file tests/test_urls.txt
```

## Información de Debugging

El script interactivo con `--debug` muestra:

1. **Información básica de la página:**
   - Título, URL, dimensiones

2. **Posibles selectores para nombres:**
   - Busca elementos h1, h2, con clases que contengan "title", "name", etc.

3. **Posibles selectores para precios:**
   - Busca elementos con clases que contengan "price", "cost", "amount"

4. **Elementos con números grandes:**
   - Usa JavaScript para encontrar posibles precios

## Consejos para Debugging

1. **Usa `--debug` primero** para entender la estructura de la página
2. **Toma screenshots** para análisis visual
3. **Ejecuta sin `--headless`** para ver qué está pasando en tiempo real
4. **Revisa los logs** con `--verbose` para detalles técnicos

## Extensión para Nuevos Sitios

Para agregar soporte a un nuevo sitio web:

1. Crea un nuevo adaptador en `adapters/`
2. Agrega detección del dominio en `track.py` y en los scripts de test
3. Agrega URLs de prueba en `test_urls.txt`
4. Ejecuta los tests para validar funcionamiento

## Resultados y Reportes

Los resultados se guardan en formato JSON con:
- Información del producto extraída
- Errores encontrados
- Timestamps para tracking
- Estadísticas de éxito/fallo
