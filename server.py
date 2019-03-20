import socket
import threading
import xml.etree.ElementTree as ET
from time import gmtime, strftime
import errno
import hashlib

class User:
    def __init__(self, username, con):
        self.Connection = con
        self.Username = username
        self.Messages = []

HOST = '127.0.0.1'
PORT = 50007
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
users = []
connections = []

# type 0 : hello
# type 1 : message
# type 2 : notification
# type 3 : cmd


def parseCmd(user, cmd, args):
    if cmd == "/users": # returns the user list and who is on the server
        list = "" # creates an empty string
        for user in users: # loops through all users
            list = list + "\n" + user.Username # adds them to the string
        user.Connection.send("<data type='2'><message>" + list + "</message></data>") # sends the notification data packet
    if cmd == "/messages": # gets the current messages a user has sent since joining
        list = ""
        for message in user.Messages:
            list = list + "\n" + message
        user.Connection.send("<data type='2'><message>" + list + "</message></data>")
    elif cmd == "/time": # returns the time
        formatted = strftime("[%d/%m/%y %H:%M:%S]", gmtime())
        dateTime = str(formatted)
        user.Connection.send("<data type='2'><message>" + "Current Time: " + dateTime + "</message></data>")
    elif cmd == "/color": # sets the color of a user in chat
        for user in users:
            user.Connection.send("<data type='2'><message>" + user.Username + " changed their color to " + args[0] + "</message></data>")
    elif cmd == "/username": # sets the username of a user in chat
        for user in users:
            user.Connection.send("<data type='2'><message>" + user.Username + " changed their username to " + args[0] + "</message></data>")
            user.Username = args[0]
    elif cmd == "/ping": # ping command to return the response ms time
        user.Connection.send("<data type='2'><message>" + "Pong" + "</message></data>")
    elif cmd == "/kick": # kicks a user
        for user in users:
            if user.Username == args[0]:
                user.Connection.send("<data type='4'><message>" + "You've been kicked from the server" + "</message></data>")
                user.Connection.close()



def logThis(log): # logs a message in the server window and file
    formatted = strftime("[%d/%m/%y %H:%M:%S]", gmtime())
    dateTime = str(formatted)
    print dateTime + str(log)


def manageConnection(con, addr): # manages individual clients
    connections.append(con) # adds the connection object to an array
    cu = None # creates a current user
    while 1:
        try:
            data = con.recv(1024) # waits for data
            root = ET.fromstring(data) # parses the data recived into a xml data type
            if root.attrib['type'] == '0': # looks to see if it s hello message
                username = root.find("username").text # gets the username from it
                logThis(str(addr) + username + " Connected") # creates a new user object and logs
                cu = User(username,con) # the new user into an array
                users.append(cu)
                for user in users:
                    user.Connection.send(data) # sends a mesage to the rest of the server for x has joined
            elif root.attrib['type'] == '1': # if its a message
                hash = hashlib.sha224(root.find("message").text).hexdigest() # get the hex code from the message
                if hash == root.find("hash").text: # compare it with the hex code inside the data packet
                    logThis("(" + str(addr[0]) + ")"+root.find("username").text+":"+root.find("message").text) # log the message
                    cu.Messages.append(root.find("message").text) # add that message to the users messages
                    for user in users: # loop through all users
                        user.Connection.send(data) # send the message to all users
                else:
                    print "Mismatch in message hash" # error: hashes arent the same which means the messages arent the same
            elif root.attrib['type'] == '2':
                args = root.find('message').text.split(" ")
                cmd = args.pop(0)
                logThis("(" + str(addr[0]) + ")"+root.find("username").text+":"+root.find("message").text)
                parseCmd(cu, cmd, args)
        except socket.error as error:
            return


while 1:
    s.listen(1)
    conn, addr = s.accept()
    t = threading.Thread(target=manageConnection, args=(conn, addr))
    t.start()
