from download import Download
from multiprocessing import Process, Lock


class DownloadManager:

    downloads = {}
    sockets = {}

    def __init__(self, socketio):
        self.socketio = socketio

    def __call__(self, uuid, message):
        for socket in self.sockets:
            if self.sockets[socket] == uuid:
                try:
                    process = Process(target=self.socketio.emit, args=('update', message.json(),),
                                      kwargs={'room': str(socket)})
                    process.start()
                except Exception as e:
                    print(e)

    def add_download(self, session, link):
        download = Download(session, link, self)
        if session not in self.downloads:
            self.downloads[session] = []
        self.downloads[session].append(download)
        download.download()

    def get_downloads(self, session):
        try:
            return self.downloads[session]
        except KeyError:
            return None

    def register_socket(self, socket_id, session_id):
        self.sockets[socket_id] = session_id

    def unregister_socket(self, socket_id):
        if socket_id in self.sockets:
            del self.sockets[socket_id]

