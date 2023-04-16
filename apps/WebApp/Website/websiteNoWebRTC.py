# Web streaming example
# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming
#
# Usage:
#  Run code by running python3 Remote.py
#  Open on a web browser {ipAddress}:8000

##############
import pyaudio
##############
import os
import io
import picamera
import logging
import argparse         # Requried for argument parsing
import socketserver
import configparser     # Required for ini files

from threading import Condition
from http      import server

RES    = ['160x120', '320x240', '640x480', '1280x960']

PAGE   = open("/opt/boobot/apps/WebApp/Website/templates/indexNoWebRTC.html", "r").read()
CSS    = open("/opt/boobot/apps/WebApp/Website/static/css/style.css", "r").read()
CTRLJS = open("/opt/boobot/apps/WebApp/Website/static/scripts/controller.js", "r").read()
WSJS   = open("/opt/boobot/apps/WebApp/Website/static/scripts/websocket.js", "r").read()

IMGBS  = open("/opt/boobot/apps/WebApp/Website/static/images/joystick_base.png", "rb").read()
IMGJS  = open("/opt/boobot/apps/WebApp/Website/static/images/joystick_black.png", "rb").read()
IMGSL  = open("/opt/boobot/apps/WebApp/Website/static/images/slider.png", "rb").read()


def getIP(IP):
    return IP if IP != "" else os.popen("hostname -I").read().split()[0]


def connectionInfo(config):
    section = 'WebsiteLocal' if config['Settings'].getboolean('local settings') else 'WebsiteRemote'
    ip      = getIP(config[section]['ip'])
    portW   = config[section]['Port']
    portWS  = config[section]['websocketport']
    portS   = config['Socket']['Port']
    cert    = config['WebsiteCertificate']['certificate']
    key     = config['WebsiteCertificate']['key']

    return section, ip, portW, portWS, portS, cert, key


def serverInfo(ip, portws):
    content = ("\nlet serverIP      = \"" + ip     + "\";" +
               "\nlet websocketPort = "   + portws + ";"   +
               "\n"
               )
    return content


def clientConfigJS():
    section, ip, portW, portWS, portS, cert, key = connectionInfo(configuration)
    ip         = getIP(ip)
    info = serverInfo(ip, portWS)
    
    return info + WSJS


class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.emptyBuffer = io.BytesIO()
        self.condition = Condition()

    #This method is called from inside camera.start_recording
    def write(self, buf): 
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = buf  #No Buffer
                self.buffer.flush()
                
                #self.frame = self.buffer.getvalue()

                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

    
class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
            
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
            
        elif self.path == '/static/css/style.css':
            content = CSS.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/css')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)

        elif self.path == '/static/images/joystick_black.png':
            content = IMGJS#.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)

        elif self.path == '/static/images/joystick_base.png':
            content = IMGBS#.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)

        elif self.path == '/static/images/slider.png':
            content = IMGSL#.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)

        elif self.path == '/static/scripts/controller.js':
            content = CTRLJS.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/javascript')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)

        elif self.path == '/static/scripts/websocket.js':
            content = clientConfigJS().encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/javascript')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

            
class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads      = True

    
if __name__ == "__main__":
    global config
    print("Hello")
    parser = argparse.ArgumentParser(description="Pibot WebApp")
    parser.add_argument("--config-file", default="/opt/boobot/apps/WebApp/configuration/app.config", help="File with configuration")
    args          = parser.parse_args()
    configuration = configparser.ConfigParser()
    configuration.read(args.config_file)
    section, ip, portW, portWS, portS, cert, key = connectionInfo(configuration)

    print(ip)
    with picamera.PiCamera(resolution=RES[0], framerate=30) as camera:
        output = StreamingOutput()
        camera.start_recording(output, format='mjpeg')
        try:
            address = (getIP(ip), int(portW))
            server  = StreamingServer(address, StreamingHandler)
            server.serve_forever()
        finally:
            camera.stop_recording()
    
