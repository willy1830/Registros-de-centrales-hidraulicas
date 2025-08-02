import sqlite3
from flask import Flask, g, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)
DATABASE = 'registros.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registros_hidraulicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                central TEXT NOT NULL,
                presion REAL NOT NULL,
                temperatura REAL NOT NULL,
                observaciones TEXT
            );
        ''')
        db.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/registros', methods=['POST'])
def guardar_registro():
    data = request.get_json()
    fecha = data.get('fecha')
    try:
        datetime.strptime(fecha, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Formato de fecha inválido'}), 400

    campos = ('fecha','central','presion','temperatura','observaciones')
    valores = tuple(data.get(c) for c in campos)

    db = get_db()
    cursor = db.cursor()
    cursor.execute(f'''
        INSERT INTO registros_hidraulicos ({','.join(campos)})
        VALUES (?,?,?,?,?);
    ''', valores)
    db.commit()

    return jsonify({'status': 'ok', 'id': cursor.lastrowid}), 201

if __name__ == '__main__':
    init_db()
    app.run(debug=True)