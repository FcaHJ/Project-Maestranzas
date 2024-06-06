from flask import Flask, render_template, request, redirect, url_for,Response, session, flash
from functools import wraps
from flask_mysqldb import MySQL, MySQLdb
from config import config
import string, secrets, random


app= Flask(__name__, template_folder='template')
db = MySQL(app)

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
        
        cur = db.connection.cursor()
        cur.execute('SELECT * FROM user WHERE username=%s AND password=%s', (username,password,))
        account = cur.fetchone()

        if account:
            session['logueado'] = True
            session['id'] = account[0]
            session['id_rol'] = account[1]
            session['first_name'] = account[4]
            session['username'] = account[2]
            session['user_data'] = account

            if session['id_rol'] == 1:
                return redirect(url_for('admin'))
            elif session['id_rol'] == 2:
                return redirect(url_for('home'))

        else:
            flash('Usuario o Contraseña incorrecta')
            return render_template('/login.html')
    else:
        return render_template('/login.html', )
    
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

@app.route('/productos')
def producto():
    if 'username' in session:
        return render_template('productos.html', first_name=session['first_name'])
    else:
        return redirect(url_for('login'))

@app.route('/modificaciones')
def modificacion():
    if 'username' in session:
        return render_template('modificaciones.html', first_name=session['first_name'])
    else:
        return redirect(url_for('login'))

#Arreglar
@app.route('/usuarios',methods=["GET", "POST"])
def mostrar_usuario():

    cur = db.connection.cursor()
    cur.execute('SELECT * FROM user')
    usuarios = cur.fetchall()
    cur.close()
    #user_data = session['user_data']
    if 'username' in session:
        return render_template('usuarios.html', first_name=session['first_name'],usuarios=usuarios)
    else:
        return redirect(url_for('login'))

@app.route('/crear-registro', methods=['GET', 'POST'])
def crear_registro():

        id_rol = request.form['id_rol']
        password = generate_password()
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        if first_name and last_name:
            #Creacion del nombre de usuario con 1era letra del nombre y apellido completo
            username = f"{first_name[0].lower()}{last_name.lower()}"

        cur = db.connection.cursor()
        cur.execute('INSERT INTO user(id_rol, username, password, first_name, last_name) VALUES(%s,%s,%s,%s,%s)',(id_rol,username,password,first_name, last_name))
        db.connection.commit()
        cur.close()

        flash('Usuario creado!')
        return render_template('registro.html')

#Funcion para la generacion de contraseña 
def generate_password(min_length=8, max_length=12):
    # Define los caracteres que se pueden usar en la contraseña, en este caso, letras y numeros
    characters = string.ascii_letters + string.digits
    length = random.randint(min_length, max_length)
    # Genera una contraseña aleatoria
    password = ''.join(secrets.choice(characters) for i in range(length))
    return password

if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.run()