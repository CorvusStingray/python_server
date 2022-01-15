#!/usr/bin/env python

from json import load
from typing import Union, Optional
import socket as s
from time import strftime as strft

# Handlers START

import handlers.handler_login

# Handlers END

def import_config(config_path : str) -> dict:
    with open(config_path, 'r') as reader:
        return load(reader)

class Server:
    def __init__(self, app_path : str, ip : str, port : int, queue : int, buffer_size : int, urls : dict) -> None:
        self.app_path = app_path
        self.addr = (ip, port)
        self.queue = queue
        self.buffer_size = buffer_size
        self.urls = urls

        self.server = s.socket(s.AF_INET, s.SOCK_STREAM)
        self.server.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, True)

    def __bind(self, addr : tuple) -> None:
        try:
            self.server.bind(addr)
        except PermissionError:
            print(f"[x] Use 'sudo' for bind a server on {addr[1]} port")
        except OSError:
            print(f"[x] Port {addr[1]} already in use")
        else:
            return
        
        exit()

    def __process_request(self, request : bytes) -> Union[dict, bool]:
        request_splitted = request.decode('utf-8').split()

        processed_request = dict()

        try:
            processed_request['method'] = request_splitted[0]
        except IndexError:
            return False
        else:        
            try:
                processed_request['path'], get_data_chunk = request_splitted[1].split('?')
            except ValueError:
                processed_request['path'] = request_splitted[1]
            else:
                get_data_vars = [get_data_var.split('=') for get_data_var in get_data_chunk.split('&')]

                processed_request['get_data'] = dict()

                for key, value in get_data_vars:
                    processed_request['get_data'][key] = value

            if processed_request['method'] == 'POST':
                data_vars = [data_var.split('=') for data_var in request_splitted[-1].split('&')]

                processed_request['post_data'] = dict()

                for key, value in data_vars:
                    processed_request['post_data'][key] = value

        print(f"[{processed_request}]")

        return processed_request

    def __send_response(self, client_socket : s.socket, processed_data : dict) -> None:
        try:
            with open(f"{self.app_path}/global{processed_data['path']}", 'rb') as b_reader:
                client_socket.sendfile(b_reader)
        except (FileNotFoundError, IsADirectoryError):
            if processed_data['path'] in self.urls:
                with open(f"{self.app_path}/global{self.urls[processed_data['path']]}", 'rb') as b_reader:
                    client_socket.sendfile(b_reader)
            else:
                with open(f"{self.app_path}/global{self.urls['/404']}", 'rb') as b_reader:
                    client_socket.sendfile(b_reader)

    def listen(self) -> None:
        self.__bind(self.addr)

        self.server.listen(self.queue)

        while self.server:
            try:
                client, client_addr = self.server.accept()
            except KeyboardInterrupt:
                print(f"Keyboard interrupt. Closing a server...")

                break
            else:
                print(f"[!] [{strft('%D, %T')}] : [{client_addr[0]}:{client_addr[1]}] : ", end='')

                client_data = client.recv(self.buffer_size)

                if not client_data:
                    pass
                else:
                    processed_request = self.__process_request(client_data)

                    if processed_request:
                        self.__send_response(client, processed_request)

                client.close()

        self.server.close()

def main(config = import_config('./config.json')) -> None:
    Server(
        app_path = config['server']['app_path'],
        ip = config['server']['ip'],
        port = config['server']['port'],
        queue = config['server']['queue'],
        buffer_size = config['server']['buffer_size'],
        urls = config['urls']
    ).listen()

if __name__ == '__main__':
    main()