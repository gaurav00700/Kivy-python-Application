#Pyhton Libraries
from plyer import notification #for windows
import os #for checking os type 

os_name=os.name #macos->posix , windows->Windows

if os_name=='posix': #for macos
    import pync # for macos
    def notify_me(message,msg_title):
        pync.notify(message=message, title=msg_title)
    
    
else:    #for windows
    def notify_me(message,msg_title):        
        notification.notify(title=message, message=msg_title)