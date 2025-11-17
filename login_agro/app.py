from flask import Flask, render_template, request, redirect, session, jsonify 
from flask import render_template, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'miclave123'

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="agroquimica"
    )

@app.route('/')
def index():
    session.clear()
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    mensaje = ''
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s AND contrasena = %s", (usuario, contrasena))
        user = cursor.fetchone()
        cursor.close()
        db.close()
        if user:
            session['usuario'] = usuario
            session['rol'] = user['rol']  
            return redirect('/menu')
        else:
            mensaje = 'Usuario o contraseña incorrectos'
    return render_template('login.html', mensaje=mensaje)

@app.route('/menu')
def menu():
    if 'usuario' not in session:
        return redirect('/login')
    return render_template('menu.html', usuario=session['usuario'], rol=session.get('rol'))

@app.route('/productos')
def productos():
    if 'usuario' not in session:
        return redirect('/login')
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT p.id, p.nombre, p.descripcion, p.precio, p.stok, p.icono, c.nombre AS categoria, p.categoria_id
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
    """)
    productos = cursor.fetchall()
    
    cursor.execute("SELECT * FROM categorias")
    categorias = cursor.fetchall()
    cursor.close()
    db.close()
    
 
    return render_template(
        'productos.html',
        usuario=session['usuario'],
        rol_usuario=session.get('rol'),  
        productos=productos,
        categorias=categorias
    )

@app.route('/productos/agregar', methods=['POST'])
def agregar_producto():
    if 'usuario' not in session:
        return jsonify({"success": False, "error": "No autorizado"})
    if session.get('rol') not in ['administrador', 'vendedor']:
        return jsonify({"success": False, "error": "No tiene permiso para agregar"})

    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    categoria_id = request.form['categoria']
    precio = request.form['precio']
    stok = request.form['stok']
    icono = request.form['icono']
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        INSERT INTO productos (nombre, descripcion, categoria_id, precio, stok, icono)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (nombre, descripcion, categoria_id, precio, stok, icono))
    db.commit()

    cursor.execute("""
        SELECT p.id, p.nombre, p.descripcion, p.precio, p.stok, p.icono, c.nombre AS categoria
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
    """)
    productos = cursor.fetchall()
    cursor.close()
    db.close()

    return jsonify({"success": True, "productos": productos})

@app.route('/productos/modificar/<int:id>', methods=['POST'])
def modificar_producto(id):
    if 'usuario' not in session:
        return jsonify({"success": False, "error": "No autorizado"})
    if session.get('rol') not in ['administrador', 'vendedor']:
        return jsonify({"success": False, "error": "No tiene permiso para modificar"})

    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    categoria_id = request.form['categoria']
    precio = request.form['precio']
    stok = request.form['stok']
    icono = request.form['icono']

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        UPDATE productos
        SET nombre=%s, descripcion=%s, categoria_id=%s, precio=%s, stok=%s, icono=%s
        WHERE id=%s
    """, (nombre, descripcion, categoria_id, precio, stok, icono, id))
    db.commit()

    cursor.execute("""
        SELECT p.id, p.nombre, p.descripcion, p.precio, p.stok, p.icono, c.nombre AS categoria
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
    """)
    productos = cursor.fetchall()
    cursor.close()
    db.close()

    return jsonify({"success": True, "productos": productos})

@app.route('/productos/eliminar/<int:id>', methods=['POST'])
def eliminar_producto(id):
    if 'usuario' not in session:
        return jsonify({"success": False, "error": "No autorizado"})
    if session.get('rol') != 'administrador':
        return jsonify({"success": False, "error": "Solo el administrador puede eliminar"})

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("DELETE FROM productos WHERE id=%s", (id,))
    db.commit()

    cursor.execute("""
        SELECT p.id, p.nombre, p.descripcion, p.precio, p.stok, p.icono, c.nombre AS categoria
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
    """)
    productos = cursor.fetchall()
    cursor.close()
    db.close()

    return jsonify({"success": True, "productos": productos})

@app.route('/productos/detalle/<int:id>')
def detalle_producto(id):
    if 'usuario' not in session:
        return redirect('/login')
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.id, p.nombre, p.descripcion, p.precio, p.stok, p.icono, c.nombre AS categoria
        FROM productos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        WHERE p.id=%s
    """, (id,))
    producto = cursor.fetchone()
    cursor.close()
    db.close()

    if not producto:
        return "Producto no encontrado", 404

    return render_template('detalle.html', producto=producto, rol=session.get('rol'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/categorias')
def categorias():
    if 'usuario' not in session:
        return redirect('/login')
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM categorias")
    categorias = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('categorias.html', categorias=categorias, usuario=session['usuario'], rol=session.get('rol'))

@app.route('/categorias/agregar', methods=['POST'])
def agregar_categoria():
    if 'usuario' not in session:
        return jsonify({"success": False, "error": "No autorizado"})
    if session.get('rol') != 'administrador':
        return jsonify({"success": False, "error": "Solo el administrador puede agregar categorías"})
    
    nombre = request.form['nombre']
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("INSERT INTO categorias (nombre) VALUES (%s)", (nombre,))
    db.commit()
    cursor.close()
    db.close()

    return jsonify({"success": True})

@app.route('/categorias/eliminar/<int:id>', methods=['POST'])
def eliminar_categoria(id):
    if 'usuario' not in session:
        return jsonify({"success": False, "error": "No autorizado"})
    if session.get('rol') != 'administrador':
        return jsonify({"success": False, "error": "Solo el administrador puede eliminar categorías"})
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("DELETE FROM categorias WHERE id=%s", (id,))
    db.commit()

    cursor.execute("SELECT * FROM categorias")
    categorias = cursor.fetchall()
    cursor.close()
    db.close()

    return jsonify({"success": True, "categorias": categorias})

if __name__ == '__main__':
    app.run(debug=True)
    