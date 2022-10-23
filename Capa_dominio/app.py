import datetime
import email
from email.policy import default
from runpy import run_path
import numpy as np
from flask import Flask, jsonify, request, render_template
from flask import redirect, url_for, flash
from Prediccion import almacenar_prediccion
from Validaciones import contrasena_val, email_val
from Prediccion import actualizar_prediccion, consulta_pronostico
from Usuarios import Usuario
from Notificacion import detectar_condicion, consulta_email
from Monitoreo import actualizacion, almacenamiento
from Validaciones import acceso_val, registro_val
from flask_mail import Mail, Message
import json
from flask_cors import CORS, cross_origin
import requests

acceso=False

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = '\xa6\x8b\xafF\xee\x81\xaa\x0e\xb8/\xd4H\xdb\xff\x9b\x19g+sM\x8dQ\xda\x05'
app.config['MAIL_SERVER']= 'smtp.gmail.com'
app.config['MAIL_PORT']=587
app.config['MAIL_USERNAME']='monitoreoapp.service@gmail.com'
app.config['MAIL_PASSWORD']='udkqdqvpwtxnvdcz'
app.config['MAIL_DEFAULT_SENDER']= 'monitoreoapp.service@gmail.com'
app.config['MAIL_USE_TLS']=True

mail= Mail(app)

#==================================RUTAS=======================================
# en esta ruta llegaan los datos desde la aplicación movil
@app.route("/hola", methods=['POST', 'GET'])
def recibir_datos():
	msg = request.get_data()
	#data = msg
	js = json.loads(msg.decode("utf-8"))
	for dato in js:
		almacenamiento(dato)
		resultado = detectar_condicion(dato)
		mensaje(resultado)

	return "todo correcto"
def recibir_pronostico():
	#URL = "http://127.0.0.1:8000/pronostico"
	#registro = requests.get(url = URL)
	pronostico= request.get_data()
	js = json.loads(pronostico.decode("utf-8"))
	for dato in js:
		almacenar_prediccion(dato)
	return "Todo correcto"

@app.route("/datos_pronostico", methods=['POST', 'GET'])
def recibir_pronostico():
	datos = consulta_pronostico()
	o =[]
	t = []
	f=[]
	for dato in datos:
		o.append(dato[1])
		t.append(dato[2])
		f.append(dato[5].strftime('%d/%m/%Y %H:%M:%S'))
	data = {
	"oxigeno": o,
	"temperatura": t,
	"fecha": f
    }
	print(f)  

	return jsonify(data)

@cross_origin
@app.route('/inicio/', methods=['POST', 'GET'])
def inicio():
	return render_template('index.html')
	
@cross_origin
@app.route('/monitoreo/', methods=['POST', 'GET'])
def graficar_m():
	registro = actualizacion()
	print(registro)
	o =[]
	t = []
	h = []
	f=[]
	for dato in registro:
		o.append(dato[1])
		t.append(dato[2])
		h.append(dato[5].strftime('%H:%M:%S'))
		f.append(dato[5].strftime('%d/%m/%Y'))
	o_reverse= o[::-1]
	t_reverse= t[::-1]
	h_reverse= h[::-1]
	f_reverse= f[::-1]
	print(h)
	print(h_reverse)

	data = {
	"oxigeno": o_reverse,
	"temperatura": t_reverse,
	"hora": h_reverse,
	"fecha": f_reverse
    }
	return jsonify(data)
	
@cross_origin
@app.route('/predecir/', methods=['POST', 'GET'])
def graficar_prediccion():
	registro = actualizar_prediccion()
	o =[]
	t = []
	h = []
	f=[]
	for dato in registro:
		o.append(dato[1])
		t.append(dato[2])
		h.append(dato[5].strftime('%H:%M:%S'))
		f.append(dato[5].strftime('%d/%m/%Y'))
	o_reverse= o[::-1]
	t_reverse= t[::-1]
	h_reverse= h[::-1]
	f_reverse= f[::-1]
	print(h)
	print(h_reverse)

	data = {
	"oxigeno": o_reverse,
	"temperatura": t_reverse,
	"hora": h_reverse,
	"fecha": f_reverse
    }
	return jsonify(data)


#===============================Rutas usuarios====================================
@app.route("/", methods=['POST', 'GET'])
def acceder():
	print('hola')
	
	global acceso
	form = acceso_val()

	if request.method == 'POST': 
		usuario = form.usuario.data
		contrasena = form.contrasena.data
		u = Usuario('','', '', usuario, contrasena)
		acceso = u.acceso()
		print('datos usuario: ', acceso)
		#user=u.get_id()
		#print (user)
		if  acceso == True:
			
			return redirect(url_for('inicio'))
		else: print('Acceso incorrecto')
		flash('¡Acceso incorrecto! verifique que el usuario y la contraseña coincidan')
	
	return render_template('login.html', form=form)

@app.before_request
def login():
	global acceso
	print('esto es la ruta', request.path)
	path=request.path
	if path == '/' or  path == '/inicio/':
		print('el acceso es: ', acceso)
		if request.path != '/':
			print('No estas en login')
			
			print('esto es la ruta', request.path)
			if  acceso == False:
				
				return redirect(url_for('acceder'))
		else: print('estas en login')


@app.route('/Registro', methods = ['POST', 'GET'])
def registrar():
	form = registro_val()
	if request.method == 'POST':
		nombre = form.nombre.data
		email = form.email.data.lower()
		usuario = form.usuario.data.lower()
		contrasena = form.contrasena.data
		
		u = Usuario('', nombre, email, usuario, contrasena)
		registro = u.registro()
		
		if registro == True:
			return redirect(url_for('acceder'))
		else:
			print ('El nombre de usuario o el email ya se han registrado')
			flash('El nombre de usuario o email ya han sido registrados')
			return render_template('Registro.html', form=form)
	
	return render_template('Registro.html', form=form)

@app.route('/Restablecer_contrasena', methods = ['POST', 'GET'])
def formulario_contrasena():
	form = contrasena_val()
	if request.method =='POST':
		email= form.email.data
		contrasena=form.contrasena.data
		nueva_contrasena = form.confirmacion.data
		if nueva_contrasena == contrasena:
			u=Usuario('', '', email, '', contrasena)
			u.actualizar_contrasena()
			flash('La contraseña fue restablecida')
			return redirect(url_for('acceder'))
		else: 
			flash('Las contraseñas no coinciden')
	return render_template('Restablecer_contrasena.html', form=form)

@app.route('/Cambio_de_contrasena', methods = ['POST', 'GET'])
def restablecer_contrasena():
	form = email_val()
	if request.method =='POST':
		destinatario=[]
		email= form.email.data
		u=Usuario('', '', email, '', '')
		destinatario.append(email)
		print(destinatario)
	
		if u.verificar_email():
			mensaje_contrasena(destinatario)
			flash('Se ha enviado un mensaje a tu correo electrónico con el link para restablecer la contraseña')
		else:
			flash('El correo proporcionado no se encuentra registrado en el sistema')
	return render_template('Cambio_de_contrasena.html', form=form)	
#=============================================ALERTAS=======================================
def mensaje(resultado):
	if len(resultado) > 0: 
		r=str(resultado).replace('[','').replace(']','').replace('{','').replace('}','').replace("'",'')
		print(r)
		with mail.connect() as conn:
			subj = "Alerta"
			msg = Message(recipients=consulta_email(),  subject=subj)
			msg.html =(f'<b>Se han detectado valores fuera de rango</b><br><br>{r}<br><b> <br>Consulta más información </b><A HREF="https://iotacuicola.herokuapp.com/">aquí.</A>')
			conn.send(msg) 

def mensaje_contrasena(destinatario):

	with mail.connect() as conn:
		subj = "Restablecer contraseña"
		msg = Message(recipients=destinatario,  subject=subj)
		msg.html =('Has solicitado restablecer la contraseña de tu cuenta de MonitoreoApp. Ingresa <A HREF="https://iotacuicola.herokuapp.com/Restablecer_contrasena">aquí </A>para continuar.')
		conn.send(msg)

if __name__ == "__main__":
	#debug=True para no tener que estar reiniciando el servidor cada que se actualice algo
	#socketio.run(app, host="https://iotacuicola.herokuapp.com", port=8000, debug=True)
    app.run(debug=True, port=8000)

