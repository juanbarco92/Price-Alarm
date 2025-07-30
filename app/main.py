#!/usr/bin/env python3
"""
Flask application for Price Alarm dashboard.

This app provides:
- Web dashboard for price monitoring
- Admin panel for managing products
- Charts and historical data visualization
- REST API for product management
"""

import os
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

# Import shared modules
import sys
sys.path.append(str(Path(__file__).parent.parent))

from shared.utils.database import PriceDatabase


def create_app(config=None):
    """Application factory for Flask app."""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['DATABASE_URL'] = os.getenv('DATABASE_URL', 'sqlite:///db/prices.db')
    
    # Enable CORS
    CORS(app)
    
    # Initialize database
    db = PriceDatabase()
    
    @app.route('/')
    def dashboard():
        """Main dashboard page."""
        return render_template('dashboard.html')
    
    @app.route('/admin')
    def admin():
        """Admin panel for managing products."""
        return render_template('admin.html')
    
    @app.route('/api/products', methods=['GET'])
    def get_products():
        """API endpoint to get all products."""
        try:
            # Get all products with their presentations and stores
            products = db.get_all_products_with_details()
            return jsonify({
                "products": products,
                "status": "success"
            })
        except Exception as e:
            return jsonify({
                "products": [],
                "status": "error",
                "message": str(e)
            }), 500
    
    @app.route('/api/products', methods=['POST'])
    def add_product():
        """API endpoint to add a new product."""
        try:
            data = request.get_json()
            
            if not data or 'name' not in data or 'alias' not in data:
                return jsonify({
                    "status": "error",
                    "message": "Faltan campos requeridos: name, alias"
                }), 400
            
            # Create product
            product_id = db.create_product(data['name'], data['alias'])
            
            # Add presentations and stores if provided
            if 'presentations' in data:
                for pres_data in data['presentations']:
                    if 'size' in pres_data and 'unit_count' in pres_data:
                        pres_id = db.create_presentation(
                            product_id, 
                            pres_data['size'], 
                            pres_data['unit_count']
                        )
                        
                        # Add stores for this presentation
                        if 'stores' in pres_data:
                            for store_data in pres_data['stores']:
                                if 'name' in store_data and 'url' in store_data:
                                    db.create_store(
                                        pres_id,
                                        store_data['name'],
                                        store_data['url']
                                    )
            
            return jsonify({
                "status": "success",
                "message": "Producto agregado exitosamente",
                "product_id": product_id
            })
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error al agregar producto: {str(e)}"
            }), 500
    
    @app.route('/api/prices/<product_alias>')
    def get_price_history(product_alias):
        """API endpoint to get price history for a product."""
        try:
            # Get price history for this product alias
            prices = db.get_price_history_by_alias(product_alias)
            return jsonify({
                "product": product_alias,
                "prices": prices,
                "status": "success"
            })
        except Exception as e:
            return jsonify({
                "product": product_alias,
                "prices": [],
                "status": "error",
                "message": str(e)
            }), 500
    
    @app.route('/api/products/<int:product_id>', methods=['PUT'])
    def update_product(product_id):
        """API endpoint to update a product."""
        try:
            data = request.get_json()
            success = db.update_product(
                product_id,
                name=data.get('name'),
                alias=data.get('alias')
            )
            
            if success:
                return jsonify({
                    "status": "success",
                    "message": "Producto actualizado exitosamente"
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": "No se pudo actualizar el producto"
                }), 400
                
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error al actualizar producto: {str(e)}"
            }), 500
    
    @app.route('/api/products/<int:product_id>', methods=['DELETE'])
    def delete_product(product_id):
        """API endpoint to delete a product."""
        try:
            success = db.delete_product(product_id)
            
            if success:
                return jsonify({
                    "status": "success",
                    "message": "Producto eliminado exitosamente"
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": "No se pudo eliminar el producto"
                }), 400
                
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error al eliminar producto: {str(e)}"
            }), 500
    
    @app.route('/api/presentations', methods=['POST'])
    def add_presentation():
        """API endpoint to add a new presentation to an existing product."""
        try:
            data = request.get_json()
            
            if not data or 'product_id' not in data or 'size' not in data or 'unit_count' not in data:
                return jsonify({
                    "status": "error",
                    "message": "Faltan campos requeridos: product_id, size, unit_count"
                }), 400
            
            pres_id = db.create_presentation(
                data['product_id'],
                data['size'],
                data['unit_count']
            )
            
            return jsonify({
                "status": "success",
                "message": "Presentación agregada exitosamente",
                "presentation_id": pres_id
            })
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error al agregar presentación: {str(e)}"
            }), 500
    
    @app.route('/api/stores', methods=['POST'])
    def add_store():
        """API endpoint to add a new store to an existing presentation."""
        try:
            data = request.get_json()
            
            if not data or 'presentation_id' not in data or 'store_name' not in data or 'url' not in data:
                return jsonify({
                    "status": "error",
                    "message": "Faltan campos requeridos: presentation_id, store_name, url"
                }), 400
            
            store_id = db.create_store(
                data['presentation_id'],
                data['store_name'],
                data['url']
            )
            
            return jsonify({
                "status": "success",
                "message": "Tienda agregada exitosamente",
                "store_id": store_id
            })
            
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Error al agregar tienda: {str(e)}"
            }), 500
    
    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        return jsonify({"status": "healthy", "service": "price-alarm-web"})
    
    return app


def main():
    """Main entry point for development server."""
    app = create_app()
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug)


if __name__ == '__main__':
    main()
