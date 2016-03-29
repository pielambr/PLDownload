import youtube_dl
from multiprocessing.pool import ThreadPool
from youtube_dl.utils import DownloadError
from datetime import datetime


class Download:
    link = ""
    done = False
    error = False
    started = None

    def __init__(self, link):
        self.link = link
        self.started = datetime.now()

    def download(self):
            try:
                youtube_dl._real_main(["--yes-playlist", "-R", "10", "-x", "--audio-format", "mp3", "-v", self.link])
            except DownloadError:
                self.error = True
            finally:
                self.done = True

    def start(self):
            pool = ThreadPool()
            pool.apply_async(self.download)
