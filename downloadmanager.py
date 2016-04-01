from concurrent.futures import ThreadPoolExecutor
from threading import RLock
from copy import deepcopy

from download import Download


class DownloadManager:

    socket_lock = RLock()
    download_lock = RLock()

    downloads = {}
    sockets = {}

    def __init__(self, socketio):
        self.socketio = socketio

    def __call__(self, uuid, message):
        sockets_copy = deepcopy(self.sockets)
        for socket in sockets_copy:
            if self.sockets[socket] == uuid:
                try:
                    self.socketio.emit('update', message.json(), room=str(socket))
                except Exception as e:
                    print(e)

    def add_download(self, session, link):
        with self.download_lock:
            download = Download(session, link, self)
            if session not in self.downloads:
                self.downloads[session] = []
            self.downloads[session].append(download)
            exec = ThreadPoolExecutor(max_workers=4)
            exec.submit(download.start)

    def get_downloads(self, session):
        with self.download_lock:
            try:
                return reversed(self.downloads[session])
            except KeyError:
                return None

    def cleanup(self):
        with self.download_lock:
            for session in self.downloads:
                self.downloads[session][:] = [d for d in self.downloads[session] if not d.remove()]
            self.downloads = {s: d for s, d in self.downloads.items() if len(d) > 0}

    def register_socket(self, socket_id, session_id):
        with self.socket_lock:
            self.sockets[socket_id] = session_id

    def unregister_socket(self, socket_id):
        with self.socket_lock:
            if socket_id in self.sockets:
                del self.sockets[socket_id]

