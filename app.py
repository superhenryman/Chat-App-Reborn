import eventlet
eventlet.monkey_patch()
from flask import Flask, render_template, jsonify, redirect, request
from flask_socketio import SocketIO, emit
from argon2 import PasswordHasher
import logging
import os
import html
from database_stuff import *
from security import sign_client_id, verify_signature
def clean(text: str) -> str:
    """ Function to prevent XSS (screw you, dirty hacker.) """
    return str(html.escape(text, quote=True))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",)
ph = PasswordHasher()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("KEY")
socketio = SocketIO(app, async_mode='eventlet')

init_db()
init_banned_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/signup", methods=["POST"])
def signup():
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")
        create_user(username, password)
        return jsonify({
            "goto": "root",
            "code": render_template("index.html")
        })
    except Exception as e:
        logging.error(e)
        return jsonify({
            "goto": "nowhere",
            "error": e
        })

@app.route("/wheredoigo", methods=["POST"])
def username():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    serverchoice = data.get("serverChoice")
    
    if user_exists(username, password):
        # user exists
        print("user exists")
        if not user_is_banned(username):
            # if user isn't banned
            print("user not banned")
            return jsonify({
                "goto": "chatroom",
                "code": render_template("chatroom.html")
            })
        else:
            print("user banned")
            return "you're not cool"
    else:
        print("user doesn't exist")
        return jsonify({
            "goto": "signup",
            "code": render_template("signup.html"),
        })
if __name__ == '__main__':
    socketio.run(app, log_output=True, port=8080, host="0.0.0.0")
