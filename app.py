from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from models import db
import os

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
CORS(app, origins=app.config['CORS_ORIGINS'])
jwt = JWTManager(app)
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'RentalMonitor Pro API'})

@app.route('/api/objects', methods=['GET'])
def get_objects():
    return jsonify([])

@app.route('/api/analytics/summary', methods=['GET'])
def analytics_summary():
    return jsonify({
        'count': 0,
        'avg_profitability': 0,
        'undervalued_count': 0,
        'for_sale_count': 0,
        'for_rent_count': 0
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
