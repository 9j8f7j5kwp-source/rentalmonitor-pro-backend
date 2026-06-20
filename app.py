from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import db, User, RentalObject
import os
import uuid

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
CORS(app, origins=app.config['CORS_ORIGINS'])
jwt = JWTManager(app)
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# ========== HEALTH CHECK ==========
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'RentalMonitor Pro API'})

# ========== AUTH ENDPOINTS ==========
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409
    
    # Create new user
    new_user = User(
        username=data['username'],
        email=data['email'],
        password_hash=generate_password_hash(data['password'])
    )
    db.session.add(new_user)
    db.session.commit()
    
    # Create access token
    access_token = create_access_token(identity=new_user.id)
    
    return jsonify({
        'message': 'User created successfully',
        'access_token': access_token,
        'user': {
            'id': new_user.id,
            'username': new_user.username,
            'email': new_user.email
        }
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing credentials'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    }), 200

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at.isoformat()
    }), 200

# ========== OBJECTS CRUD ==========
@app.route('/api/objects', methods=['GET'])
@jwt_required()
def get_objects():
    current_user_id = get_jwt_identity()
    objects = RentalObject.query.filter_by(user_id=current_user_id).all()
    
    return jsonify([
        {
            'id': obj.id,
            'address': obj.address,
            'area': obj.area,
            'is_for_sale': obj.is_for_sale,
            'price_total': obj.price_total,
            'rent_per_sqm': obj.rent_per_sqm,
            'profitability': obj.profitability,
            'is_undervalued': obj.is_undervalued,
            'created_at': obj.created_at.isoformat(),
            'updated_at': obj.updated_at.isoformat()
        } for obj in objects
    ]), 200

@app.route('/api/objects', methods=['POST'])
@jwt_required()
def create_object():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('address') or not data.get('area'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    new_object = RentalObject(
        id=str(uuid.uuid4()),
        user_id=current_user_id,
        address=data['address'],
        area=data['area'],
        is_for_sale=data.get('is_for_sale', False),
        price_total=data.get('price_total'),
        rent_per_sqm=data.get('rent_per_sqm'),
        profitability=data.get('profitability', 0.0),
        is_undervalued=data.get('is_undervalued', False)
    )
    
    db.session.add(new_object)
    db.session.commit()
    
    return jsonify({
        'message': 'Object created successfully',
        'object': {
            'id': new_object.id,
            'address': new_object.address,
            'area': new_object.area,
            'is_for_sale': new_object.is_for_sale,
            'price_total': new_object.price_total,
            'rent_per_sqm': new_object.rent_per_sqm,
            'profitability': new_object.profitability,
            'is_undervalued': new_object.is_undervalued
        }
    }), 201

@app.route('/api/objects/<object_id>', methods=['GET'])
@jwt_required()
def get_object(object_id):
    current_user_id = get_jwt_identity()
    obj = RentalObject.query.filter_by(id=object_id, user_id=current_user_id).first()
    
    if not obj:
        return jsonify({'error': 'Object not found'}), 404
    
    return jsonify({
        'id': obj.id,
        'address': obj.address,
        'area': obj.area,
        'is_for_sale': obj.is_for_sale,
        'price_total': obj.price_total,
        'rent_per_sqm': obj.rent_per_sqm,
        'profitability': obj.profitability,
        'is_undervalued': obj.is_undervalued,
        'created_at': obj.created_at.isoformat(),
        'updated_at': obj.updated_at.isoformat()
    }), 200

@app.route('/api/objects/<object_id>', methods=['PUT'])
@jwt_required()
def update_object(object_id):
    current_user_id = get_jwt_identity()
    obj = RentalObject.query.filter_by(id=object_id, user_id=current_user_id).first()
    
    if not obj:
        return jsonify({'error': 'Object not found'}), 404
    
    data = request.get_json()
    
    if 'address' in data:
        obj.address = data['address']
    if 'area' in data:
        obj.area = data['area']
    if 'is_for_sale' in data:
        obj.is_for_sale = data['is_for_sale']
    if 'price_total' in data:
        obj.price_total = data['price_total']
    if 'rent_per_sqm' in data:
        obj.rent_per_sqm = data['rent_per_sqm']
    if 'profitability' in data:
        obj.profitability = data['profitability']
    if 'is_undervalued' in data:
        obj.is_undervalued = data['is_undervalued']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Object updated successfully',
        'object': {
            'id': obj.id,
            'address': obj.address,
            'area': obj.area,
            'is_for_sale': obj.is_for_sale,
            'price_total': obj.price_total,
            'rent_per_sqm': obj.rent_per_sqm,
            'profitability': obj.profitability,
            'is_undervalued': obj.is_undervalued
        }
    }), 200

@app.route('/api/objects/<object_id>', methods=['DELETE'])
@jwt_required()
def delete_object(object_id):
    current_user_id = get_jwt_identity()
    obj = RentalObject.query.filter_by(id=object_id, user_id=current_user_id).first()
    
    if not obj:
        return jsonify({'error': 'Object not found'}), 404
    
    db.session.delete(obj)
    db.session.commit()
    
    return jsonify({'message': 'Object deleted successfully'}), 200

# ========== ANALYTICS ==========
@app.route('/api/analytics/summary', methods=['GET'])
@jwt_required()
def analytics_summary():
    current_user_id = get_jwt_identity()
    objects = RentalObject.query.filter_by(user_id=current_user_id).all()
    
    total_count = len(objects)
    for_sale_count = sum(1 for obj in objects if obj.is_for_sale)
    for_rent_count = total_count - for_sale_count
    undervalued_count = sum(1 for obj in objects if obj.is_undervalued)
    
    avg_profitability = 0
    if total_count > 0:
        avg_profitability = sum(obj.profitability for obj in objects) / total_count
    
    return jsonify({
        'count': total_count,
        'avg_profitability': round(avg_profitability, 2),
        'undervalued_count': undervalued_count,
        'for_sale_count': for_sale_count,
        'for_rent_count': for_rent_count
    }), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
