import socket
import threading
import random
import os
import sys
import struct

sockets = {}

def receive_data(sock):
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            data = data.decode('utf-8')
            # print(data)
            if "chat_invite::" in data:
                data = data.split('chat_invite::')[1].split('//')
                listener_add((data[0], int(data[1])))
                print("You are added in group chat!")
                continue

            print(data)
        except Exception as ex:
            print(f'{type(ex).__name__}')

def listener_add(addr: tuple):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('' ,addr[1]))
    mreq = struct.pack("4sl", socket.inet_aton(addr[0]), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    sockets[str(len(sockets))] = sock
    threading.Thread(target=receive_data, args=(sock,)).start()


def run_client(serverIP):
    host = socket.gethostbyname(socket.gethostname())
    port = random.randint(6000,10000)
    print('Client IP->'+str(host)+' Port->'+str(port))
    server = (str(serverIP),5000)   
    s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    s.bind((host,port))
    
    sockets['0'] = s

    name = input('Please write your name here: ')
    if name == '':
        name = 'Guest'+str(random.randint(1000,9999))
        print('Your name is:'+name)
    s.sendto(name.encode('utf-8'),server)
    threading.Thread(target=receive_data,args=(s,)).start()
    while True:
        data = input()
        if data == 'qqq':
            break
        # elif 'chat::' in data:
        #     data = data.split('chat::')[1].split('//')
        #     sockets[data[0]].sendto(data[1].encode('utf-8'), server)
        #     continue

        elif data=='':
            continue


        data = f'[{name}]fsjakfw{data}'
        # data = '['+name+']' + '->'+ data
        s.sendto(data.encode('utf-8'), server)
    # s.sendto(data.encode('utf-8'),server) 
    s.close()
    os._exit(1)

if __name__ == "__main__":
    # run_client(sys.argv[1])
    run_client('127.0.1.1')