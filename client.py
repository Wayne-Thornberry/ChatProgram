import threading
import socket
from time import gmtime, strftime
import xml.etree.ElementTree as ET
import os
import time
import hashlib


class User:
    def __init__(self):
        self.username = ""
        self.color = "0;37;40m"
        self.privilege = 0


HOST = '127.0.0.1'  # The remote host
PORT = 50007  # The same port as used by the server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
connected = 1
os.system('color')  # importing the color lib
user = User()  # creates a new user object

while user.username == "":  # checks if the user hasnt entered a name
    user.username = raw_input("Please Enter A Username: ")  # prompts the user for a username
s.sendall("<data type='0'><username>" + user.username + "</username></data>")  # sends the server the user data

# type 0 : hello
# type 1 : message
# type 2 : notification
# type 3 : cmd

def readInput(so):
    global start
    try:
        while connected:
            text = raw_input()
            if text != "" and text != " ":  # checks if the input is empty or null
                hash = hashlib.sha224(text).hexdigest()  # creates a hash based on the message typed
                if text[0] == "/":  # checks if the first character is started with a / to determine if its a command or not
                    args = text.split(" ")  # split the text input to get the arguments out of it
                    if "/username" in text:  # username command to allow the changing of the clients username
                        user.username = args[1]  # gets the first argument of the split which is the username
                    elif "/color" in text:  # color changes the color of the username in the chat
                        if "red" in args[1]:
                            user.color = "1;31;40m"  # red
                        elif "green" in args[1]:
                            user.color = "1;32;40m"  # green
                        elif "blue" in args[1]:
                            user.color = "1;34;40m"  # blue
                        else:
                            user.color = "1;37;40m"  # white
                    elif "/ping" in text:
                        start = time.time()
                    so.sendall("<data type='2'><hash>" + hash + "</hash><color>" + user.color + "</color><username>" + user.username + "</username><message>" + text + "</message></data>")  # formats the data into a xml type that can be read using tags, the type atrabute indicates what type of data this is. the data tag indicates this, the hash contains the hashed code comapred on the server, username and color indicate the username and color and the message tag has the full message typed
                else:  # if its not a command, simply send the message to the server
                    so.sendall("<data type='1'><hash>" + hash + "</hash><color>" + user.color + "</color><username>" + user.username + "</username><message>" + text + "</message></data>")
    except socket.error as error:  # if the client disconnects from the server, catch the error and close the connection
        print error
        return

inputThread = threading.Thread(target=readInput, args=(s,))
inputThread.start()

def readOutput(s):
    global connected
    try:
        while connected:
            data = s.recv(1000)  # waits for a response
            root = ET.fromstring(data)
            formatted = strftime("[%H:%M:%S]", gmtime())  # gets the system time
            dateTime = str(formatted)  # formats the time

            if root.attrib['type'] == '0':
                print dateTime + root.find("username").text + " Joined The Chat Room"
            elif root.attrib['type'] == '1':
                print dateTime + "\033[" + root.find("color").text + root.find("username").text + "\033[0;37;40m" + ":" + root.find("message").text
            elif root.attrib['type'] == '2':
                if root.find("message").text == "Pong":
                    end = time.time()
                    print dateTime + root.find("message").text + " Time Took: " + str(end - start) + "ms" # prints the output data with time and message
                else:
                    print dateTime + root.find("message").text  # prints the output data with time and message
            elif root.attrib['type'] == '4':
                connected = 0
                print dateTime + root.find("message").text  # prints the output data with time and message
    except socket.error as error:
        return

outputThread = threading.Thread(target=readOutput, args=(s,))
outputThread.start()
