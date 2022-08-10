#python libraries
from kivy.lang import Builder  
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock
from kivymd.uix.menu import MDDropdownMenu
from plyer import accelerometer
from plyer import notification
import os
from kivy.uix.floatlayout import FloatLayout
# from kivy.garden.matplotlib.backend_kivyagg import 

#Import python module 
import sqldb
import LSTM_model
import alert_noti
import fernet
import graphs

#**************WINDOW SIZE MAY BE DIFFERENT IN OTHER SYSTEM********************#

Window.size = (320, 650) #window size

#**************WINDOW SIZE MAY BE DIFFERENT IN OTHER SYSTEM********************#


#Declate global variables
user_name=''    #store username
user_pass='' #store password
cipher_username='' #store encrypted username
cipher_pass='' #store encrypted username
notification=True   #for notification toggle
notification_hr=True #for notification per hr
Prediction=''   #Store the predicted activity class
val=() #store test data for prediction if accelrometer not available (offline prediction)
row=1 #row number for test data

#Create new account screen
class CreateAcc(Screen):
    global cipher_username
    global cipher_pass

    def create_save(self):
        #Data encryption using fernet
        cipher_username = fernet.encrypt(self.ids.Cname.text) #user name entered by user
        cipher_pass = fernet.encrypt(self.ids.Cpass.text) #password entered by user
        cipher_name = fernet.encrypt('') #initiate with blank value
        cipher_age = fernet.encrypt('') #initiate with blank value
        cipher_weight = fernet.encrypt('') #initiate with blank value
        cipher_height = fernet.encrypt('') #initiate with blank value
        cipher_job = fernet.encrypt('') #initiate with blank value
        
        #Insert the encrypted data in user db table
        sqldb.insert_items_user(cipher_username,cipher_pass,cipher_name,cipher_age,cipher_weight,cipher_height,cipher_job)
        self.parent.current='login' #screen change to login screen

#Login Screen
class Login(Screen):

    def verify_credentials(self):
        global user_name
        global user_pass
        global cipher_username
        global cipher_pass
        
        n_rows=sqldb.get_count_row_users('CUser') #Get number of rows in user table
        u_name = sqldb.get_items_users('CUser') #get all user names
        u_pass = sqldb.get_items_users('CPass') #get all user passwords       
        correct=False

        #Iterates through each row of user names and psswords
        for i in range(0, n_rows ,1):
            #Store decrypted data in variable
            decrypted_uname = fernet.decrypt(u_name[i][0]) 
            decrypted_pass = fernet.decrypt(u_pass[i][0]) 
            #Checks whether the same combination of password and username is in the db or not
            if decrypted_uname==self.ids.user.text and decrypted_pass==self.ids.Pass.text:
                correct=True
                user_name=decrypted_uname
                user_pass=decrypted_pass
                cipher_username=u_name[i][0] #for saving with user's other details
                cipher_pass=u_pass[i][0] #for saving with user's other details
                decrypted_uname=''
                decrypted_pass=''
                break

        if correct==True:
            self.ids.approved.text ="Welcome!"
            self.ids.approved.text_color = 0,1,0,1                     
            alert_noti.notify_me('SignIn approved','Fitness App') #send notofication for signin approved            
            self.parent.current='mainpage' #Change screen to mainpage
            correct=False
                
        else:
            self.ids.approved.text ="Incorrect Credentials"
            self.ids.approved.text_color = 1,0,0,1
            correct=False
               
#Main Page 
class MainPage(Screen):
    global notification_hr    
    
    def acc_toggle_start(self):
        global val
        global notification

        try: #check if accelerometer not avalable
            accelerometer.enable() #Enable accelerometer sensor on phone 
            Clock.schedule_interval(self.prediction_accelerometer, 90) #schedule clock for call prediction_accelerometer fuctn at every 90 sec
            if notification==True:
                alert_noti.notify_me('Predicting from Accelerameter', 'Fitness App') #send notification if not avalable
            else:
                pass
        except:
            if notification==True: 
                alert_noti.notify_me('Accelerometer NOT available \n Predicting from TEST data', 'Fitness App') #send notification if not avalable
            else:
                pass
            #-----------------TEST DATA----------------------#
            import pandas as pd
            df=pd.read_csv('test_data.csv') #loading local test data
            records = df.to_records(index=False)
            df = list(records)
            val=tuple(map(tuple, df)) # convert data frame into tuple list
            #-----------------TEST DATA----------------------#

            Clock.schedule_interval(self.prediction_test, 5) #schedule clock for call prediction_test fuctn at every 5 sec                 

    def prediction_accelerometer(self, dt):
        global user_name

        Rate=8 #sampelling rate,Tx=8
        for i in range(0,Rate,1):
            if i<=Rate:                
                val = accelerometer.acceleration[:3] #Get accelerometer row values            
                if not val == (None, None, None): #store acc data if available
                    self.ids.x_label.text = "X (m/sec2)| " + str(val[0]) # val[i][0] for TESTING
                    self.ids.y_label.text = "Y (m/sec2)| " + str(val[1]) 
                    self.ids.z_label.text = "Z (m/sec2)| " + str(val[2]) 
                    xval=val[0] # val[i][0] for TESTING
                    yval=val[1]
                    zval=val[2]
                    sqldb.insert_acc(xval,yval,zval)                    
            else:
                pass
        Prediction = LSTM_model.predict() #Predicting activity
        #send prediction msg in main page
        self.ids.prd_val.text ="Your current activity is [b]{}[/b].".format(Prediction)
        #insert prediction data into predition db
        sqldb.insert_prediction(user_name,Prediction)
        print('Activity prediction from Accelerometer is "{}"'.format(Prediction))
        print('#------------------------------------------------------------#')

        #-----------------ALTERNATE CODE----------------------#
        # val = accelerometer.acceleration[:3)
        # while val != (None, None, None):
        #     self.ids.x_label.text = "X: " + str(val[0]) # val[i][0] for TESTING
        #     self.ids.y_label.text = "Y: " + str(val[1]) 
        #     self.ids.z_label.text = "Z: " + str(val[2]) 
        #     xval=val[0] # val[i][0] for TESTING
        #     yval=val[1]
        #     zval=val[2]
        #     sqldb.insert_acc(xval,yval,zval)          
            
        #     Prediction = LSTM_model.predict() #Predicting activity
        #     #send prediction msg in main page
        #     self.ids.prd_val.text ="Your current activity is [b]{}[/b].".format(Prediction)
        #     #insert prediction data into predition db
        #     sqldb.insert_prediction(Prediction)    
        #     #delay time
        #     import time
        #     time.sleep(10) #remove time delay if UI freezes
        #     val = accelerometer.acceleration[:3]
        #-----------------ALTERNATE CODE----------------------# 

    def prediction_test(self, dt):
        global Prediction
        global user_name
        global val
        global row
 
        xval=val[row][0] # val[i][0] for TESTING
        yval=val[row][1]
        zval=val[row][2]
        #insert acc values (X,Y,X) in db
        sqldb.insert_acc(xval,yval,zval)

        #showing acc value (X,Y,X) on main page
        self.ids.x_label.text = "X (m/sec2)| " + str(val[row][0]) # val[i][0] for TESTING
        self.ids.y_label.text = "Y (m/sec2)| " + str(val[row][1]) 
        self.ids.z_label.text = "Z (m/sec2)| " + str(val[row][2])

        #Predicting activity
        Prediction = LSTM_model.predict() #Predicting activity            
        #send prediction msg in main page
        self.ids.prd_val.text ="Your current activity is [b]{}[/b].".format(Prediction)
        #insert prediction data into predition db
        sqldb.insert_prediction(user_name,Prediction)
        row +=1
        print('Activity prediction from TEST DATA is "{}"'.format(Prediction))
        print('#----------------------------------------------------------#')  
        

    def acc_toggle_stop(self):
        global notification

        try: #handelling error, if occoured
            accelerometer.disable() #Disable accelerometer sensor
        except:
            pass
        Clock.unschedule(self.prediction_accelerometer) #Unschedule clock of prediction from accelerometer
        Clock.unschedule(self.prediction_test) #Unschedule clock of prediction from accelerometer
        self.ids.prd_val.text = 'No Activity/Checked out' #showing msg on mainpage
        #showing acc value (X,Y,X) on main page
        if notification==True:   
            alert_noti.notify_me('Activity stopped', 'Fitness App') #send notification when checked out
        else:
            pass
        #turning acc values to null when checked out
        self.ids.x_label.text = "X (m/sec2)| 0.00" 
        self.ids.y_label.text = "Y (m/sec2)| 0.00" 
        self.ids.z_label.text = "Z (m/sec2)| 0.00"
    
    def toggle_notification(self):
        global notification
        global notification_hr
        
        if notification==True:
            self.ids.notify.text="Notifications OFF"            
            notification = False #Notification toggle bool
            notification_hr=False
        else:
            self.ids.notify.text="Notifications ON"
            alert_noti.notify_me('Notification are ON', 'Fitness App')  #notification on OR off
            notification = True #Notification toggle bool
            notification_hr=False

    def Remind(self):
        if notification_hr==True:
            alert_noti.notify_me('Activity remainder', 'Fitness App')
        else:
            pass

#Setting Screen
class Settings_page(Screen):
    global user_name
    global user_pass
    global notification_hr

    def add(self):
        global cipher_username
        global cipher_pass

        n_rows=sqldb.get_count_row_users('CUser') #get number of rows
        u_name = sqldb.get_items_users('CUser') #get user name column from user table
        u_pass = sqldb.get_items_users('CPass') #get password column from user table
        for i in range(0,n_rows,1):
            if u_name[i][0]==cipher_username and u_pass[i][0]==cipher_pass: #compare user name and password
                cipher_name = fernet.encrypt(self.ids.Sname.text)
                cipher_age = fernet.encrypt(self.ids.Sage.text)
                cipher_weight = fernet.encrypt(self.ids.Sweight.text)
                cipher_height = fernet.encrypt(self.ids.Sheight.text)
                cipher_job = fernet.encrypt(self.ids.Sjob.text)
                row_id=i+1 #rowid where data will be saved
                
                #save user details data as per user row
                sqldb.save_data_ids(cipher_name,cipher_age,cipher_weight,cipher_height,cipher_job,row_id)
                
                break

    def show_details(self):
        global cipher_username
        global cipher_pass

        #get are rows of respectivae columns
        n_rows=sqldb.get_count_row_users('CUser')
        u_name = sqldb.get_items_users('CUser')
        u_pass = sqldb.get_items_users('CPass')
        name = sqldb.get_items_users('Name')
        age = sqldb.get_items_users('Age')
        weight = sqldb.get_items_users('Weight')
        height = sqldb.get_items_users('Height')
        job = sqldb.get_items_users('Job')

        #check for correct user and password combination
        for i in range(0,n_rows,1):
            if u_name[i][0]==cipher_username and u_pass[i][0]==cipher_pass: #decrypt the values if match found
                decrypted_name = fernet.decrypt(name[i][0])
                decrypted_age = fernet.decrypt(age[i][0])
                decrypted_weight = fernet.decrypt(weight[i][0])
                decrypted_height = fernet.decrypt(height[i][0])
                decrypted_job = fernet.decrypt(job[i][0])
                
                #send values for showing in setting page 
                self.ids.Sname.text = decrypted_name
                self.ids.Sage.text = decrypted_age
                self.ids.Sweight.text = decrypted_weight
                self.ids.Sheight.text = decrypted_height
                self.ids.Sjob.text = decrypted_job
                break

    #function for detail of sensors used        
    def sensors_detail(self):
        #accelerometer check'
        try:
            accelerometer.enable()
            check_acc='YES'          
        except:
            check_acc='NO' 
        self.ids.acc_chk.text = check_acc #return check result
        
        #Disk write check
        if os.access(os.getcwd(), os.W_OK)==True:
            check_disk='YES'
        else:
            check_disk='NO'
        self.ids.disk_chk.text = check_disk #return check result
        
        #Notification  check
        try:
            alert_noti.notify_me('Checking Sensors', 'Fitness App')
            check_noti='YES'
        except:
            check_noti='NO'
        self.ids.noti_chk.text = check_noti #return check result
    
    #for hourly notification
    def notify_hr(self):
        self.hr_list = [
            {
                "viewclass": "OneLineListItem",
                "text": "1",
                "on_release": lambda x = "1": self.per_hr(1)
            },
            {
                "viewclass": "OneLineListItem",
                "text": "2",
                "on_release": lambda x = "2": self.per_hr(2)
            },
            {
                "viewclass": "OneLineListItem",
                "text": "3",
                "on_release": lambda x = "3": self.per_hr(3)
            },
            {
                "viewclass": "OneLineListItem",
                "text": "4",
                "on_release": lambda x = "4": self.per_hr(4)
            },
            {
                "viewclass": "OneLineListItem",
                "text": "5",
                "on_release": lambda x = "5": self.per_hr(5)
            }
        ]
        self.menu = MDDropdownMenu(
            caller = self.ids.notify_hr,
            items = self.hr_list,
            width_mult = 1
        )
        self.menu.open()

    def per_hr(self,num):
        Clock.unschedule(self.prediction_notify) #Unschedule the clock, if active
        Clock.schedule_interval(self.prediction_notify, 3600/num) #change notification to number/Hr
        alert_noti.notify_me('Activity remainder set', 'Fitness App') #send notification remainder

    #control notifications per hour
    def prediction_notify(self):
        if notification_hr == False:
            notification_hr == True
        else:
            pass

#Screen to display Graph
class Graph(Screen):
    #Drop down menu for selecting the display of graph(Daily,Monthly,Weekly)
    def dropdown(self):
        self.menu_list = [
            {
                "viewclass": "OneLineListItem",
                "text": "Daily",
                "on_release": lambda x = "Daily": self.day()
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Weekly",
                "on_release": lambda x = "Weekly": self.week()
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Monthly",
                "on_release": lambda x = "Monthly": self.MONTH()
            }
        ]
        self.menu = MDDropdownMenu(
            caller = self.ids.MMM,
            items = self.menu_list,
            width_mult = 3
            )
        self.menu.open()

    def day(self):
        #fetch prediction data
        df=sqldb.get_prediction()
        #preocess data 
        import pandas as pd
        df = pd.DataFrame(df, columns=['date', 'activity']) #seelct data and activity column
        df['date'] = df['date'].str.replace(',', '') #remove commas from date
        df['date']=df['date'].apply(pd.to_numeric) #convert date in interger

        #get today date 
        import datetime
        from datetime import date
        from datetime import timedelta
        
        today_date=date.today() #getdate
        today_formated = today_date.strftime("%Y,%m,%d") #reformat
        today_formated=today_formated.replace(',','') #remove commas
        today_formated=int(today_formated) #convert in integer

        # activity_count=df.loc[df['date']==today_formated, 'activity'] #.loc return row query
        # data=activity_count.value_counts() #count the values for each activity
        # graphs.make(activity_count,data,'day') #send

        activity_count=df.query('{}<=date<={}'.format(today_formated, today_formated)) #query in dataframe for values range
        data=activity_count["activity"].value_counts() #get values count
        graphs.make(activity_count,data,'day') #send
        self.ids.graph.source='day.png' #load graph.png file

        self.ids.graph.source='day.png' #load graph.png file

    def week(self):
        #fetch prediction data
        df=sqldb.get_prediction()
        #preocess data 
        import pandas as pd
        df = pd.DataFrame(df, columns=['date', 'activity']) #seelct data and activity column
        df['date'] = df['date'].str.replace(',', '') #remove commas from date
        df['date']=df['date'].apply(pd.to_numeric) #convert date in interger
        
        #get today date 
        import datetime
        from datetime import timedelta
        from datetime import date

        today_date=date.today() #getdate
        today_formated = today_date.strftime("%Y,%m,%d") #reformat
        today_formated=today_formated.replace(',','') #remove commas
        today_formated=int(today_formated) #convert in integer

        date_week=today_date-timedelta(days=7) #get date for beginning of last week
        date_week = date_week.strftime("%Y,%m,%d") #reformat
        date_week=date_week.replace(',','') #remove commas
        week_formated=int(date_week) #convert in integer

        activity_count=df.query('{}<=date<={}'.format(week_formated, today_formated)) #query in dataframe for values range
        data=activity_count["activity"].value_counts() #get values count
        graphs.make(activity_count,data,'week') #send
        self.ids.graph.source='week.png' #load graph.png file

    def MONTH(self):
        #fetch prediction data
        df=sqldb.get_prediction()
        #preocess data 
        import pandas as pd
        df = pd.DataFrame(df, columns=['date', 'activity']) #seelct data and activity column
        df['date'] = df['date'].str.replace(',', '') #remove commas from date
        df['date']=df['date'].apply(pd.to_numeric) #convert date in interger

        import datetime
        from datetime import timedelta
        from datetime import date
        today_date=date.today()
        today_formated = today_date.strftime("%Y,%m,%d") #reformat
        today_formated=today_formated.replace(',','') #remove commas
        today_formated=int(today_formated) #convert in integer

        date_month=today_date-timedelta(days=30) #get date for beginning of month
        date_month = date_month.strftime("%Y,%m,%d") #reformat
        date_month=date_month.replace(',','') #remove commas
        month_formated=int(date_month) #convert in integer

        activity_count=df.query('{}<=date<={}'.format(month_formated, today_formated)) #query in dataframe for values range
        data=activity_count["activity"].value_counts() #get values count
        graphs.make(activity_count,data,'month') #send
        self.ids.graph.source='month.png' #load graph.png file


#Class for Screen Manager
class WindowManager(ScreenManager):
    pass

#Root directory of the Application
class Fitness(MDApp):

    def build(self):
        sm = ScreenManager()
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Gray"
        #----------------theme options-----------------#
        #"Red', 'Pink' "Purple', 'DeepPurple',
        #"Indigo' 'Blue', 'LightBlue' 'Cyan'.
        #"Teal', "Green' 'LightGreen' "Lime'
        #"Yellow', 'Amber', 'Orange', DeepOrange'
        #"Brown', "Gray', 'BlueGray'.
        #Defining the screen manager here
        #----------------theme options-----------------#     

        sm.add_widget(CreateAcc(name='createacc'))
        sm.add_widget(Login(name='login'))        
        sm.add_widget(MainPage(name='mainpage'))
        sm.add_widget(Settings_page(name='setting'))
        sm.add_widget(Graph(name='graph')) 
                                
        sqldb.create_main_db() #Create database for storing user and acceleration values
        LSTM_model.lstm_model_load() #tflite LSTM model load

        return Builder.load_file('main.kv')

Fitness().run()