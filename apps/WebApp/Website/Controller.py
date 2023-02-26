#
# Usage:
#   Run program Controller.py
#   On a web browser connect to <IP/localhost>:5000
#
# Note:
#   The html file is loaded from the current folder "/mywebpage.html"
#
import asyncio, websockets
from threading import Thread, Event, Lock
from flask import Flask, render_template, jsonify

# Server data
IP   = "10.0.0.14"#"localhost"
PORT = 8000

app = Flask(__name__)


@app.route('/', methods=['POST','GET'])
def home():
    return render_template('./index.html')

        
def main():
    app.run(host="0.0.0.0", port=PORT, debug=True)

if __name__ == '__main__':
    main()
    
 
