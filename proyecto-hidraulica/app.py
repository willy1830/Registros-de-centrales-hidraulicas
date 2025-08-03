import os
from datetime import datetime

from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# Importa psycopg para que registre el dialecto “psycopg” en SQLAlchemy
import psycopg  

app = Flask(__name__)

def get_database_uri():
    url = os.getenv('DATABASE_URL')
    if not url:
        # Caída a SQLite para desarrollo local
        return 'sqlite:///registros.db'
    # Heroku style: postgres:// → postgresql+psycopg://
    if url.startswith('postgres://'):
        url = url.replace('postgres://',
                          'postgresql+psycopg://', 1)
    # postgresQL standard: postgresql:// → postgresql+psycopg://
    elif url.startswith('postgresql://'):
        url = url.replace('postgresql://',
                          'postgresql+psycopg://', 1)
    return url

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de datos
class Registro(db.Model):
    __tablename__ = 'registros_hidraulicos'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    central = db.Column(db.String(100), nullable=False)
    presion = db.Column(db.Float, nullable=False)
    temperatura = db.Column(db.Float, nullable=False)
    observaciones = db.Column(db.Text)

# Crear las tablas antes de la primera petición
@app.before_first_request
def init_db():
    db.create_all()

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# API para guardar registros
@app.route('/api/registros', methods=['POST'])
def guardar_registro():
    data = request.get_json()
    fecha_str = data.get('fecha')
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return jsonify({'error': 'Formato de fecha inválido'}), 400

    registro = Registro(
        fecha=fecha,
        central=data.get('central'),
        presion=data.get('presion'),
        temperatura=data.get('temperatura'),
        observaciones=data.get('observaciones')
    )
    db.session.add(registro)
    db.session.commit()

    return jsonify({'status': 'ok', 'id': registro.id}), 201

if __name__ == '__main__':
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=debug
    )
