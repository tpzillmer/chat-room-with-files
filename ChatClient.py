def client(listeningport, connectport):

    try:
        messagesock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        messagesock.connect(('localhost', int(listeningport)))
        messagesock.send(str(connectport).encode())
        usernamemsg = messagesock.recv(100).decode()
        print(usernamemsg)

        while True:
            username = sys.stdin.readline()
            messagesock.send(username.encode())
            response = messagesock.recv(100).decode()
            if response == "Username taken":
                print("Username taken. Please enter a new username:")
            else:
                print(response)
                break
            
        filerquestsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        filerquestsock.connect(('localhost', int(connectport)))

        threading.Thread(target=recvMsg, args=[messagesock]).start()
        threading.Thread(target=fileListener, args=[filerquestsock, connectport]).start()

        try:
            while True:
                optionPrint()
                opt = sys.stdin.readline()[:-1]

                if opt.lower()=='f':
                    print("Enter the name of the user who has the file: ")
                    username = sys.stdin.readline()[:-1]
                    filerquestsock.send(username.encode())
                    
                    print("Enter the name of the file you want: ")
                    filename = sys.stdin.readline()[:-1]
                    filerquestsock.send(filename.encode())
                    filetransfersock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    filetransfersock.connect(('localhost', int(connectport)))
                    fileWriter(filetransfersock, filename)
                    
                elif opt.lower()=='m':
                   print("You: ", end="")
                   sys.stdout.flush()
                   msg = sys.stdin.readline()
                   messagesock.send(msg.encode())

                elif opt.lower()=='x':
                    print("closing your sockets...goodbye")
                    messagesock.shutdown(socket.SHUT_WR)
                    messagesock.close()
                    filerquestsock.shutdown(socket.SHUT_WR)
                    filerquestsock.close()
                    sys.exit()
                    
        except OSError:
            print("Server has closed. Goodbye.")
            messagesock.shutdown(socket.SHUT_WR)
            messagesock.close()
            filerquestsock.shutdown(socket.SHUT_WR)
            filerquestsock.close()
            sys.exit()
            
    except ConnectionRefusedError:
        print("Server not yet open.")
    
    
def recvMsg(messagesock):
    try:
        while True:
            recvmsg = messagesock.recv(1024)
            print(recvmsg.decode())
            optionPrint()
    except OSError:
        pass

def fileListener(filerquestsock, connectport):
    try:
        while True:
            filename = filerquestsock.recv(100).decode()
            if(len(filename)):
                filetransfersock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                filetransfersock.connect(('localhost', int(connectport)))
                try:
                    f = open(filename, 'rb')
                    l = f.read()
                    filetransfersock.sendall(l)
                    f.close()
                    print("Done sending.")
                    filetransfersock.shutdown(socket.SHUT_WR)
                    filetransfersock.close()
                except FileNotFoundError:
                    print("File not found.")
                    filetransfersock.shutdown(socket.SHUT_WR)
                    filetransfersock.close()
            optionPrint()
    except OSError:
        pass


def fileWriter(filetransfersock, filename):
    filebytes = filetransfersock.recv(1024)
    if len(filebytes) == 0:
        print("Either user or file not found.")
    else:
        f = open(filename, 'wb')
        while(filebytes):
            f.write(filebytes)
            filebytes = filetransfersock.recv(1024)
        f.close()
        print("Finished writing.")

def optionPrint():
    print("Enter an option ('m', 'f', 'x'):\n"
          " (M)essage (send)\n"
          " (F)ile (request)\n"
          "e(X)it")

def usage():
    print("Usage: python ChatClient.py -l <listening port number> -p <connect server port>")

if __name__ == "__main__":
    import getopt
    import sys
    import os
    import threading
    import socket

    #gets command line arguments
    try:
        opts, args = getopt.getopt(sys.argv[1:], "l:p:")
        if len(opts) == 2:
            if opts[0][0] == '-l' and opts[1][0] == '-p':
                client(opts[0][1], opts[1][1])
            else:
                usage()
        else:
            usage()
    except getopt.GetoptError:
        usage()
        
    
