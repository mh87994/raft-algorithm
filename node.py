import random
import socket
import threading
from _thread import *
import json
import sys


servers = [9001, 9002, 9003]
rank = str(random.randint(1, 100))
name = sys.argv[1]
index = int(sys.argv[2])
serverAddress = ("127.0.0.1", servers[index])
serversList = [("127.0.0.1", servers[i]) for i in range(len(servers)) if i != index]
leader_name = None
leader_ip = None
client_numbers = []
storage = []


# convert dict to byte-type
def dict_to_byte(data):
    tmp = json.dumps(data).encode('utf-8')
    return tmp


# convert byte-type to dict
def byte_to_dict(data):
    tmp = json.loads(data.decode('utf-8'))
    return tmp


# make message format
def message(node_name, request, message):
    tmp = {'name': f'{node_name}', 'request': f'{str(request)}', 'message': str(message)}
    return tmp


# server will broadcast election request
def broadcast():
    xs = []
    election_request = message(name, 'Election', servers[index])
    for i in range(len(serversList)):
        s = socket.socket()
        s.connect(serversList[i])
        s.send(dict_to_byte(election_request))
        data = s.recv(1024)
        xs.append(data)
    return xs


# performing election with other servers
def election():
    global leader_name, leader_ip
    tmp = broadcast()
    max_rank = rank
    lead = name
    leaderIp = servers[index]
    for i in tmp:
        xs = byte_to_dict(i)
        print(f"{xs['name']}  rank:{xs['request']}")
        if xs['request'] > max_rank:
            max_rank = xs['request']
            lead = xs['name']
            leaderIp = xs['message']
    leader_name = lead
    leader_ip = leaderIp


# handle received data from servers and client
def threaded(c: socket.socket):
    global client_numbers, storage
    data = c.recv(1024)
    xs = byte_to_dict(data)

    # send name and rank for election
    if xs['request'] == 'Election':
        c.sendall(dict_to_byte(message(name, rank, servers[index])))

    # handle client request
    elif xs['request'] == 'send':
        if name == leader_name:
            print(f"i got from {xs['name']} value: {xs['message']}")
            client_numbers.append(xs['message'])
            c.send(dict_to_byte("ok!"))
            if len(client_numbers) != 0:
                if len(client_numbers) % 3 == 0:
                    print("My stack is:", client_numbers, "\r")
                    print("sending data to followers!!!!")
                    for i in range(len(serversList)):
                        try:
                            s = socket.socket()
                            s.connect(serversList[i])
                            s.send(dict_to_byte(message(leader_name, "inform", client_numbers)))
                            delivery_submission = byte_to_dict(s.recv(1024))
                            print(delivery_submission)

                        except Exception:
                            pass
            else:
                pass

        else:
            # send leader information to client for next requests
            c.send(dict_to_byte(message(leader_name, "redirect", leader_ip)))

    elif xs['request'] == 'inform':
        storage.append(xs['message'])
        for i in range(len(storage)):
            print(storage[i])

    else:
        print("Bye")


def main():
    global leader_name, leader_ip
    print(f"I AM {name} My Rank: {rank}\r\n")
    print("Waiting for a connection ...")
    server_thread = threading.Thread(target=server)
    server_thread.start()
    election()
    print("Leader is: " + leader_name)
    server_thread.join()


def server():
    s = socket.socket()
    s.bind(serverAddress)
    s.listen()
    while True:
        connection, client_addr = s.accept()
        start_new_thread(threaded, (connection,))


if __name__ == "__main__":
    main()
