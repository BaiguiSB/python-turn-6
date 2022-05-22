from apps.templates import create_app
from flask_socketio import SocketIO, join_room, leave_room

from itsdangerous import TimedJSONWebSignatureSerializer, BadTimeSignature, SignatureExpired
from flask import current_app

app, socketio = create_app()


@socketio.on('join')
def on_join(data):
    if "token" in data.keys():
        serializer = TimedJSONWebSignatureSerializer(
            current_app.config["SECRET_KEY"],
            expires_in=current_app.config["EXPIRATION"])
        try:
            data = serializer.loads(data["token"])
        except BadTimeSignature:
            return None
        data = dict(data)
        join_room(data['room'])


@socketio.on('leave')
def on_leave(data):
    if "token" in data.keys():
        serializer = TimedJSONWebSignatureSerializer(
            current_app.config["SECRET_KEY"],
            expires_in=current_app.config["EXPIRATION"])
        try:
            data = serializer.loads(data["token"])
        except BadTimeSignature:
            return None
        data = dict(data)
        leave_room(data['room'])


@socketio.on('message')
def message(data):
    if "token" in data.keys():
        serializer = TimedJSONWebSignatureSerializer(
            current_app.config["SECRET_KEY"],
            expires_in=current_app.config["EXPIRATION"])
        try:
            data2 = serializer.loads(data["token"])
        except BadTimeSignature:
            return None
        data2 = dict(data2)
        socketio.emit("message", {'name': data2["name"], "content": data["content"]}, to=data2["room"])


if __name__ == '__main__':
    socketio.run(app)
