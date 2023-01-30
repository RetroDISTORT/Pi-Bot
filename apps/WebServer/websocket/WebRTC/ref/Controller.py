#
# Usage:
#   Run program Controller.py
#   On a web browser connect to <IP/localhost>:8000
#
# Note:
#   The html file is loaded from the current folder "/mywebpage.html"
#

import http.server
import socketserver
import logging
import cgi

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = 'mywebpage.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        logging.error(self.headers)
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })
        for item in form.list:
            logging.error(item)
        http.server.SimpleHTTPRequestHandler.do_GET(self)

        with open("data.txt", "w") as file:
            for key in form.keys(): 
                file.write(str(form.getvalue(str(key))) + ",")
          
            
# Create an object of the above class
handler_object = MyHttpRequestHandler

PORT = 8000
my_server = socketserver.TCPServer(("", PORT), handler_object)

# Star the server
my_server.allow_reuse_address = True
my_server.serve_forever()
