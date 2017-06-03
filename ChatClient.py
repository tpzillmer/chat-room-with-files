def client(listeningport, connectport):

    messagesock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    messagesock.connect(('localhost', int(listeningport)))
    
    messagesock.send(str(connectport).encode())
    print("Please enter your username :")
    username = sys.stdin.readline()
    messagesock.send(username.encode())

    filerquestsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    filerquestsock.connect(('localhost', int(connectport)))

    threading.Thread(target=recvMsg, args=[messagesock]).start()
    threading.Thread(target=fileListener, args=[filerquestsock, connectport]).start()
    

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
            messagesock.shutdown(socket.SHUT_WR)
            messagesock.close()
            filerquestsock.shutdown(socket.SHUT_WR)
            filerquestsock.close()
            sys.exit()
            
def recvMsg(messagesock):
    #Handles the receiving of messages
    
    while True:
        recvMsg = messagesock.recv(1024)
        print(recvMsg.decode())
        optionPrint()

def fileListener(filerquestsock, connectport):
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


def fileWriter(filetransfersock, filename):
    filebytes = filetransfersock.recv(1024)
    f = open(filename, 'wb')
    while(filebytes):
        print("Writing bytes")
        f.write(filebytes)
        filebytes = filetransfersock.recv(1024)
    f.close()
    if(os.stat(filename).st_size == 0):
        os.remove(filename)
        print("File not found.")
    else:
        print("Finished writing")

def optionPrint():
    print("Enter an option ('m', 'f', 'x'):\n"
          " (M)essage (send)\n"
          " (F)ile (request)\n"
          "e(X)it")
            

if __name__ == "__main__":
    import getopt
    import sys
    import os
    import threading
    import socket

    #gets command line arguments
    opts, args = getopt.getopt(sys.argv[1:], "l:p:")

    if(len(args) == 0):
        if(len(opts) == 2):
            client(opts[0][1], opts[1][1])
