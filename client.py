import random
import socket
import json

name = 'client'
leader_port = None
leader_name = None


def server_address(port):
    serveraddress = ("127.0.0.1", port)
    return serveraddress


def dict_to_byte(data):
    tmp = json.dumps(data).encode('utf-8')
    return tmp


def byte_to_dict(data):
    if data != b"":
        tmp = json.loads(data.decode('utf-8'))
        return tmp
    else:
        pass


def message(node_name, number):
    tmp = {'name': f'{node_name}', 'request': 'send', 'message': f'{number}'}
    return tmp


def main():
    for i in range(0, 6):
        global leader_name, leader_port
        number = random.randint(1, 100)
        if leader_port is None:
            leader_port = random.randint(9001, 9003)
            s = socket.socket()
            print("connect to random server: ", server_address(leader_port))
            s.connect(server_address(leader_port))
            s.sendall(dict_to_byte(message(name, number)))
            recieved = byte_to_dict(s.recv(1024))
            s.close()
            if recieved['request'] == 'redirect':  # if client get redirect flag means it sent message to wrong server
                try:
                    leader_name = recieved['name']
                    leader_port = int(recieved['message'])
                    print("Leader is : ", recieved['name'], "\n")
                    s = socket.socket()
                    s.connect(server_address(leader_port))
                    s.sendall(dict_to_byte(message(name, number)))
                    recieved_from_leader = byte_to_dict(s.recv(1024))
                    print(recieved_from_leader)
                    s.close()
                except Exception:
                    pass
        else:
            s = socket.socket()
            print("connect to leader: ", server_address(leader_port), "\n")
            s.connect(server_address(leader_port))
            s.sendall(dict_to_byte(message(name, number)))
            recieved = byte_to_dict(s.recv(1024))
            print(recieved)
            s.close()


if __name__ == "__main__":
    main()
