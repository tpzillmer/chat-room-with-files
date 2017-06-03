clientlist = []

def server(messageport):
    messageserversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    messageserversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    messageserversocket.bind(('localhost', int(messageport)))
	
    while True:
        messageserversocket.listen(5)
        messagesock, addr = messageserversocket.accept()
        fileport = messagesock.recv(100).decode()
        usernamemsg = "Please enter your username: "
        messagesock.send(usernamemsg.encode())
  
        while True:
            username = messagesock.recv(100).decode()[:-1]
            usernamenottaken = 1
            for client in clientlist:
                if client[0].lower() == username.lower():
                    response = "Username taken"
                    messagesock.send(response.encode())
                    usernamenottaken = 0
                    break
            if usernamenottaken:
                welcome = "Welcome to the chat room!"
                messagesock.send(welcome.encode())
                break
        
        fileserversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        fileserversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        fileserversocket.bind(('localhost', int(fileport)))
        
        fileserversocket.listen(5)
        filerequestsock, addr = fileserversocket.accept()
        
        userinfo = (username, messagesock, filerequestsock, fileport, fileserversocket)
        clientlist.append(userinfo)
        
        threading.Thread(target=messageHandler, args=[userinfo]).start()
        threading.Thread(target=fileListener, args=[userinfo]).start()
		
	
def messageHandler(userinfo):
    while True:
        username = userinfo[0]+': '
        msg = userinfo[1].recv(1024).decode()
        
        if len(msg):
            for client in clientlist:
                if client != userinfo:
                    client[1].send((username+msg[:-1]).encode())
        else:
            try:
                print("User {} has exited the chat room".format(userinfo[0]))
                clientlist.remove(userinfo)
                break
            except ValueError:
                break
					
def fileListener(userinfo):
    while True:
        fileowner = userinfo[2].recv(100).decode()
        filename = userinfo[2].recv(100)
        fileownerexists = 0
        
        if(len(fileowner)):
            for client in clientlist:
                if client[0].lower() == fileowner.lower():
                    fileownerexists = client
            
            if(fileownerexists):
                print("Connecting with "+fileowner)
                print("Looking for "+filename.decode())
                
                fileownerexists[2].send(filename)
                fileowner_sock = fileownerexists[4]
                fileowner_sock.listen(5)
                filereceivesock, addr=fileowner_sock.accept()
                l = filereceivesock.recv(1024)
                file = l
                while(l):
                    l = filereceivesock.recv(1024)
                    file += l
                                                        
                userinfo[4].listen(5)
                filetransfersock, addr = userinfo[4].accept()
                if(len(l)):
                    print("Sending bytes to {}".format(userinfo[0]))
                else:
                    print("File not found.")
                filetransfersock.sendall(file)
                filetransfersock.shutdown(socket.SHUT_WR)
                filetransfersock.close()
                        
            else:
                print("User not found")
                userinfo[4].listen(5)
                filetransfersock, addr = userinfo[4].accept()
                filetransfersock.shutdown(socket.SHUT_WR)
                filetransfersock.close()
                            
        else:
            try:
                print("User {} has exited the chat room".format(userinfo[0]))
                clientlist.remove(userinfo)
                break
            except ValueError:
                break
        
if __name__ == "__main__":
    import getopt
    import sys
    import threading
    import socket
    
    #gets command line arguments
    opts, args = getopt.getopt(sys.argv[1:], "")

    if(len(opts) == 0):
        if(len(args) == 1):
            server(args[0])
    else:
        print("Usage: py ChatServer.py <listening port number>")
            

