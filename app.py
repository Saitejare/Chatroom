from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_socketio import SocketIO, join_room, leave_room, emit
import MySQLdb.cursors
import bcrypt
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'saiteja5566'
app.config['MYSQL_DB'] = 'login'

mysql = MySQL(app)
socketio = SocketIO(app)

@app.route('/')
def home():
    if 'loggedin' in session:
        return redirect(url_for('chat'))
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM login_users WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['loggedin'] = True
            session['username'] = username
            return redirect(url_for('chat'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if 'loggedin' in session:
        return render_template('chat.html', username=session['username'])
    flash('Please log in to access the chat.', 'warning')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@socketio.on('join')
def handle_join(data):
    username = session.get('username')
    room = data['room']
    join_room(room)
    emit('message', {'msg': f"{username} has joined the room."}, room=room)

@socketio.on('leave')
def handle_leave(data):
    username = session.get('username')
    room = data['room']
    leave_room(room)
    emit('message', {'msg': f"{username} has left the room."}, room=room)

@socketio.on('send_message')
def handle_message(data):
    room = data['room']
    msg = data['msg']
    username = session.get('username')
    emit('message', {'msg': f"{username}: {msg}"}, room=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)
