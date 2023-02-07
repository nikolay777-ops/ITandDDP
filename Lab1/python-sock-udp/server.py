import socket
import threading
import queue
import json
import sys
import random
import os

VERIFICATION_NUM = '127:234:145'

class User():
    def __init__(self, name: str):
        self.name = name
        self.mess_history = [] 
        self.active = True
        self.verified = True

    def close(self):
        self.active = False
        self.port = 0

class Chat():
    def __init__(self, size: int):
        self.id = str(size + 1)
        self.message_history = []
        self.participants = []
        self.create_socket()

    def create_socket(self):
        ttl = 2
        
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM,
            socket.IPPROTO_UDP
        )

        sock.setsockopt(
            socket.IPPROTO_IP,
            socket.IP_MULTICAST_TTL,
            ttl)

        self.address = '224.1.1.1', random.randint(5000, 10000)
        self.sock = sock
        

    def send_message(self, sender, text: str):
        data = f'[{sender}]->{text}'
        self.sock.sendto(data.encode('utf-8'), self.address)

    def chat_invite(self, invite: list, users: dict):
        for inv in invite:
            print(f'Sock name: {self.sock.getsockname()}')
            self.sock.sendto(
                f'chat_invite::{self.address[0]}//{self.address[1]}'.encode('utf-8'),
                 users[inv].address)

def receive_data(sock,recvPackets):
    while True:
        data,addr = sock.recvfrom(1024)
        recvPackets.put((data,addr))


def run_server():
    host = socket.gethostbyname(socket.gethostname())
    port = 5000
    print('Server hosting on IP-> '+str(host))
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.bind((host,port))
    clients = {}
    chats = {}
    recvPackets = queue.Queue()

    print('Server Running...')

    threading.Thread(target=receive_data, args=(s,recvPackets)).start()

    while True:

        while not recvPackets.empty():
            data,addr = recvPackets.get()
            data = data.decode('utf-8').split("]fsjakfw")      

            if len(data) > 1:      
                sender, data = data
                sender = sender[1:]
            else:
                sender = data[0]

            if sender not in clients:
                client = User(sender)
                client.address = addr
                clients[client.name] = client

                continue
            else:
                if clients[sender].address != addr:
                    clients[sender].address = addr
                if 'verify::' in data:
                    if data.split('verify::')[1] == VERIFICATION_NUM:
                        clients[sender].verified = True
                elif clients[sender].verified == False:
                    s.sendto("Please, verify your account for sending messages".encode('utf-8'), 
                    clients[sender].address)
                    continue
          
            if 'sendto::' in data:
                data = data.split('sendto::')[1].split('//')
                for key, value in clients.items():
                    if key == data[0]:
                        s.sendto((f'[{sender}]->'+ data[1]).encode('utf-8'), 
                        value.address)
                        clients[sender].mess_history.append(
                            {key: data[1]}
                        )
                print(f'{sender} send message to {data[0]}')

            elif 'chat::' in data:
                data = data.split('chat::')[1].split('//')
                
                for key, value in chats.items(): 
                    if key == data[0] and sender in value.participants:
                        data = f'chat[{key}]:{data[1]}'
                        value.send_message(sender, data)

            elif 'chat_create::' in data:
                data = data.split('chat_create::')[1].split('//')
                chats[data[0]] = Chat(len(chats))
                chat = chats[data[0]]
                data = data[1].split(', ')
                data.append(sender)

                chat.chat_invite(data, clients)

                for user in data:
                    chat.participants.append(user)
                
            elif 'chat_add::' in data:
                data = data.split('chat_add::')[1].split('//')

                chat = chats[data[0]]
                data = data[1].split(', ')
                chat.chat_invite(data, clients)
                
                for user in data:
                    if user not in chat.participants:
                        chat.participants.append(user)
                    s.sendto(f'Your chosen users already added'.encode('utf-8'),
                     clients[sender].address)

            elif 'active_list::' in data:
                active_users = set(
                    [key if value.active == True else '' for key, value in clients.items()])
                active_users = str(active_users).replace('{', '').replace('}', '')  
                active_users = f'Active users: {active_users}' 
                s.sendto(active_users.encode('utf-8'), clients[sender].address)

            elif 'message_his::' in data:
                client = clients[sender]
                his: str = ''

                for mes in client.mess_history:
                    key, value = *mes, *mes.values()
                    his = his + f'[{client.name}]->[{key}]:{value}\n'                

                s.sendto(his.encode('utf-8'), client.address)

            elif data == 'qqq':
                client = clients[addr[1]]
                client.close()
            
                continue
    s.close()

if __name__ == "__main__":
    run_server()