from flask import Flask, session, render_template, request, send_from_directory
from uuid import uuid4
from os import path
from downloader import Downloader
app = Flask(__name__)
app.secret_key = '93)q.2M)k7#X02yt,nbz"eA6EfOw9s$N_e3kh4E'
downloader = Downloader()


@app.before_request
def before_request():
    if 'session_id' not in session:
        session['session_id'] = str(uuid4())


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
    app.run(debug=True)