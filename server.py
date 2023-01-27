#  coding: utf-8 
import socketserver
import os
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

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        # print ("Got a request of: %s\n" % self.data)

        # split the received data from socket
        # self.data = self.data.decode().splitlines()
        request_type, path, protocol = self.data.decode("utf-8").split("\r\n")[0].split(" ")

        # # extract information: request_type, path
        # request_type = self.data[0].split()[0]  # GET
        # path = self.data[0].split()[1] 
        # protocol = self.data[0].split()[2]
        # ==========================================================================
        # USER STORY: As a webserver admin I want ONLY files in ""./www" and deeper to be served
        expected_path = './www' + path
        # requested_path = os.path.abspath(path)
        
        file_type = "" 
        if (".html" in path):  
            file_type = "text/html"
        elif (".css" in path):
            file_type = "text/css"
        # ==========================================================================
        # USER STORY: As a webserver admin I want to serve HTML and CSS files from ./www
        # determine the file type first to process the request separetely
        # https://www.geeksforgeeks.org/python-os-path-commonprefix-method/
        
        file_relative_path = self.get_file_relative_path(path, expected_path)

        if (file_relative_path is None):
            response = self.wrong_path()
            self.request.sendall(bytearray(response,'utf-8'))
            return

        if ((request_type in ["POST","PUT","DELETE"]) or (request_type != "GET")):
            # 405 Method Not Allowed” for any method you cannot handle (POST/PUT/DELETE)
            response = self.wrong_request()
            self.request.sendall(bytearray(response,'utf-8'))
            return

        elif (file_type == ""):
            # directory
            
            if file_relative_path.endswith('/'):
                print("this for 301 with /")
                response = self.get_content_dir(file_relative_path)
                self.request.sendall(bytearray(response, "utf-8"))
                
            else:    
                # 301 moved
                print("this is test for without / endwith")
                print("file for the file_relative_path %s", file_relative_path)
                # ./wwww/deep  -> /deep 
                response = self.moved_path(path) 
                self.request.sendall(bytearray(response, "utf-8"))   
                return         

        # elif (os.path.commonprefix([expected_path,file_relative_path]) != expected_path):
        
        elif (file_type in ["text/html","text/css"]):
            # 404 errors for paths not found
            # check if file exist 
            print("xxxxxxx: the file_re_path %s", file_relative_path)
            
            if ((os.path.exists(file_relative_path)) and (not self.directory_checker(file_relative_path))):
                # 200
                response = self.get_content(file_relative_path,file_type)
                self.request.sendall(bytearray(response,'utf-8'))
            else:
                # 404
                response = self.wrong_path()
                self.request.sendall(bytearray(response,'utf-8'))
                return
        else:
            # 200
            response = self.get_content(file_relative_path,file_type)
            self.request.sendall(bytearray(response, "utf-8"))
                
            # try:
            #     # it will detect if the file path is inside this directory
            #     # if not, will be IsADirectoryError and status code will be 301
            #     # if is, will read file accoding to the file type and status code is 200

            #     response = self.get_content(file_relative_path,file_type)

            # except IsADirectoryError:
            #     # do we need to test if file_relative_path.endwith("/")
            #     # Must use 301 to correct paths such as http://127.0.0.1:8080/deep 
            #     # to http://127.0.0.1:8080/deep/  ./www/deep  /deep.css

            #     response = self.moved_path(str(file_relative_path) +"/")
            #     self.request.sendall(bytearray(response, "utf-8"))

            # # everything correct 
            # self.request.sendall(bytearray(response,'utf-8'))

    def directory_checker(self, file_relative_path):
        """
        Check for backward directory access, ie /../../.. etc
        """
        dirs = file_relative_path.split("/")
        return (".." in dirs)

    def get_content_dir(self,file_relative_path):
        file_relative_path += "/index.html"
        f = open(file_relative_path, 'r')
        content = f.read()
        # header
        header = "HTTP/1.1 200 OK\r\n" + "Content-Type: " + "text/html" + "\r\n" + "Content-Length: " + str(len(content)) + "\r\n" + \
        "Connection: Closed\r\n" + content
        f.close()
        return header


    def moved_path(self,file_relative_path):
        # file_relative_path += "/index.html"
        status_code = 301
        response_301 = self.send_response(status_code,file_relative_path)
        print("this is for test 301 response %s", response_301)
        return response_301

        
    def wrong_request(self):
        status_code = 405
        content = ""
        response_405 = self.send_response(status_code,content)
        return response_405


    def wrong_path(self):
        # handle the invalid path and provide response 404
        status_code = 404
        content = ""
        response_404 = self.send_response(status_code, content)
        return response_404

    def send_response( self, status,path):
        # provide the header according to different status code
        if status == 404:
            response = "HTTP/1.1 %i Method Not Found\r\n" % status
        elif status == 405:
            response = "HTTP/1.1 %i Method Not Allowed\r\n" %status
        elif status == 301:
            response = "HTTP/1.1 %i Moved Permanently\r\n" %status
            response += "Location: http://localhost:8080%s/ \r\n" %path  
        return response
           
    def get_content(self, expected_path,file_type):

        f = open(expected_path, 'r')
        content = f.read()
        # header
        header = "HTTP/1.1 200 OK\r\n" + "Content-Type: " + file_type + "\r\n" + "Content-Length: " + str(len(content)) + "\r\n" + \
        "Connection: Closed\r\n" + content
        f.close()
        return header
        
        
    def get_file_relative_path(self, path, expected_path):
        # for if and elif -> check if path is with dir ./www
        path = "./www" +path
        if os.path.isfile(expected_path):
            print("xxxx: find the file")
            return path
        elif os.path.isdir(expected_path):
            # return os.path.join(path, "index.html")
            return path
        else:
            response = self.wrong_path()
            self.request.sendall(bytearray(response,'utf-8'))
            return



        
if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
