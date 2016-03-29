from flask import Flask, session
from uuid import uuid4
from downloader import Downloader
app = Flask(__name__)
app.secret_key = '93)q.2M)k7#X02yt,nbz"eA6EfOw9s$N_e3kh4E'
downloader = Downloader()

@app.before_request
def before_request():
    if 'session_id' not in session:
        session['session_id'] = uuid4()


@app.route('/', methods=['GET'])
def index():
    return 'Woop'

@app.route('/', methods=['POST'])
def index_post():
    downloader.add_download("")


if __name__ == '__main__':
    app.run(debug=True)