from download import Download
from threading import Lock


class DownloadManager:

    mutex = Lock()
    downloads = {}
    sockets = {}

    def __init__(self, socketio):
        self.socketio = socketio

    def __call__(self, uuid, message):
        self.socketio.emit('update', message.json())
        for socket in self.sockets:
            if self.sockets[socket] == uuid:
                self.socketio.emit('update', message.json(), room=socket)

    def add_download(self, session, link):
        download = Download(session, link, self)
        if session not in self.downloads:
            self.downloads[session] = []
        self.downloads[session].append(download)
        download.start()

    def get_downloads(self, session):
        try:
            return self.downloads[session]
        except KeyError:
            return None

    def register_socket(self, socket_id, session_id):
        self.sockets[socket_id] = session_id

    def unregister_socket(self, socket_id):
        self.mutex.acquire()
        if socket_id in self.sockets:
            del self.sockets[socket_id]
        self.mutex.release()

