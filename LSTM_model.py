# import tensorflow as tf #for Tflite
import pickle  #for pickle

#import python modules
import sqldb

#declare global variables
input_details=''
output_details=''
interpreter=''

#laod Tfliteor Pickle model when app starts (will be load only once for speed prediction)
def lstm_model_load():
    # global input_details
    # global output_details
    global interpreter
    #---------------TFlite model---------------------#
    # interpreter = tf.lite.Interpreter(model_path="LSTM_model.tflite")
    # interpreter.allocate_tensors()

    # input_details = interpreter.get_input_details()
    # output_details = interpreter.get_output_details()
    # input_details[0]['shape'] #to ckeck required input shape
    #---------------TFlite model---------------------#

    #---------------Pickel model---------------------#
    with open('LSTM_model_pickle','rb') as f: #wb--> read byte 
        interpreter = pickle.load(f)
    #---------------Pickel model---------------------#


#activity prediction using LSTM model
def predict():
    reshaped_acc = sqldb.last_n_rows_acc(8) #get lastest 8 rows values of acceleration in required shape LSTM (1,8,3), Tx=8

    #---------------Tflite model---------------------#
    # interpreter.set_tensor(input_details[0]['index'], reshaped_acc) #Feeding acc values for predition
    # interpreter.invoke()
    # output_data = interpreter.get_tensor(output_details[0]['index']) #Store activity prediction as probability %
    #---------------Tflite model---------------------#

    #---------------Pickel model---------------------#
    output_data=interpreter.predict(reshaped_acc)  #Store activity prediction as probability %
    #---------------Pickel model---------------------#

    Predicted_Class = Return_Class(output_data) #getting the activity type
    return Predicted_Class #Returning the final Class of prediction

#Return the class with the highest probability
def Return_Class(output_data):
    import numpy as np #numpy is required for argmax fncn
    real_pred = np.argmax(output_data) #return indice number with highest probabilty
    if real_pred==0:
        return 'Running'
    elif real_pred==1:
        return 'Sitting'
    elif real_pred==2:
        return 'Walking'

   
