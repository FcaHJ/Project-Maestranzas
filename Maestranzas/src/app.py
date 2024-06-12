from flask import Flask, render_template, request, redirect, url_for,Response, session, flash, g
from functools import wraps
from flask_mysqldb import MySQL
from config import config
import string, secrets, random


app= Flask(__name__, template_folder='template')
db = MySQL(app)

@app.before_request
def before_request():
    # La función get_logged_in_user() obtiene el usuario actual de la sesión
    g.user = get_logged_in_user()

def get_logged_in_user():
    user_id = session.get('id')
    if user_id:
        cur = db.connection.cursor()
        cur.execute('SELECT * FROM user WHERE id = %s', (user_id,))
        user = cur.fetchone()
        cur.close()
        return user
    return None

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        #print(request.form['username'])
        #print(request.form['password'])
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Por favor, completa todos los campos.')
            return render_template('/login.html')
        
        cur = db.connection.cursor()
        cur.execute('SELECT * FROM user WHERE username=%s AND password=%s', (username,password,))
        account = cur.fetchone()

        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['id_rol'] = account['id_rol']
            session['first_name'] = account['first_name']
            session['username'] = account['username']

            if session['id_rol'] == 1:
                return redirect(url_for('admin'))
            elif session['id_rol'] == 2:
                return redirect(url_for('home'))
            elif session['id_rol'] == 3:
                return redirect(url_for('home'))

        else:
            flash('Usuario o Contraseña incorrecta')
            return render_template('/login.html')
    else:
        return render_template('/login.html', )
#CERRAR SESION
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if 'username' in session:
        return render_template('home.html', first_name=session['first_name'])
    else:
        return redirect(url_for('login'))


@app.route('/admin')
def admin():
    if 'username' in session:
        return render_template('admin.html', first_name=session['first_name'])
    else:
        return redirect(url_for('login'))

@app.route('/registro')
def registro():
    if 'username' in session:
        return render_template('registro.html', first_name=session['first_name'])
    else:
        return redirect(url_for('login'))
    
#LISTAR PRODUCTOS
@app.route('/productos')
def mostrar_producto():
    if 'username' in session:
        categorias = get_categories()
        sort_by = request.args.get('sort_by')
        if sort_by:
            if sort_by == 'nombre':
                order_by_clause = 'ORDER BY nombre'
            elif sort_by == 'descripcion':
                order_by_clause = 'ORDER BY descripcion'
            elif sort_by == 'ubicacion':
                order_by_clause = 'ORDER BY ubicacion'
            elif sort_by == 'cantidad':
                order_by_clause = 'ORDER BY cantidad'
            elif sort_by == 'categoria':
                order_by_clause = 'ORDER BY categoria'

            # Realiza la consulta a la base de datos para obtener los productos ordenados
            cur = db.connection.cursor()
            cur.execute(f'''SELECT p.*, c.descripcion AS categoria_nombre
                    FROM productos p
                    LEFT JOIN categorias c ON p.categoria = c.id_categ {order_by_clause}''')
            productos = cur.fetchall()
            cur.close()
            return render_template('productos.html', first_name=session['first_name'],productos=productos,categorias=categorias)

        else:
            cur = db.connection.cursor()
            cur.execute('''SELECT p.*, c.descripcion AS categoria_nombre
            FROM productos p
            LEFT JOIN categorias c ON p.categoria = c.id_categ''')
            productos = cur.fetchall()
            cur.close()
            return render_template('productos.html', first_name=session['first_name'],productos=productos,categorias=categorias)
    else:
        return redirect(url_for('login'))

#MOSTRAR MODIFICACIONES REALIZADAS
@app.route('/modificaciones')
def mostrar_modificacion():
    if 'username' in session:
        cur = db.connection.cursor()
        cur.execute('SELECT m.*, p.nombre as producto_nombre FROM modificaciones m JOIN productos p ON m.producto_id = p.id ORDER BY m.fecha_hora DESC')
        modificaciones = cur.fetchall()
        cur.close()
        return render_template('modificaciones.html', first_name=session['first_name'],modificaciones=modificaciones)
    else:
        return redirect(url_for('login'))

#LISTAR USUARIOS
@app.route('/usuarios', methods=["GET", "POST"])
def mostrar_usuario():

    if 'username' in session:
        cur = db.connection.cursor()
        cur.execute('SELECT * FROM user')
        usuarios = cur.fetchall()
        cur.close()
        return render_template('usuarios.html', first_name=session['first_name'],usuarios=usuarios)
    else:
        return redirect(url_for('login'))

#REGISTRO DE USUARIOS
@app.route('/crear-registro', methods=['GET', 'POST'])
def crear_registro():
        if request.method == 'POST':
            if 'id_rol' not in request.form:
                flash('El campo "Rol" es obligatorio.', 'danger')
                return render_template('registro.html')
            
            id_rol = request.form['id_rol']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            run = request.form['run']

            # Verificar si se han dejado campos en blanco
            if not first_name or not last_name or not run:
                flash('Por favor, completa todos los campos.', 'danger')
                return render_template('registro.html')
            try:
                rut = format_rut(run)
            except ValueError as e:
                flash(str(e))
                return redirect(url_for('registro'))
        
            password = generate_password()

            #Creacion del nombre de usuario con 3 primeras letras del nombre y apellido completo
            username = f"{first_name[:3].lower()}.{last_name.lower()}"
            
            cur = db.connection.cursor()
            cur.execute('INSERT INTO user(id_rol, username, password, first_name, last_name, run) VALUES(%s,%s,%s,%s,%s,%s)',
                        (id_rol,username,password,first_name, last_name, rut))
            db.connection.commit()
            cur.close()

            flash('Usuario creado!', 'success')
            return render_template('registro.html')
        return render_template('registro.html')

#Funcion para la generacion de contraseña 
def generate_password(min_length=8, max_length=12):
    # Define los caracteres que se pueden usar en la contraseña, en este caso, letras y numeros
    characters = string.ascii_letters + string.digits
    length = random.randint(min_length, max_length)
    # Genera una contraseña aleatoria
    password = ''.join(secrets.choice(characters) for i in range(length))
    return password

#Formato del rut
def format_rut(run):
    rut_str = str(run)

    # Valida que el RUT tenga entre 8 y 9 caracteres numéricos
    if not rut_str.isdigit() or not (8 <= len(rut_str) <= 9):
        raise ValueError("El RUT debe ser numérico y tener entre 8 y 9 dígitos")

    # Formatear RUT
    formatted_rut = f"{rut_str[:-7]}.{rut_str[-7:-4]}.{rut_str[-4:-1]}-{rut_str[-1]}"
    return formatted_rut

#EDITAR USUARIO
@app.route('/editar_usuario/<int:id>', methods=['POST'])
def edit_user(id):

        id_rol = request.form['editIdRol']
        username = request.form['editUsername']
        first_name = request.form['editName']
        last_name = request.form['editLastName']
        run = request.form['editRut']

        generate_password_flag = request.form.get('generatePassword')
        if generate_password_flag:
            password = generate_password()
            cur = db.connection.cursor()
            cur.execute('UPDATE user SET id_rol = %s, username = %s, first_name = %s, last_name = %s, run = %s, password = %s WHERE id = %s',
                    (id_rol, username, first_name, last_name, run, password, id))
        else:
            cur = db.connection.cursor()
            cur.execute('UPDATE user SET id_rol = %s, username = %s, first_name = %s, last_name = %s, run = %s WHERE id = %s',
                (id_rol, username, first_name, last_name, run, id))
            
        db.connection.commit()
        cur.close()

        flash(f'Usuario {first_name} Modificado!')
        return redirect(url_for('mostrar_usuario'))

#ELIMINAR USUARIO
@app.route('/eliminar_usuario/<int:id>', methods=['POST'])
def delete_user(id):
        
        cur = db.connection.cursor()
        cur.execute('DELETE FROM user WHERE id=%s', (id,))
        db.connection.commit()
        cur.close()

        flash(f'Usuario ID: {id} Eliminado')
        return redirect(url_for('mostrar_usuario'))

#BUSCAR PRODUCTOS /ARREGLAR
@app.route('/buscar-producto', methods=['GET', 'POST'])
def buscar_producto():
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        if search_query:
            # Realiza la consulta a la base de datos para buscar productos por nombre o descripcion
            cur = db.connection.cursor()
            cur.execute("SELECT * FROM productos WHERE nombre LIKE %s OR descripcion LIKE %s", 
                        ('%' + search_query + '%', '%' + search_query + '%'))
            productos = cur.fetchall()
            cur.close()
            return render_template('productos.html',  first_name=session['first_name'],productos=productos, search_query=search_query)
        else:
            return redirect(url_for('mostrar_producto'))
    return redirect(url_for('mostrar_producto'))

#AGREGAR PRODUCTOS
@app.route('/agregar_productos', methods=['GET', 'POST'])
def add_product():
        
        if request.method == 'POST':
            if 'addCategoria' not in request.form:
                flash('Seleccione opcion en el campo "Categoria".', 'danger')
                return redirect(url_for('mostrar_producto'))

            
            nro_serie = request.form['addNroSerie']
            nombre = request.form['addNombre']
            descripcion = request.form['addDescripcion']
            ubicacion = request.form['addUbicacion']
            cantidad = request.form['addCantidad']
            categoria = request.form['addCategoria']

            # Verificar si se han dejado campos en blanco
            if not nro_serie or not nombre or not descripcion or not ubicacion or not cantidad:
                flash('Por favor, completa todos los campos.', 'danger')
                return redirect(url_for('mostrar_producto'))

            
            cur = db.connection.cursor()
            cur.execute('INSERT INTO productos(nro_serie, nombre, descripcion, ubicacion, cantidad, categoria) VALUES(%s,%s,%s,%s,%s,%s)',
                        (nro_serie,nombre,descripcion,ubicacion,cantidad, categoria))
            db.connection.commit()
            cur.close()

            flash('Producto agregado!')
            return redirect(url_for('mostrar_producto'))

        return render_template('productos.html')

# Función para obtener categorías
def get_categories():
    cur = db.connection.cursor()
    cur.execute('SELECT * FROM categorias')
    categorias = cur.fetchall()
    cur.close()
    return categorias

#EDITAR PRODUCTOS
@app.route('/editar_producto/<int:id>', methods=['POST'])
def edit_product(id):

        nro_serie = request.form['editNroSerie']
        nombre = request.form['editNombre']
        descripcion = request.form['editDescripcion']
        ubicacion = request.form['editUbicacion']
        cantidad = request.form['editCantidad']
        categoria = request.form['editCategoria']

        # Obtener el nombre de la nueva categoría
        cur = db.connection.cursor()
        cur.execute('SELECT descripcion FROM categorias WHERE id_categ = %s', (categoria,))
        categoria_nombre = cur.fetchone()['descripcion']
        cur.close()

        #Obtiene usuario actual
        user_id = session['id']
        username = session['username']

        #Registrar modificacion en la base de datos
        cur = db.connection.cursor()
        cur.execute('UPDATE user SET nro_serie = %s, nombre = %s, descripcion = %s, ubicacion = %s, cantidad = %s,categoria = %s WHERE id = %s',
                (nro_serie, nombre, descripcion, ubicacion, cantidad, categoria, id))
        db.connection.commit()

        #Insertar datos de la modificacion
        cur = db.connection.cursor()
        cur.execute('INSERT INTO modificaciones', (id, user_id, username, ))
        db.connection.commit()
        cur.close()

        flash('Producto Modificado!')
        return redirect(url_for('mostrar_producto'))

if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.run()