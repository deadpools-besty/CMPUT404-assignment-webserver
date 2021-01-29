#  coding: utf-8 
from genericpath import exists
import socketserver
import os
import http.server
from sys import path
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):

    def fetch_file(self, requested_file):
        fname = 'www' + requested_file
        try:
            f = open(fname, "r")
            lines = f.readlines()
            f.close()
            return lines
        except Exception as e:
            return str(e)
    
    def find_file_type(self, filename):
        return filename.split('.')[1]
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        
        print ("Got a request of: %s\n" % str(self.data, 'utf-8'))
        
        encoded_data = str(self.data, "utf-8")

        list_of_encoded = encoded_data.split('\r')
        
        # list of not allowed methods for producing 405 error
        na_method_list = ['POST', 'PUT', 'DELETE']
        
        # compare against the method list to see if method is allowed
        request_type = list_of_encoded[0].split()[0]
        requested_file = list_of_encoded[0].split()[1]
        
        # handle 405 error
        if request_type in na_method_list:
            self.request.sendall(bytearray('HTTP/1.1 405 Method not allowed\r\nConnection: close\r\n', "utf-8"))
        
        # check if dir exists
        elif os.path.exists('www' + requested_file):
            
            if '..' in requested_file:
                bytearray_to_send = f'''HTTP/1.1 404 Not found\r\nConnection: close\r\n'''
                self.request.sendall(bytearray(bytearray_to_send, 'utf-8'))
            
            # handle user inputting just a directory
            elif os.path.isdir('www' + requested_file):
                
                if requested_file[-1] == '/':
                
                    readout = self.fetch_file(requested_file + 'index.html')
                    
                    readout_string = ''
                    
                    for line in readout:
                        readout_string += line
                    bytearray_to_send = f'''HTTP/1.1 200 Ok\r\nContent-Type: text/html; charset=utf-8\r\nConnection: close\r\n\r\n{readout_string}'''
                    self.request.sendall(bytearray(bytearray_to_send,'utf-8'))
                else:
                    # handle 301 and redirect
                    bytearray_to_send = f'''HTTP/1.1 301 Permanently moved\r\nLocation: {requested_file + '/'}\r\nConnection: close\r\n\r\n'''
                    self.request.sendall(bytearray(bytearray_to_send,'utf-8'))
    
            # handle user inputting file
            elif os.path.isfile('www' + requested_file):
                readout = self.fetch_file(requested_file)
                

                # generate string to send 
                readout_string = ''
                for line in readout:
                    readout_string += line

                # send response
                file_ext = self.find_file_type(requested_file)
                bytearray_to_send = f'''HTTP/1.1 200 Ok\r\nContent-Type: text/{file_ext}; charset=utf-8\r\nConnection: close\r\n\r\n{readout_string}'''
                self.request.sendall(bytearray(bytearray_to_send,'utf-8'))
                    
        elif not os.path.exists('www' + requested_file):
            bytearray_to_send = f'''HTTP/1.1 404 Not found\r\nConnection: close\r\n'''
            self.request.sendall(bytearray(bytearray_to_send, 'utf-8'))
            
            
                    

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
