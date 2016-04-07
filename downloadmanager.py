from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from threading import RLock

from download import Download


class DownloadManager:

    socket_lock = RLock()
    download_lock = RLock()

    downloads = {}
    sockets = {}

    def __init__(self, socketio):
        self.socketio = socketio

    def __call__(self, session_id, message):
        sockets_copy = deepcopy(self.sockets)
        for socket in sockets_copy:
            if self.sockets[socket] == session_id:
                try:
                    self.socketio.emit(message.type, message.json(), room=str(socket))
                except Exception as e:
                    print(e)

    def add_download(self, session_id, link):
        with self.download_lock:
            download = Download(session_id, link, self)
            if session_id not in self.downloads:
                self.downloads[session_id] = []
            self.downloads[session_id].append(download)
            executor = ThreadPoolExecutor(max_workers=2)
            executor.submit(download.start)

    def get_downloads(self, session):
        with self.download_lock:
            try:
                return reversed(self.downloads[session])
            except KeyError:
                return None

    def zip_download(self, session_id, playlist_id):
        if session_id not in self.downloads:
            raise LookupError("No downloads found for this session")
        download = next((dl for dl in self.downloads[session_id] if dl.playlist_id == playlist_id), None)
        if download is None:
            raise LookupError("This playlist was not found for your session")
        elif download.zipping:
            return None
        elif not download.zipping and not download.zipped:
            executor = ThreadPoolExecutor(max_workers=2)
            executor.submit(download.zip)
            return None
        elif download.zipped:
            return download.file_path

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

