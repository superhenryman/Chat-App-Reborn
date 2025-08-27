import eventlet
eventlet.monkey_patch()
from flask import Flask, render_template, jsonify, redirect, request, url_for
from flask_socketio import SocketIO, emit, join_room
from argon2 import PasswordHasher
import logging
import os
import html
from database_stuff import init_banned_db, init_db, create_user, user_exists, user_is_banned
import random
import string
def clean(text: str) -> str:
    """ Function to prevent XSS (screw you, dirty hacker.) """
    return str(html.escape(text, quote=True))

def random_key():
    key = ""
    for i in range(8):
        key += random.choice(string.printable)
    return key

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",)
ph = PasswordHasher()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("KEY") or random_key()
socketio = SocketIO(app, async_mode='eventlet')

init_db()
init_banned_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/error")
def error(): return render_template("error.html")

@app.route("/chatroom/<server_choice>/<username>")
def chatroom(server_choice, username):
    return render_template("chatroom.html", serverchoice=server_choice, username=username)

@app.route("/signup.html")
def signup_template():
    return render_template("signup.html")

@app.route("/signup", methods=["POST"])
def signup():
    try:
        username = request.form.get("username")
        password = request.form.get("password")
        create_user(username, password)
        return redirect("/")
    except Exception as e:
        logging.error(e)
        return redirect("/error")
    
@app.route("/wheredoigo", methods=["POST"])
def wheretogore():
    serverchoice = request.form.get("serverchoice")
    username = request.form.get("username")
    password = request.form.get("password")
    if user_exists(username, password):
        if not user_is_banned(username):
            return redirect(url_for("chatroom", server_choice=serverchoice, username=username))
        else:
            return "you're not cool"
    else:
        return redirect("/signup.html")
    
# socketio functions

@socketio.on("join")
def handle_join(data):
    serverChoice = data["serverchoice"]
    username = clean(data["username"] or "Guest")
    join_room(serverChoice)
    emit("message", 
         {"serverchoice": serverChoice, 
        "message": f"{username} joined server {serverChoice}!", 
        "color": "yellow"},
        room=serverChoice)

@socketio.on("message")
def handle_message(data):
    serverChoice = data["serverchoice"]
    user_temp = clean(data["username"])
    username = f"<{user_temp}>" 
    message = clean(data["message"])
    emit("message", {
        "serverChoice": serverChoice,
        "message": f"{username} {message}",
        "color": "white"
    }, room=serverChoice)

if __name__ == '__main__':
    socketio.run(app, log_output=True, port=8080, host="0.0.0.0")
