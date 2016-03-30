from uuid import uuid4

from downloadmanager import DownloadManager
from eventlet import monkey_patch
from flask import Flask, session, render_template, request, send_from_directory
from flask_socketio import SocketIO
from os import path

monkey_patch()
app = Flask(__name__)
app.secret_key = '93)q.2M)k7#X02yt,nbz"eA6EfOw9s$N_e3kh4E'
socketio = SocketIO(app, async_mode='eventlet')
downloader = DownloadManager(socketio)


@app.before_request
def before_request():
    if 'session_id' not in session:
        session['session_id'] = str(uuid4())


@socketio.on('authentication')
def socket_authentication(uuid):
    downloader.register_socket(request.sid, uuid)


@socketio.on('disconnect')
def socket_disconnection():
    downloader.unregister_socket(request.sid)


@socketio.on_error_default
def default_error_handler(e):
    print(request.event["message"]) # "my error event"
    print(request.event["args"])    # (data,)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        downloader.add_download(session['session_id'], request.form['pl_link'])
    return render_template("index.html", list=downloader.get_downloads(session['session_id']))


@app.route('/download/<playlist_id>/<file>', methods=['GET'])
def download(playlist_id, file):
    curr_path = path.dirname(path.abspath(__file__))
    dl_path = curr_path + '/downloads/' + playlist_id + '/'
    return send_from_directory(dl_path, file)


if __name__ == '__main__':
    socketio.run(app)