
from datetime import date, timedelta
from Conexion import conectar;
from datetime import datetime
import tensorflow as tf
from tensorflow import keras
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import pandas as pd
import numpy as np

#===========================FUNCIONES DE IMPLEMENTACIÓN DEL MODELO===========================
def consulta():
    con = conectar()
    cursor = con.cursor() 
    consulta = "SELECT * from parametros order by id desc limit 100"
    cursor.execute(consulta)
    registro=cursor.fetchall()
    con.commit()
    cursor.close()
    con.close()
    return registro

def pronostico(modelo, datos, wlength, pasos, scaler_t, scaler_o, tiempo_f):
    x=datos[-wlength:]
    count=0
    while count<=pasos-1:    
        prediccion=modelo.predict(x)
        print(prediccion)
        xnew=np.delete(x[0], 0, axis=0)
        xnew=np.append(xnew, prediccion)
        xnew.shape=(1, 100, 2)
        x=xnew
        temperatura_pred = prediccion[:, 0].reshape(-1,1)
        oxigeno_pred = prediccion[:, 1].reshape(-1,1)
        temp_pred_inverse = scaler_t.inverse_transform(temperatura_pred)
        oxg_pred_inverse = scaler_o.inverse_transform(oxigeno_pred)
        incremento = timedelta(minutes=5)
        tiempo_f+=incremento
        temp=temp_pred_inverse[0,0]
        oxig=oxg_pred_inverse[0,0]
        almacenar_prediccion(oxig, temp, tiempo_f)
        count+=1


def almacenar_prediccion(o, temp, t):
  
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
#==========================IMPLEMENTACIÓN DEL MODELO======================================

new_model = tf.keras.models.load_model('modelo_gru_2.h5')
new_model.summary()

oxg=[]
temp=[]
tiempo=[]
registro=consulta()

datos= registro[::-1]
for dato in datos:
    oxg.append(dato[1])
    temp.append(dato[2])
    tiempo.append(dato[5])

d={'oxigeno': oxg, 'temperatura': temp, 'tiempo': tiempo}
d_pred = pd.DataFrame(data=d)
print(d_pred.head())
tiempo_f=tiempo[99]
# Se calcula los valores máximos y mínimos de la media 
up_o = d_pred['oxigeno'].mean() + 2.1*d_pred['oxigeno'].std()
low_o = d_pred['oxigeno'].mean() - 2.1*d_pred['oxigeno'].std()
# Se determina cuales valores se salen de esos rangos y se reemplazan por interpolación
d_pred.loc[d_pred['oxigeno'] > up_o, 'oxigeno'] = np.nan
d_pred.loc[d_pred['oxigeno'] < low_o, 'oxigeno'] = np.nan
d_pred['oxigeno'].interpolate(inplace=True)
print(d_pred.head())

# Se calcula los valores máximos y mínimos de la media  
up_t = d_pred['temperatura'].mean() + 2.1*d_pred['temperatura'].std()
low_t = d_pred['temperatura'].mean() - 2.1*d_pred['temperatura'].std()
# Se determina cuales valores se salen de esos rangos y se reemplazan por interpolación
d_pred.loc[d_pred['temperatura'] > up_t, 'temperatura'] = np.nan
d_pred.loc[d_pred['temperatura'] < low_t, 'temperatura'] = np.nan
d_pred['temperatura'].interpolate(inplace=True)

print(d_pred.head())
# Genarar un nuevo dataframe con los valores actualizados del pre-procesamiento
'''d= {'tiempo': d_pred['tiempo'],  'temperatura':d_pred['oxigeno'], 'oxigeno': d_pred['temperatura']}
data = pd.DataFrame(data=d)
print(data.head)'''
# Covertir los valores a numpy array y la forma para su correcto procesamiento
temperatura_pred = np.array(d_pred['temperatura'])
oxigeno_pred = np.array(d_pred['oxigeno'])

temp=temperatura_pred.reshape(-1,1)
oxig=oxigeno_pred.reshape(-1,1)

print(temp.shape)
print(oxig.shape)

# Definir los rangos para cada variable 
scaler_t = MinMaxScaler(feature_range = (0,1))
scaler_o = MinMaxScaler(feature_range = (0,1))
# Ajustar el scaler usando los datos de entrenamiento
input_scaler_t = scaler_t.fit(temp)
input_scaler_o = scaler_o.fit(oxig)
# Aplicar el scaler a los datos de entrenamiento
pred_norm_t = input_scaler_t.transform(temp)
pred_norm_o = input_scaler_o.transform(oxig)

df_norm={'oxigeno': pred_norm_t.reshape(-1), 'temperatura': pred_norm_o.reshape(-1)}
X_norm = pd.DataFrame(data=df_norm)

X_array=np.array(X_norm)
X_array.shape=(1, 100, 2)

def result_pronostico():
   pronostico(new_model, X_array, 100, 10, scaler_t, scaler_o, tiempo_f)
   



