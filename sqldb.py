#Pyhton libraries
import datetime
import sqlite3 as sql
import numpy as np

today = datetime.datetime.now()

#User and acc db: Creates new DBs for user and accelarometer values
def create_main_db():

    conn = sql.connect('data.db')
    c = conn.cursor()
    #create table for users data
    c.execute("""CREATE TABLE if not exists users(
        CUser text,
        CPass text,
        Name text,
        Age text,
        Weight text,
        Height text,
        Job text
        )
        """)
    #create table for acceleration data
    c.execute("""CREATE TABLE if not exists acc_xyz(
        date text,
        time text,
        X_val float,
        Y_val float,
        Z_val float
        )
        """)
    c.execute("""CREATE TABLE if not exists activity(
        date text,
        time text,
        u_name text,
        prediction text
        )
        """)
    conn.commit()
    conn.close()

#User db: Returns number of rows
def get_count_row_users(col_name):

    conn = sql.connect('data.db')
    c = conn.cursor()
    c.execute('SELECT COUNT({}) from users'.format(col_name))
    result = c.fetchone()
    n_rows =result[0]
    conn.commit()
    conn.close()
    return n_rows

#User db: getting row item in selected column
def get_items_users(item_name):

    conn = sql.connect('data.db')
    c = conn.cursor()   
    c.execute('SELECT {} FROM users'.format(item_name))
    record = c.fetchall()
    conn.commit()
    conn.close()
    return record

#User db: Inserts data of particular column of users table
def insert_items_user(cipher_username,cipher_pass,cipher_name,cipher_age,cipher_weight,cipher_height,cipher_job):
    conn = sql.connect('data.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (CUser,CPass,Name,Age,Weight,Height,Job) VALUES(?,?,?,?,?,?,?)", 
        (cipher_username,cipher_pass,cipher_name,cipher_age,cipher_weight,cipher_height,cipher_job)
        )
    conn.commit()
    conn.close()

#User db: Inserts data of particular rowid of users table
def save_data_ids(cipher_name,cipher_age,cipher_weight,cipher_height,cipher_job,row_id):
    conn = sql.connect('data.db')
    c = conn.cursor()
    c.execute ('UPDATE users SET Name=?,Age=?,Weight=?,Height=?,Job=? WHERE rowid = ?',
    (cipher_name,cipher_age,cipher_weight,cipher_height,cipher_job,row_id)
    )
    conn.commit()
    conn.close()

#Acc db: Returns column number from accelerometer db
def get_items_acc(item_name):

    conn = sql.connect('data.db')
    c = conn.cursor()   
    c.execute('SELECT {} FROM acc_xyz'.format(item_name))
    Record = c.fetchall()
    conn.commit()
    conn.close()
    return Record

#Acc db: Inserts data of particular column into accelerometer db
def insert_acc(X_val,Y_val,Z_val):
    global today
    time = today.strftime("%H:%M:%S")
    date = today.strftime("%d,%m,%Y")
    conn = sql.connect('data.db')
    c = conn.cursor()
    c.execute("INSERT INTO acc_xyz (date,time,X_val,Y_val,Z_val) VALUES(?,?,?,?,?)", 
        (date,time,X_val,Y_val,Z_val)
        )
    conn.commit()
    conn.close()

#Acc db: fetch accelerometer data
def last_n_rows_acc(num_rows):
    conn = sql.connect('data.db')
    c = conn.cursor()
    c.execute("SELECT X_val,Y_val,Z_val FROM acc_xyz ORDER BY rowid DESC LIMIT {}".format(num_rows))
    acc_data = c.fetchall()
       
    #Coverting Data which is compatible with input of GRU model
    x=[]
    y=[]
    z=[]
    acc_record=[]
    for i in range(0,num_rows):

        xs = acc_data[i][0]
        ys = acc_data[i][1]
        zs = acc_data[i][2]
        x.append(xs)
        y.append(ys)
        z.append(zs)
        
    acc_record.append([x, y, z]) #3D shape array
    acc_record = np.array(acc_record, dtype=np.float32) #Converting to 3D npArray with dtype=32
    #Reshaping accelerometer data which compatible with my GRU model
    reshaped_acc = np.asarray(acc_record, dtype= np.float32).reshape(-1, 8, 3)
    return reshaped_acc #Returning the 3D Array as per LSTM models

#prediction db: insert activity prediction into activity table
def insert_prediction(user_name,prediction):
    global today
    date = today.strftime("%Y,%m,%d")  
    time = today.strftime("%H:%M:%S")

    conn = sql.connect('data.db')
    c = conn.cursor()
    c.execute("INSERT INTO activity (date,time,u_name,prediction) VALUES(?,?,?,?)", 
        (date,time,user_name,prediction)
        )
    conn.commit()
    conn.close()

#Prediction db: fetch data for graph.
def get_prediction():
    conn = sql.connect('data.db')
    c = conn.cursor()   
    c.execute('SELECT date,prediction FROM activity') #get date and activity data 
    data = c.fetchall()
    conn.commit()
    conn.close()
    return data