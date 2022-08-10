#Import libraries
from cryptography.fernet import Fernet

def write_key():
    key = Fernet.generate_key() # Generates the key
    with open("key.key", "wb") as key_file: # Opens the file the key is to be written to
        key_file.write(key) # Writes the key

def load_key():
    return open("key.key", "rb").read() #Opens the file, reads and returns the key stored in the file

# write_key() # Writes the key to the key file
key = load_key() # Loads the key and stores it in a variable
f = Fernet(key) #we need to initialize the fernet object by passing in the key we just loaded

def encrypt(text): #function for encryption
    decr_text=f.encrypt(bytes((text),encoding='utf-8'))
    return decr_text
    

def decrypt(text): #function for decription
    decr_text=f.decrypt(text).decode("utf-8")
    return decr_text