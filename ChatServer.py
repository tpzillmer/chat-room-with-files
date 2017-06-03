clientlist = []

def server(messageport):
    messageserversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    messageserversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    messageserversocket.bind(('localhost', int(messageport)))
	
    messageserversocket.listen(5)
    while True:
        messagesock, addr = messageserversocket.accept()
        fileport = messagesock.recv(100).decode()
        username = messagesock.recv(100).decode()[:-1]
        
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
					
def fileListener(userinfo):
    while True:
        fileowner = userinfo[2].recv(100).decode()
        filename = userinfo[2].recv(100)

        print("Connecting with "+fileowner)
        print("Looking for "+filename.decode())
        
        if(len(fileowner)):
            for client in clientlist:
                if client[0].lower() == fileowner.lower():
                    client[2].send(filename)
                    print("Listening...")
                    
                    fileowner_sock = client[4]
                    fileowner_sock.listen(5)
                    filereceivesock, addr=fileowner_sock.accept()
                    print("Receiver sock opened")
                    l = filereceivesock.recv(1024)
                    file = l
                    while(l):
                        print("Receiving bytes...")
                        l = filereceivesock.recv(1024)
                        file += l
						
        userinfo[4].listen(5)
        filetransfersock, addr = userinfo[4].accept()
        
        print("Sending bytes")
        filetransfersock.sendall(file)
        filetransfersock.shutdown(socket.SHUT_WR)
        filetransfersock.close()
        
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
            

