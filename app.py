import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'adhya_pratham_private_key'
# SocketIO setup with CORS for local testing
socketio = SocketIO(app, cors_allowed_origins="*") # CORS allow karna zaroori hai

# Fixed Credentials as per your request
USERS = {
    "pratham": "Adsu", # Password change kar lena yahan
    "Adhya": "123"    # Password change kar lena yahan
}

# Track active connections
online_users = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('login')
def handle_login(data):
    username = data.get('username', '').lower()
    password = data.get('password', '')

    if username in USERS and USERS[username] == password:
        # User ko unke personal room mein join karwana
        join_room(username)
        online_users[username] = request.sid
        emit('login_success', {'username': username})
        print(f"[LOG] {username} logged in successfully.")
    else:
        emit('login_error', {'msg': 'Ghalat details bhai!'})

@socketio.on('call_user')
def handle_call(data):
    # data: { caller: "pratham", target: "adhya" }
    target = data.get('target')
    caller = data.get('caller')
    print(f"[CALL] {caller} is calling {target}")
    emit('incoming_call', {'from': caller}, room=target)

@socketio.on('signal')
def handle_webrtc_signaling(data):
    # Signaling data (offer, answer, candidates) target ko bhejna
    target = data.get('target')
    emit('signal', data, room=target)

@socketio.on('call_action')
def handle_call_actions(data):
    # Action: 'hold' or 'cut'
    target = data.get('target')
    action = data.get('action')
    status = data.get('status') # Hold true/false
    
    print(f"[ACTION] {action} signal sent to {target}")
    emit('call_action_received', data, room=target)

@socketio.on('disconnect')
def handle_disconnect():
    # User agar tab band kare to online_users se hatana
    for user, sid in list(online_users.items()):
        if sid == request.sid:
            print(f"[LOG] {user} disconnected.")
            del online_users[user]
            break

if __name__ == '__main__':
    # Render PORT variable provide karta hai, use pick karna zaroori hai
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)
