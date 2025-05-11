from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Pluto bot is live", 200

@app.route('/ping')
def ping():
    return "pong", 200


def keep_alive():
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()
