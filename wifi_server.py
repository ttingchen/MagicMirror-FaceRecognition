import socket
import json

HOST = "192.168.137.141" # IP address of your Raspberry PI
PORT = 65432          # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()

    try:
        while 1:
            # gs_list = fc.get_grayscale_list()
            client, clientInfo = s.accept()
            print("server recv from: ", clientInfo)
            data = client.recv(1024)      # receive 1024 Bytes of message in binary format
            result="test"
            if data != b"":
                if data == b"forward\r\n":
                    result = "forward"
                elif data == b"backward\r\n":
                    result = "backward"
                elif data == b"left\r\n":
                    result = "left"
                elif data == b"right\r\n":
                    result = "right"
                print(data) 
                pidata = json.dumps(result)  
                client.sendall(bytes(pidata,encoding="utf-8")) # Echo back to client
    except: 
        print("Closing socket")
        client.close()
        s.close()    
