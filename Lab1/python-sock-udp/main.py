# Make User class with message history as a list of messages. Message is tuple (text, reciever)
# Make verifying user by dict creation with name key and bool result (Verified or not)
# Refactor for 2 files: client and server

import socket
import threading
import queue
import sys
import random
import os

class User():
    def __init__(self, name: str, size: int):
        self.name = name
        self.id = size
        self.mess_history = [] 



#Server Code
def RecvData(sock,recvPackets):
    while True:
        data,addr = sock.recvfrom(1024)
        recvPackets.put((data,addr))

def RunServer():
    host = socket.gethostbyname(socket.gethostname())
    port = 5000
    print('Server hosting on IP-> '+str(host))
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.bind((host,port))
    clients = set()
    recvPackets = queue.Queue()

    print('Server Running...')

    threading.Thread(target=RecvData,args=(s,recvPackets)).start()

    while True:
        while not recvPackets.empty():
            data,addr = recvPackets.get()
            if addr not in clients:
                clients.add(addr)
                continue
            clients.add(addr)
            data = data.decode('utf-8')
            if data.endswith('qqq'):
                clients.remove(addr)
                continue
            print(str(addr)+data)
            for c in clients:
                if c!=addr:
                    s.sendto(data.encode('utf-8'),c)
    s.close()
#Serevr Code Ends Here

# if __name__ == '__main__':
#     if len(sys.argv)==1:
#         RunServer()
#     elif len(sys.argv)==2:
#         RunClient(sys.argv[1])
#     else:
#         print('Run Serevr:-> python Chat.py')
#         print('Run Client:-> python Chat.py <ServerIP>')
