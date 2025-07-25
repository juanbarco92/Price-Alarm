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
        # TODO: Implement product listing from database
        return jsonify({
            "products": [],
            "message": "API endpoint working"
        })
    
    @app.route('/api/products', methods=['POST'])
    def add_product():
        """API endpoint to add a new product."""
        data = request.get_json()
        # TODO: Implement product addition
        return jsonify({
            "status": "success", 
            "message": "Product addition endpoint ready"
        })
    
    @app.route('/api/prices/<product_alias>')
    def get_price_history(product_alias):
        """API endpoint to get price history for a product."""
        # TODO: Implement price history retrieval
        return jsonify({
            "product": product_alias,
            "prices": [],
            "message": "Price history endpoint ready"
        })
    
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
