
from Conexion import conectar;

import requests

#===========================FUNCIONES DE IMPLEMENTACIÓN DEL MODELO===========================
#URL = "http://127.0.0.1:8000/pronostico"
#registro = requests.get(url = URL)

def consulta_pronostico():
    con = conectar()
    cursor = con.cursor() 
    consulta = "SELECT * from parametros order by id desc limit 100"
    cursor.execute(consulta)
    registro=cursor.fetchall()
    con.commit()
    cursor.close()
    con.close()
    return registro


def almacenar_prediccion(datos):
    data=datos
    temp= data[0]
    o = data[1]
    t = data[2]
  
    con = conectar()
    cursor = con.cursor() 
    #Crear y ejecutar consulta
    consulta = "INSERT INTO prediccion(oxigeno, temperatura, tiempo) VALUES('{0}', '{1}', '{2}')".format(o, temp, t) 
    cursor.execute(consulta)
    #Hacer cambios en la base de datos
    con.commit()
    #Cerrar cursor y conexión
    cursor.close()
    con.close()
    
def actualizar_prediccion():
    con = conectar()
    cursor = con.cursor() 
    consulta = "SELECT * from prediccion order by id desc limit 10;"
    cursor.execute(consulta)
    registro=cursor.fetchall()
    con.commit()
    cursor.close()
    con.close()
    return registro




